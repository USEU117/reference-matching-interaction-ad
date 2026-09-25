# Non-blocking launcher + resource sampler for a long E1 run.
param(
    [Parameter(Mandatory = $true)][string]$Exe,
    [Parameter(Mandatory = $true)][string]$ScriptArgs,
    [Parameter(Mandatory = $true)][string]$OutLog,
    [Parameter(Mandatory = $true)][string]$ErrLog,
    [Parameter(Mandatory = $true)][string]$StateFile,
    [Parameter(Mandatory = $true)][string]$Id,
    [string]$WorkDir = (Get-Location).Path,
    [int]$IntervalSec = 30
)

$start = Get-Date
$unitLines = @()
$samples = @()
$proc = Start-Process -FilePath $Exe -ArgumentList $ScriptArgs -WorkingDirectory $WorkDir `
    -RedirectStandardOutput $OutLog -RedirectStandardError $ErrLog -PassThru -NoNewWindow
$pid0 = $proc.Id
Write-Output "PID=$pid0"

function Get-TreeWorkingSetMiB([int]$rootPid) {
    # the venv python.exe is a launcher that re-execs the real interpreter, so
    # sum the working set of the process tree, not just the launcher
    $all = Get-Process -ErrorAction SilentlyContinue
    $children = @{}
    foreach ($p in $all) {
        $ppid = $null
        try { $ppid = (Get-CimInstance Win32_Process -Filter "ProcessId=$($p.Id)" -ErrorAction SilentlyContinue).ParentProcessId } catch {}
        if ($ppid) {
            if (-not $children.ContainsKey([int]$ppid)) { $children[[int]$ppid] = @() }
            $children[[int]$ppid] += $p.Id
        }
    }
    $stack = New-Object System.Collections.Stack
    $stack.Push($rootPid)
    $seen = @{}
    $total = 0.0
    while ($stack.Count -gt 0) {
        $id = $stack.Pop()
        if ($seen.ContainsKey($id)) { continue }
        $seen[$id] = $true
        $proc = $all | Where-Object { $_.Id -eq $id }
        if ($proc) { $total += $proc.WorkingSet64 / 1MB }
        if ($children.ContainsKey($id)) { foreach ($c in $children[$id]) { $stack.Push($c) } }
    }
    return [math]::Round($total, 1)
}

function Write-State($status, $exitCode) {
    $os = Get-CimInstance Win32_OperatingSystem
    $totMiB = [math]::Round($os.TotalVisibleMemorySize / 1024, 1)
    $availMiB = [math]::Round($os.FreePhysicalMemory / 1024, 1)
    $obj = [ordered]@{
        id            = $Id
        status        = $status
        pid           = $pid0
        command       = "$Exe $ScriptArgs"
        workdir       = $WorkDir
        start_local   = $start.ToString("s")
        now_local     = (Get-Date).ToString("s")
        elapsed_s     = [math]::Round(((Get-Date) - $start).TotalSeconds, 0)
        exit_code     = $exitCode
        total_ram_mib = $totMiB
        avail_ram_mib = $availMiB
        stdout        = $OutLog
        stderr        = $ErrLog
        units_done    = $unitLines.Count
        last_unit_line = if ($unitLines.Count) { $unitLines[-1] } else { $null }
        samples       = $samples
    }
    $obj | ConvertTo-Json -Depth 6 | Set-Content -Path $StateFile -Encoding UTF8
}

Write-State "running" $null

while (-not $proc.HasExited) {
    Start-Sleep -Seconds $IntervalSec
    if ($proc.HasExited) { break }
    $pr = Get-Process -Id $pid0 -ErrorAction SilentlyContinue
    $os = Get-CimInstance Win32_OperatingSystem
    $ws = Get-TreeWorkingSetMiB $pid0
    $priv = if ($pr) { [math]::Round(($pr.PrivateMemorySize64 + 0) / 1MB, 1) } else { 0 }
    $avail = [math]::Round($os.FreePhysicalMemory / 1024, 1)
    $elapsed = [math]::Round(((Get-Date) - $start).TotalSeconds, 0)
    $tail = @()
    if (Test-Path $OutLog) {
        $tail = Get-Content -Path $OutLog -Tail 6 -ErrorAction SilentlyContinue
    }
    $samples += [ordered]@{
        t_s            = $elapsed
        ws_mib         = $ws
        private_mib    = $priv
        avail_ram_mib  = $avail
        out_tail       = ($tail -join " | ")
    }
    if (Test-Path $OutLog) {
        $unitLines = @(Select-String -Path $OutLog -Pattern '^\[E1:stride\d+\] .*methods \(\d+s\)$' -ErrorAction SilentlyContinue | ForEach-Object { $_.Line })
    }
    Write-Output ("t={0}s ws={1}MiB avail={2}MiB units={3}" -f $elapsed, $ws, $avail, $unitLines.Count)
    Write-State "running" $null
}

$exitCode = $proc.ExitCode
if (Test-Path $OutLog) {
    $unitLines = @(Select-String -Path $OutLog -Pattern '^\[E1:stride\d+\] .*methods \(\d+s\)$' -ErrorAction SilentlyContinue | ForEach-Object { $_.Line })
}
Write-State "finished" $exitCode
Write-Output "EXIT=$exitCode units=$($unitLines.Count)"
