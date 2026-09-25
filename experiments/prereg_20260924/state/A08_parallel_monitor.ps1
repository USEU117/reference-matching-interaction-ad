# Resource / progress sampler for the sharded A08 stride-1 sweep.
#
# Writes state\A08_parallel_progress.json every -IntervalSec seconds and exits by
# itself after -MaxMinutes (0 = never) or when every shard has exited.
# READ-ONLY: it never writes anything except the progress file.
#
# Pure ASCII on purpose: Windows PowerShell 5.1 decodes a BOM-less .ps1 as GBK.
#
# Usage:
#   powershell -ExecutionPolicy Bypass -File experiments\prereg_20260924\state\A08_parallel_monitor.ps1
#   ... -IntervalSec 60 -MaxMinutes 1440

param(
    [int]$IntervalSec = 60,
    [int]$MaxMinutes = 1440,
    [string]$Root = 'D:\STUDY\My_github\sci_project',
    [string]$WorkersFile = 'experiments\prereg_20260924\state\A08_parallel_workers.json',
    [string]$ProgressFile = 'experiments\prereg_20260924\state\A08_parallel_progress.json',
    [switch]$Once
)

$ErrorActionPreference = 'Continue'
$base = Join-Path $Root 'experiments\prereg_20260924'
$workersPath = Join-Path $Root $WorkersFile
$progressPath = Join-Path $Root $ProgressFile

function Read-Workers {
    return (Get-Content -LiteralPath $workersPath -Raw | ConvertFrom-Json)
}

function Get-SnapshotTables {
    # one CIM pass + one Get-Process pass, reused for every worker tree
    $parent = @{}
    foreach ($row in Get-CimInstance Win32_Process -ErrorAction SilentlyContinue) {
        $parent[[int]$row.ProcessId] = [int]$row.ParentProcessId
    }
    $children = @{}
    foreach ($kv in $parent.GetEnumerator()) {
        $pp = $kv.Value
        if (-not $children.ContainsKey($pp)) { $children[$pp] = New-Object System.Collections.ArrayList }
        [void]$children[$pp].Add($kv.Key)
    }
    $procTable = @{}
    foreach ($p in Get-Process -ErrorAction SilentlyContinue) { $procTable[$p.Id] = $p }
    return @{ parent = $parent; children = $children; procs = $procTable }
}

function Get-TreeWorkingSetMiB([int]$rootPid, $tables) {
    # the venv python.exe is a launcher that re-execs the real interpreter, so
    # sum the working set of the process tree, not just the launcher
    $stack = New-Object System.Collections.Stack
    $stack.Push($rootPid)
    $seen = @{}
    $total = 0.0
    while ($stack.Count -gt 0) {
        $cur = $stack.Pop()
        if ($seen.ContainsKey($cur)) { continue }
        $seen[$cur] = $true
        if ($tables.procs.ContainsKey($cur)) { $total += $tables.procs[$cur].WorkingSet64 / 1MB }
        if ($tables.children.ContainsKey($cur)) { foreach ($c in $tables.children[$cur]) { $stack.Push($c) } }
    }
    return [math]::Round($total, 1)
}

function Write-Sample {
    $workers = Read-Workers
    $outAbs = $workers.output
    $unitsDir = Join-Path $outAbs 'units'
    $estMap = @{}
    if ($workers.est_per_unit) {
        foreach ($p in $workers.est_per_unit.PSObject.Properties) { $estMap[$p.Name] = [double]$p.Value }
    }
    $plan = @($workers.plan)
    $planTotal = $plan.Count
    $started = [datetime]::Parse($workers.launched_local)
    if ($started.Kind -eq 'Unspecified') { $started = [datetime]::SpecifyKind($started, 'Local') }
    $totalCategoryInstances = 0
    foreach ($u in $plan) {
        if ($u -like 'mpdd*') { $totalCategoryInstances += 6 } else { $totalCategoryInstances += 3 }
    }

    # checkpoint-derived ground truth
    $doneUnits = @()
    $catInstances = 0
    if (Test-Path -LiteralPath $unitsDir) {
        foreach ($f in Get-ChildItem -LiteralPath $unitsDir -Filter '*.json' -ErrorAction SilentlyContinue) {
            try { $j = Get-Content -LiteralPath $f.FullName -Raw | ConvertFrom-Json } catch { continue }
            if ($j.complete) { $doneUnits += $f.BaseName }
            if ($j.categories_done) { $catInstances += @($j.categories_done).Count }
        }
    }

    $elapsed = ((Get-Date) - $started).TotalSeconds
    $doneWork = 0.0; $totalWork = 0.0
    foreach ($u in $plan) {
        $e = if ($estMap.ContainsKey($u)) { $estMap[$u] } else { 0.0 }
        $totalWork += $e
        if ($doneUnits -contains $u) { $doneWork += $e }
    }
    $rate = if ($elapsed -gt 0) { $doneWork / $elapsed } else { 0.0 }

    # ETA: a *global* rate that only counts completed units understates the pace
    # while every shard is still inside its first unit.  So the pace is measured
    # per shard (its own completed work over its own elapsed time) and scaled by
    # the number of shards that are up; each shard also projects its own finish,
    # which is what accounts for the staggered starts.  The latest projection wins.
    $paces = @()
    $etaCandidates = @()

    $os = Get-CimInstance Win32_OperatingSystem
    $tables = Get-SnapshotTables
    $shardRows = @()
    $anyAlive = $false
    foreach ($s in $workers.worker_entries) {
        $alive = $false
        if ($s.pid -and [int]$s.pid -gt 0) {
            $alive = $null -ne (Get-Process -Id $s.pid -ErrorAction SilentlyContinue)
        }
        if ($alive) { $anyAlive = $true }
        $ws = if ($alive) { Get-TreeWorkingSetMiB $s.pid $tables } else { 0 }
        $done = 0; $last = ''
        if (Test-Path -LiteralPath $s.stdout) {
            $lines = @(Get-Content -LiteralPath $s.stdout -ErrorAction SilentlyContinue)
            $done = @($lines | Where-Object { $_ -match 'methods \(\d+s\)$' }).Count
            if ($lines.Count) { $last = [string]$lines[-1] }
        }
        $shardRows += [ordered]@{
            id             = $s.id
            pid            = $s.pid
            alive          = $alive
            ws_mib         = $ws
            units_done     = $done
            units_total    = $s.units_total
            units_assigned = @($s.units)
            est_seconds    = $s.est_seconds
            last_line      = $last
            stdout         = $s.stdout
        }

        $shardDoneWork = 0.0
        foreach ($u in @($s.units)) { if ($doneUnits -contains $u) { $shardDoneWork += [double]$estMap[$u] } }
        if ($shardDoneWork -gt 0 -and $s.start_local) {
            $shardStart = [datetime]::Parse($s.start_local)
            if ($shardStart.Kind -eq 'Unspecified') { $shardStart = [datetime]::SpecifyKind($shardStart, 'Local') }
            $shardElapsed = ((Get-Date) - $shardStart).TotalSeconds
            if ($shardElapsed -gt 0) {
                $pace = $shardDoneWork / $shardElapsed
                $paces += $pace
                $etaCandidates += (([double]$s.est_seconds) - $shardDoneWork) / $pace
            }
        }
    }
    $launchedCount = @($workers.worker_entries | Where-Object { [int]$_.pid -gt 0 }).Count
    if ($paces.Count -gt 0) {
        $meanPace = ($paces | Measure-Object -Average).Average
        $aggregatePace = $meanPace * [math]::Max($launchedCount, 1)
        if ($aggregatePace -gt 0) { $etaCandidates += ($totalWork - $doneWork) / $aggregatePace }
    }
    $etaS = if ($etaCandidates.Count) { ($etaCandidates | Measure-Object -Maximum).Maximum } else { $null }

    $finalProducts = @()
    foreach ($p in 'replicate_stride1.npz', 'point_stride1.csv', 'E1_STATUS_stride1.json') {
        if (Test-Path -LiteralPath (Join-Path $outAbs $p)) { $finalProducts += $p }
    }
    $wsSum = 0.0
    foreach ($r in $shardRows) { $wsSum += [double]$r['ws_mib'] }

    $progress = [ordered]@{
        now_local                = (Get-Date).ToString('s')
        elapsed_seconds          = [math]::Round($elapsed, 0)
        shards                   = $workers.shards
        any_shard_alive          = $anyAlive
        units_done               = $doneUnits.Count
        units_total              = $planTotal
        category_instances_done  = $catInstances
        category_instances_total = $totalCategoryInstances
        done_estimated_seconds   = [math]::Round($doneWork, 0)
        total_estimated_seconds  = [math]::Round($totalWork, 0)
        effective_rate           = [math]::Round($rate, 4)
        eta_seconds              = if ($etaS) { [math]::Round($etaS, 0) } else { $null }
        eta_hours                = if ($etaS) { [math]::Round($etaS / 3600, 2) } else { $null }
        eta_local                = if ($etaS) { (Get-Date).AddSeconds($etaS).ToString('s') } else { $null }
        total_ram_mib            = [math]::Round($os.TotalVisibleMemorySize / 1024, 1)
        avail_ram_mib            = [math]::Round($os.FreePhysicalMemory / 1024, 1)
        sum_worker_ws_mib        = [math]::Round($wsSum, 1)
        final_products_present   = $finalProducts
        per_shard                = $shardRows
    }
    $progress | ConvertTo-Json -Depth 8 | Set-Content -LiteralPath $progressPath -Encoding UTF8
    $launched = @($workers.worker_entries | Where-Object { [int]$_.pid -gt 0 }).Count
    $entries = @($workers.worker_entries).Count
    Write-Host ("[{0}] units {1}/{2}  cat {3}/{4}  rate={5} work/s  eta_h={6}  avail={7}MiB  ws={8}MiB  alive={9}" -f `
        (Get-Date).ToString('HH:mm:ss'), $doneUnits.Count, $planTotal, $catInstances,
        $totalCategoryInstances, $progress.effective_rate, $progress.eta_hours,
        $progress.avail_ram_mib, $progress.sum_worker_ws_mib, "$launched/$entries up, running=$anyAlive")
    if ($anyAlive) { return 'alive' }
    if ($launched -lt $entries) { return 'starting' }
    return 'done'
}

$state = Write-Sample
if ($Once) { exit 0 }
$deadline = if ($MaxMinutes -gt 0) { (Get-Date).AddMinutes($MaxMinutes) } else { [datetime]::MaxValue }
while ((Get-Date) -lt $deadline) {
    Start-Sleep -Seconds $IntervalSec
    $state = Write-Sample
    if ($state -eq 'done') { Write-Host 'all shards have exited'; break }
}
