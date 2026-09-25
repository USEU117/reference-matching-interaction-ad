# A11 execution queue (2026-09-25) - append-only companion of run_queue.ps1
#
# Scope: the pre-registered A11 item of docs/PREREGISTRATION_20260924_CN.md section 2.2,
#       implemented by scripts/prereg_20260924/a11_shared_op_ablation_multi.py.
#
# A11 re-uses the frozen canonical feature caches and the frozen patch_scores.npz maps,
# so the whole item is CPU-only: no CUDA context is created and the GPU is not touched.
# It is nevertheless launched with the same accounting as run_queue.ps1 so that the
# record shows whether any other GPU work could have been disturbed.
#
# The two shards below are disjoint halves of the registered plan (MPDD development and
# BTAD holdout).  Each shard checkpoints every unit, so a shard can be restarted with
# --resume without recomputing anything; the products are assembled once, by one
# closing call without --shard.
#
# Pure ASCII on purpose: Windows PowerShell 5.1 decodes a BOM-less .ps1 as GBK.

$ErrorActionPreference = 'Continue'

$root     = 'D:\STUDY\My_github\sci_project'
$base     = Join-Path $root 'experiments\prereg_20260924'
$logs     = Join-Path $base 'logs'
$out      = Join-Path $base 'out\A11'
$state    = Join-Path $base 'state'
$py       = Join-Path $root '.venv-anomalyclip\Scripts\python.exe'
$script   = Join-Path $root 'scripts\prereg_20260924\a11_shared_op_ablation_multi.py'
$progress = Join-Path $state 'progress.txt'

$gpuTotalMiB       = 6144
$requiredFreeMiB   = 1200
$sampleSeconds     = 15
$minFreeRamGiB     = 3.5

New-Item -ItemType Directory -Force -Path $logs, $out, $state | Out-Null

function Log([string]$msg) {
    $line = "{0} {1}" -f (Get-Date -Format 'yyyy-MM-dd HH:mm:ss'), $msg
    Add-Content -LiteralPath (Join-Path $logs 'queue_a11.log') -Value $line -Encoding utf8
    Write-Host $line
}

function Progress([string]$item, [string]$result) {
    $line = "{0}`t{1}`t{2}" -f (Get-Date -Format 'yyyy-MM-dd HH:mm:ss'), $item, $result
    Add-Content -LiteralPath $progress -Value $line -Encoding utf8
}

function Get-UsedMiB {
    try {
        $v = & nvidia-smi --query-gpu=memory.used --format=csv,noheader,nounits 2>$null |
             Select-Object -First 1
        if ($null -eq $v) { return $null }
        return [int]($v.ToString().Trim())
    } catch { return $null }
}

function Write-Json([string]$path, $payload, [int]$depth) {
    $json = $payload | ConvertTo-Json -Depth $depth
    Set-Content -LiteralPath $path -Value $json -Encoding utf8
}

# ---------------------------------------------------------------- pre-flight
$os = Get-CimInstance Win32_OperatingSystem
$freeGiB = [math]::Round($os.FreePhysicalMemory / 1MB, 2)
Log ("pre-flight: free RAM {0} GiB, GPU used {1} MiB" -f $freeGiB, (Get-UsedMiB))
if ($freeGiB -lt $minFreeRamGiB) {
    Log ("A11 ABORTED - free RAM {0} GiB < {1} GiB" -f $freeGiB, $minFreeRamGiB)
    Progress 'A11' 'ABORTED (pre-flight: insufficient free RAM)'
    exit 1
}

# ---------------------------------------------------------------- launch shards
$shards = @(
    [ordered]@{ id = 'A11_mpdd'; args = @('--datasets','mpdd') },
    [ordered]@{ id = 'A11_btad'; args = @('--datasets','btad') }
)
$common = @('-u', $script, '--mode', 'run', '--output', $out,
            '--seeds', '0', '1', '--shots', '1', '2', '4', '8', '--resume')

$procs = @()
foreach ($shard in $shards) {
    $id        = $shard.id
    $stdout    = Join-Path $logs ("{0}.out" -f $id)
    $stderr    = Join-Path $logs ("{0}.err" -f $id)
    $cmd       = @('--mode','run') + $shard.args + @('--output', $out,
                   '--seeds','0','1','--shots','1','2','4','8','--resume')
    $argList   = @('-u', $script) + $cmd
    $start     = Get-Date
    $env:OMP_NUM_THREADS = '6'
    $p = Start-Process -FilePath $py -ArgumentList $argList -NoNewWindow -PassThru `
                       -RedirectStandardOutput $stdout -RedirectStandardError $stderr
    Log ("{0} START pid={1} args={2}" -f $id, $p.Id, ($cmd -join ' '))
    Progress $id ("START pid={0}" -f $p.Id)
    $procs += [ordered]@{ id = $id; proc = $p; start = $start; stdout = $stdout
                          ; stderr = $stderr; cmd = ('"{0}" {1}' -f $py, ($cmd -join ' '))
                          ; peak = 0; peakVram = 0 }
}

# ---------------------------------------------------------------- monitor
#
# Peak memory is tracked on the REAL interpreters, not on the `Start-Process` handle:
# on this host that handle reports a 4 MiB stub, so the first version of this monitor
# recorded a meaningless peak.  The interpreters are picked up by name and a working set
# floor, which is the same object the RAM stop rule is meant to guard.
#
# Stop rule: THREE consecutive samples at or above $ramStopPercent, so a single transient
# spike cannot terminate a multi-hour step (it did once, at 95.4% for one sample, before
# this was tightened).  A terminated shard is restartable with --resume and loses at most
# the unit it was in.
$ramStopPercent = 96
$ramBreaches    = 0
$peakWorkSetMiB = 0
$ramKilled      = $false
$vramBase = Get-UsedMiB
while (@($procs | Where-Object { -not $_.proc.HasExited }).Count -gt 0) {
    Start-Sleep -Seconds $sampleSeconds
    $used = Get-UsedMiB
    $osNow = Get-CimInstance Win32_OperatingSystem
    $sysPct = [math]::Round(100.0 * ($osNow.TotalVisibleMemorySize - $osNow.FreePhysicalMemory) / $osNow.TotalVisibleMemorySize, 1)
    $live = @(Get-Process python -ErrorAction SilentlyContinue |
              Where-Object { $_.WorkingSet64 -gt 100MB })
    foreach ($entry in $procs) {
        if ($entry.proc.HasExited) { continue }
        if ($null -ne $used -and $used -gt $entry.peakVram) { $entry.peakVram = $used }
    }
    $wsTotal = 0
    foreach ($p in $live) {
        $wsMiB = [int]($p.WorkingSet64 / 1MB)
        $peakMiB = [int]($p.PeakWorkingSet64 / 1MB)
        $wsTotal += $peakMiB
        if ($peakMiB -gt $peakWorkSetMiB) { $peakWorkSetMiB = $peakMiB }
    }
    Log ("A11 monitor: system_used={0}% gpu_used={1}MiB live_interpreters={2} sum_peak_ws={3}MiB worst_peak_ws={4}MiB" -f `
         $sysPct, $used, $live.Count, $wsTotal, $peakWorkSetMiB)
    if ($sysPct -ge $ramStopPercent) { $ramBreaches++ } else { $ramBreaches = 0 }
    if ($ramBreaches -ge 3) {
        Log ("A11 STOP RULE: system memory >= {0}% on {1} consecutive samples - terminating both shards" -f $ramStopPercent, $ramBreaches)
        foreach ($entry in $procs) { if (-not $entry.proc.HasExited) { $entry.proc.Kill() } }
        $ramKilled = $true
        break
    }
}

foreach ($entry in $procs) {
    try { $entry.proc.WaitForExit() } catch { }
    $code = $null
    try { $entry.proc.Refresh(); $code = $entry.proc.ExitCode } catch { $code = $null }
    $secs = [int]((Get-Date) - $entry.start).TotalSeconds
    $entry['exit'] = $code
    $entry['seconds'] = $secs
    Log ("{0} END exit={1} {2}s peak_device={3}MiB" -f $entry.id,
         $(if ($null -eq $code) { 'unknown' } else { $code }), $secs, $entry.peakVram)
    Progress $entry.id ("success={0} duration={1}s" -f `
        ($null -eq $code -or $code -eq 0), $secs)
}

# ---------------------------------------------------------------- assemble
$assembleOut = Join-Path $logs 'A11_assemble.out'
$assembleErr = Join-Path $logs 'A11_assemble.err'
$assembleArgs = @('-u', $script, '--mode', 'assemble', '--output', $out,
                  '--datasets', 'mpdd', 'btad', '--seeds', '0', '1',
                  '--shots', '1', '2', '4', '8')
$t0 = Get-Date
$ap = Start-Process -FilePath $py -ArgumentList $assembleArgs -NoNewWindow -PassThru `
                    -RedirectStandardOutput $assembleOut -RedirectStandardError $assembleErr
$ap.WaitForExit()
$acode = $null
try { $ap.Refresh(); $acode = $ap.ExitCode } catch { $acode = $null }
Log ("A11_assemble END exit={0} {1}s" -f $(if ($null -eq $acode) { 'unknown' } else { $acode }),
     [int]((Get-Date) - $t0).TotalSeconds)
Progress 'A11_assemble' ("exit={0}" -f $(if ($null -eq $acode) { 'unknown' } else { $acode }))

# ---------------------------------------------------------------- inventory
$artifacts = @()
if (Test-Path -LiteralPath $out) {
    foreach ($f in Get-ChildItem -LiteralPath $out -Recurse -File -ErrorAction SilentlyContinue) {
        if ($f.FullName -match '\\units\\') { continue }
        $artifacts += [ordered]@{
            path   = $f.FullName
            bytes  = $f.Length
            sha256 = (Get-FileHash -LiteralPath $f.FullName -Algorithm SHA256).Hash
        }
    }
}
$unitFiles = @()
if (Test-Path -LiteralPath (Join-Path $out 'units')) {
    foreach ($f in Get-ChildItem -LiteralPath (Join-Path $out 'units') -File) {
        $unitFiles += [ordered]@{ name = $f.Name; bytes = $f.Length
                                  ; sha256 = (Get-FileHash -LiteralPath $f.FullName -Algorithm SHA256).Hash }
    }
}
Write-Json (Join-Path $state 'A11_execution.json') ([ordered]@{
    id = 'A11'
    status = if ($ramKilled) { 'aborted_by_ram_rule' } else { 'completed' }
    executed = $true
    script = $script
    base_vram_mib = $vramBase
    peak_working_set_mib = $peakWorkSetMiB
    stopped_by_ram_rule = $ramKilled
    ram_stop_rule_percent = $ramStopPercent
    shards = @($procs | ForEach-Object {
        [ordered]@{ id = $_.id; command = $_.cmd; start = $_.start.ToString('s')
                    ; seconds = $_.seconds; exit_code = $_.exit
                    ; peak_device_vram_mib = $_.peakVram
                    ; stdout = $_.stdout; stderr = $_.stderr } })
    assemble = [ordered]@{ exit_code = $acode; stdout = $assembleOut; stderr = $assembleErr }
    artifacts = $artifacts
    unit_checkpoints = $unitFiles
}) 10

Progress 'A11' 'done'
Log '=== A11 queue end ==='
