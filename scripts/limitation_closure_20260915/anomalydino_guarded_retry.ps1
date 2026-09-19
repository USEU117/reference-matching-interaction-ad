# Guarded retry for the AnomalyDINO MVTec/VisA dumps (night run 2026-09-18 follow-up).
#
# Why a guard: `run_baseline_anomalydino.py` loads DINOv2 through `torch.hub.load`, and torch.hub
# re-validates the cached repo against the GitHub API on every call.  On this machine that call
# has three times in one night (a) raised RemoteDisconnected, and (b) hung with no timeout - the
# second case cost two hours of wall clock because nothing detects a stalled model load.
#
# This driver runs each pass (canvas, then canvas+rotation) and polls the child's CPU time: if it
# does not advance for -StallMinutes the child is killed and the pass is recorded as stalled, so
# the pass after it (and the rest of the pipeline) still runs.  Dumps are written per category, so
# a stalled pass still leaves everything it finished on disk.  Pure ASCII on purpose.

param(
    [int]$StallMinutes = 8,
    [int]$PollSeconds = 60
)

$ErrorActionPreference = 'Continue'
$root  = 'D:\STUDY\My_github\sci_project'
$night = Join-Path $root 'scripts\limitation_closure_20260915\_night2_20260918'
$py    = Join-Path $root '.venv-anomalyclip\Scripts\python.exe'
$closeout = Join-Path $root 'scripts\paper_evidence_closeout_20260914'
$newExp = Join-Path $root 'experiments\dynamic_fusion\representation_matching_interaction_20260914'
$rm = Join-Path $newExp '05_baselines\region_maps'
$statusFile = Join-Path $night 'anomalydino_guard_status.txt'

function Log([string]$msg) {
    $line = "{0} {1}" -f (Get-Date -Format 'yyyy-MM-dd HH:mm:ss'), $msg
    Add-Content -LiteralPath $statusFile -Value $line -Encoding utf8
    Write-Host $line
}

function Invoke-GuardedPass([string]$passId, [string[]]$stepArgs, [string]$logPath) {
    Log "pass $passId started"
    $proc = Start-Process -FilePath $py -ArgumentList $stepArgs -PassThru -WindowStyle Hidden `
                          -RedirectStandardOutput $logPath -RedirectStandardError "$logPath.err"
    $lastCpu = -1.0
    $stallSeconds = 0
    while (-not $proc.HasExited) {
        Start-Sleep -Seconds $PollSeconds
        $proc.Refresh()
        if ($proc.HasExited) { break }
        $cpu = [double]$proc.TotalProcessorTime.TotalSeconds
        if ($cpu -le $lastCpu + 0.5) {
            $stallSeconds += $PollSeconds
            if ($stallSeconds -ge ($StallMinutes * 60)) {
                Log "pass $passId STALLED (cpu frozen at $([int]$cpu)s for $([int]($stallSeconds/60)) min) - killing pid $($proc.Id)"
                try { Stop-Process -Id $proc.Id -Force -ErrorAction Stop } catch { }
                Log "pass $passId result=stalled"
                return 'stalled'
            }
        } else {
            $stallSeconds = 0
        }
        $lastCpu = $cpu
    }
    $code = $proc.ExitCode
    Log "pass $passId result=exit$code"
    return "exit$code"
}

Log "guarded AnomalyDINO retry start (stall threshold ${StallMinutes} min)"

# Pass 1: canvas frame, visa only (MVTec's canvas dumps are complete already).
$canvasArgs = @('-u', (Join-Path $closeout 'run_baseline_anomalydino.py'),
    '--out', (Join-Path $newExp '05_baselines\anomalydino_mvtec_visa_canvas'), '--frame', 'canvas',
    '--suffix', '_canvas', '--datasets', 'visa', '--seeds', '0', '1', '--shots', '1', '4',
    '--dump-maps', (Join-Path $rm 'anomalydino_canvas'))
[void](Invoke-GuardedPass 'visa_canvas' $canvasArgs (Join-Path $night 'guard_visa_canvas.log'))

# Pass 2: canvas + rotation, visa.
$rotationArgs = @('-u', (Join-Path $closeout 'run_baseline_anomalydino.py'),
    '--out', (Join-Path $newExp '05_baselines\anomalydino_mvtec_visa_canvas_rotation'), '--frame',
    'canvas', '--rotation', '--suffix', '_canvas_rotation', '--datasets', 'visa', '--seeds', '0', '1',
    '--shots', '1', '4', '--dump-maps', (Join-Path $rm 'anomalydino_canvas_rotation'))
[void](Invoke-GuardedPass 'visa_rotation' $rotationArgs (Join-Path $night 'guard_visa_rotation.log'))

$canvas = @(Get-ChildItem (Join-Path $rm 'anomalydino_canvas') -Filter '*.npz' -File -ErrorAction SilentlyContinue).Count
$rot = @(Get-ChildItem (Join-Path $rm 'anomalydino_canvas_rotation') -Filter '*.npz' -File -ErrorAction SilentlyContinue).Count
Log "dump counts: canvas=$canvas rotation=$rot"
Log 'guarded AnomalyDINO retry done'
exit 0
