# E1/E2/E3 K-range extension, recovery driver (night run 2026-09-18, phase 3).
#
# Why this exists: the first phase-3 attempt died inside s4_extra_encoders.py at its metric
# stage because the seed-2 BTAD ground truth was missing:
#     01_geometry/gt/btad_s2_{01,02,03}_faithful.npz   (only seeds 0/1 had been frozen)
# Those three files were generated afterwards with freeze_s0.faithful_gt(), so the metric
# stage can now run.  s4 --skip-existing reuses every feature cache and score already on disk,
# so this driver only finishes the outstanding encoding plus the metrics, then refreshes the
# five-encoder table (s10), which the orchestrator skipped because of its own fail-fast branch
# guard.  Pure ASCII on purpose (Windows PowerShell 5.1 decodes BOM-less .ps1 as GBK).

$ErrorActionPreference = 'Continue'
$root  = 'D:\STUDY\My_github\sci_project'
$night = Join-Path $root 'scripts\limitation_closure_20260915\_night2_20260918'
$py    = Join-Path $root '.venv-anomalyclip\Scripts\python.exe'
$rep   = Join-Path $root 'scripts\representation_matching_interaction_20260914'
$statusFile = Join-Path $night 'echain_status.txt'

function Log([string]$msg) {
    $line = "{0} {1}" -f (Get-Date -Format 'yyyy-MM-dd HH:mm:ss'), $msg
    Add-Content -LiteralPath $statusFile -Value $line -Encoding utf8
    Write-Host $line
}

function Invoke-EStep([string]$id, [string[]]$stepArgs) {
    $log = Join-Path $night "echain_$id.log"
    $err = Join-Path $night "echain_$id.err"
    Log "step $id started"
    $sw = [Diagnostics.Stopwatch]::StartNew()
    $global:LASTEXITCODE = 0
    & $py @stepArgs 1>> $log 2>> $err
    $code = $LASTEXITCODE
    if ($null -eq $code) { $code = 0 }
    $sw.Stop()
    Log "step $id exit=$code ($([int]$sw.Elapsed.TotalSeconds)s)"
    return $code
}

Log 'E chain start'

foreach ($branch in @('E1', 'E2', 'E3')) {
    $code = Invoke-EStep "s4_$branch" @('-u', (Join-Path $rep 's4_extra_encoders.py'),
        '--branch', $branch, '--seeds', '0', '1', '2', '--shots', '1', '2', '4', '8',
        '--device', 'cuda', '--workers', '4', '--skip-existing', '--fast-replicates')
    if ($code -ne 0) { Log "E chain stopped: s4_$branch failed"; exit 1 }
}

$code = Invoke-EStep 's10_encoder_comparison' @('-u', (Join-Path $rep 's10_encoder_comparison.py'))
if ($code -ne 0) { Log 'E chain stopped: s10 failed'; exit 1 }

Log 'E chain complete: three branches + s10 all exit=0'
exit 0
