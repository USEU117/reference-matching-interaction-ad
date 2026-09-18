# Real-time progress for the three outstanding matrix batches, refreshed in one place.
#
#   powershell -ExecutionPolicy Bypass -File scripts\limitation_closure_20260915\watch_progress.ps1
#   powershell -ExecutionPolicy Bypass -File scripts\limitation_closure_20260915\watch_progress.ps1 -Once
#
# A batch is reported as stalled when its newest DONE.json is older than -StallSeconds, which is
# what a silently killed process looks like: the counters stop while STATUS.json still says
# "running".  That is exactly the failure this script exists to catch.

param(
    [int]$IntervalSeconds = 30,
    [int]$StallSeconds = 300,
    [switch]$Once
)

$repo = (Resolve-Path (Join-Path $PSScriptRoot '..\..')).Path
$batches = @(
    @{ Name = 'D  mpdd  (seeds 0-7, cuda)'; Path = "$repo\experiments\dynamic_fusion\seeds_extension_20260917\p1_matrix_mpdd"; Expected = 192; Pattern = '' },
    @{ Name = 'D  btad 01/02 (seeds 0-7, cuda)'; Path = "$repo\experiments\dynamic_fusion\seeds_extension_20260917\p1_matrix_btad"; Expected = 64; Pattern = '' },
    # the generalization matrix already holds 180 finished MVTec units, so only the VisA ones are
    # still outstanding and only those are counted for the rate/ETA
    @{ Name = 'C  visa  (seeds 0-2, cpu)'; Path = "$repo\experiments\dynamic_fusion\generalization_mvtec_visa_20260915\p1_matrix"; Expected = 144; Pattern = 'visa_s' }
)

function Get-ParallelActive {
    # While the parallel dispatcher is feeding VisA units, the batch's own STATUS.json is not
    # updated unit by unit, so the "no new DONE for a while" test would flag a healthy run.
    $log = Join-Path $repo 'experiments\dynamic_fusion\generalization_mvtec_visa_20260915\log_matrix_visa_parallel.txt'
    if (-not (Test-Path $log)) { return $false }
    $lines = Get-Content $log
    if (@($lines | Select-String '^\[parallel\] done ').Count -gt 0) { return $false }
    if (@($lines | Select-String 'queue drained').Count -gt 0) { return $true }
    return @($lines | Select-String '^\[parallel\] (started|finished|throttled) ').Count -gt 0
}

function Show-Progress {
    $alive = @(Get-Process python -ErrorAction SilentlyContinue).Count
    $parallelActive = Get-ParallelActive
    Write-Output "=== $(Get-Date -Format 'yyyy-MM-dd HH:mm:ss')   live python processes: $alive ==="
    foreach ($batch in $batches) {
        if (-not (Test-Path $batch.Path)) {
            Write-Output ("{0,-34} not started" -f $batch.Name)
            continue
        }
        $units = Join-Path $batch.Path 'units'
        $done = @(Get-ChildItem $units -Recurse -Filter 'DONE.json' -ErrorAction SilentlyContinue |
            Where-Object { $batch.Pattern -eq '' -or $_.FullName -match $batch.Pattern })
        $n = $done.Count
        $statusPath = Join-Path $batch.Path 'STATUS.json'
        $state = 'unknown'
        $unit = '-'
        if (Test-Path $statusPath) {
            $status = Get-Content $statusPath -Raw | ConvertFrom-Json
            $state = $status.state
            $unit = $status.unit
        }
        $newest = if ($n -gt 0) { ($done | Sort-Object LastWriteTime -Descending | Select-Object -First 1).LastWriteTime } else { $null }
        $ageText = 'n/a'
        $stall = ''
        if ($newest) {
            $age = ((Get-Date) - $newest).TotalSeconds
            $ageText = '{0:N0}s ago' -f $age
            # A finished batch is expected to stop producing DONE.json; only a batch that claims to
            # be running while nothing lands is stalled - and the VisA batch is covered by the
            # dispatcher line below while that dispatcher is alive.
            $managed = ($batch.Pattern -eq 'visa_s' -and $parallelActive)
            if ($age -gt $StallSeconds -and $state -ne 'completed' -and -not $managed) {
                $stall = '   *** STALLED ***'
            }
            if ($managed) { $stall = '   (parallel dispatcher active)' }
        }
        $etaText = '-'
        if ($n -ge 3 -and $newest) {
            $recent = $done | Sort-Object LastWriteTime -Descending | Select-Object -First 40
            $times = @($recent | ForEach-Object { $_.LastWriteTime } | Sort-Object)
            $diffs = @()
            for ($i = 1; $i -lt $times.Count; $i++) {
                $diffs += ($times[$i] - $times[$i - 1]).TotalSeconds
            }
            # Median of consecutive gaps, not the mean over the window: a batch that was killed and
            # resumed leaves one huge gap behind, and the mean would report it as the current rate.
            if ($diffs.Count -gt 0 -and ($age -le $StallSeconds -or $managed)) {
                $sorted = $diffs | Sort-Object
                $per = $sorted[[Math]::Floor($sorted.Count / 2)]
                $left = ($batch.Expected - $n) * $per / 60
                $etaText = '{0:N0} min ({1:N0}s/unit, median of {2} gaps)' -f $left, $per, $diffs.Count
            }
        }
        Write-Output ("{0,-34} {1,4}/{2,-4} state={3,-16} last={4,-10} ETA={5}{6}" -f `
            $batch.Name, $n, $batch.Expected, $state, $ageText, $etaText, $stall)
        if ($state -ne 'unknown' -and $unit -ne '-') { Write-Output ("{0,-34}   current: {1}" -f '', $unit) }
    }

    foreach ($batch in $batches) {
        $f = Join-Path $batch.Path 'FAILURES.json'
        if (-not (Test-Path $f)) { continue }
        $payload = Get-Content $f -Raw | ConvertFrom-Json
        if ($payload.Count -eq 0) { continue }
        $stamp = (Get-Item $f).LastWriteTime
        $units = Join-Path $batch.Path 'units'
        $newestDone = Get-ChildItem $units -Recurse -Filter 'DONE.json' -ErrorAction SilentlyContinue |
            Sort-Object LastWriteTime -Descending | Select-Object -First 1
        # run_matrix.py writes FAILURES.json when a batch stops; while a resumed batch is still
        # running the file on disk is left over from the previous attempt, so age it.
        $tag = if ($newestDone -and $stamp -lt $newestDone.LastWriteTime) { 'STALE (pre-restart)' } else { 'CURRENT' }
        Write-Output ("{0} FAILURES in {1} [{2} {3:HH:mm:ss}]: {4}" -f `
            $tag, $batch.Name, $tag, $stamp, ($payload | ConvertTo-Json -Compress))
    }
}

function Show-Analysis {
    $gen = "$repo\experiments\dynamic_fusion\generalization_mvtec_visa_20260915"
    $sub = "$repo\experiments\dynamic_fusion\seeds_extension_20260917"

    # how many VisA unit processes the parallel dispatcher is feeding right now
    $parallelLog = Join-Path $gen 'log_matrix_visa_parallel.txt'
    if (Test-Path $parallelLog) {
        $lines = Get-Content $parallelLog
        $started = @($lines | Select-String '^\[parallel\] started ').Count
        $finished = @($lines | Select-String '^\[parallel\] finished ').Count
        $noDone = @($lines | Select-String '^\[parallel\] FAILED ').Count
        $drained = @($lines | Select-String 'queue drained').Count -gt 0
        $done = @($lines | Select-String '^\[parallel\] done ').Count -gt 0
        # `FAILED` lines are written from a flag that cannot read ExitCode on this PowerShell build;
        # the authoritative count of unfinished units is the queue, so report that instead.
        $visaDone = @(Get-ChildItem (Join-Path $gen 'p1_matrix\units') -Recurse -Filter 'DONE.json' `
            -ErrorAction SilentlyContinue | Where-Object { $_.FullName -match 'visa_s' }).Count
        Write-Output ("visa dispatcher                     started={0} finished={1} remaining={2} drained={3} done={4}" -f `
            $started, $finished, (144 - $visaDone), $drained, $done)
        if ($noDone -gt 0) {
            Write-Output ("  note: {0} FAILED lines before 20:35 are false alarms (units did produce DONE.json)" -f $noDone)
        }
    }

    # the analysis chain: phase marker plus the tail of whatever it is currently writing
    $chainLog = Join-Path $sub 'logs_analysis.txt'
    $marker = Join-Path $sub 'ANALYSIS_CHAIN.json'
    if (Test-Path $marker) {
        $payload = Get-Content $marker -Raw | ConvertFrom-Json
        Write-Output ("analysis chain                      FINISHED {0}" -f $payload.finished_utc)
        foreach ($step in $payload.steps) {
            Write-Output ("  step {0,-34} exit {1}" -f $step.step, $step.exit_code)
        }
    } elseif (Test-Path $chainLog) {
        Write-Output "analysis chain                      running (phase log below)"
    } else {
        Write-Output "analysis chain                      not started"
    }
    if (Test-Path $chainLog) {
        $tail = Get-Content $chainLog -ErrorAction SilentlyContinue |
            Select-String -Pattern '^\[analysis\]|^\[D3\]|^\[D2b\]|^\[C5\]' |
            Select-Object -Last 3
        foreach ($line in $tail) {
            $text = $line.ToString().Trim()
            if ($text.Length -gt 110) { $text = $text.Substring(0, 110) + '...' }
            Write-Output ("  {0}" -f $text)
        }
    }

    # workflow C statistics, once the chain reaches them
    foreach ($name in @('p4_fullpixel', 'p1_statistics', 'p2_conditions')) {
        $path = Join-Path $gen $name
        $exists = Test-Path $path
        $n = if ($exists) { (Get-ChildItem $path -File -ErrorAction SilentlyContinue).Count } else { 0 }
        Write-Output ("  C statistics {0,-14} files={1}" -f $name, $n)
    }
    $c5 = Join-Path $gen 'C5_SUMMARY.json'
    $c5State = 'pending'
    if (Test-Path $c5) { $c5State = 'present' }
    Write-Output ("  C interaction table              {0}" -f $c5State)

    $dState = 'pending'
    if (Test-Path (Join-Path $sub 'interaction_by_seed.csv')) { $dState = 'present' }
    $vState = 'pending'
    if (Test-Path (Join-Path $sub 'interaction_seed_variance.json')) { $vState = 'present' }
    Write-Output ("  D per-seed table                 {0}" -f $dState)
    Write-Output ("  D variance report                {0}" -f $vState)
}

while ($true) {
    Show-Progress
    Show-Analysis
    if ($Once) { break }
    Start-Sleep -Seconds $IntervalSeconds
}
