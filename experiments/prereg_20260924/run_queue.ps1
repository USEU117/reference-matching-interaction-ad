# Pre-registration execution queue - 2026-09-24
#
# Scope: the four GPU-flagged items approved from docs/PREREGISTRATION_20260924_CN.md
# (A04 / A08 / A11 / A22).  Strictly serial: one GPU, 6 GiB, no concurrency.
#
# Order: A22 -> A11 -> A04 -> A08   (cheap/decidable first, long job last)
#
# Invariants enforced here:
#   * every product of this run is written under experiments/prereg_20260924/ ;
#     no pre-existing artefact is overwritten (the pre-flight verdicts below are the
#     reason A22 / A11 / A04 are not executed at all - see state/A22.json ... );
#   * a failing step does not stop the queue, but its dependants are skipped
#     (the pre-registration stop rules are applied per step);
#   * per step: start time, command, exit code, wall time, peak device VRAM
#     (nvidia-smi memory.used sampled every 15 s, maximum kept), stdout/stderr split
#     into logs/, artefact paths + SHA-256 into state/<item>.json ;
#   * one progress line per step appended to state/progress.txt .
#
# Pure ASCII on purpose: Windows PowerShell 5.1 decodes a BOM-less .ps1 as GBK.

$ErrorActionPreference = 'Continue'

$root     = 'D:\STUDY\My_github\sci_project'
$base     = Join-Path $root 'experiments\prereg_20260924'
$logs     = Join-Path $base 'logs'
$out      = Join-Path $base 'out'
$state    = Join-Path $base 'state'
$py       = Join-Path $root '.venv-anomalyclip\Scripts\python.exe'
$progress = Join-Path $state 'progress.txt'
$queueLog = Join-Path $logs  'queue.log'

$gpuTotalMiB        = 6144
$requiredFreeMiB    = 1200     # minimum free device memory before a step may start
$gpuWaitSeconds     = 15
$gpuWaitMaxMinutes  = 15       # give up and skip the step after this long
$sampleSeconds      = 15       # VRAM / RAM sampling period
$ramStopPercent     = 80       # pre-registration stop rule for A08: >80% of physical RAM
# The RAM stop rule is applied to the STEP'S OWN peak working set, not to whole-machine
# usage: this desktop already idles at ~74% of its 15.8 GB (unrelated apps), so a
# machine-wide threshold would fire before any job could start.  Machine-wide usage is
# still sampled and logged for the record.
$totalPhysMiB       = [int]((Get-CimInstance Win32_OperatingSystem).TotalVisibleMemorySize / 1024)
$ramStopMiB         = [int]($totalPhysMiB * $ramStopPercent / 100)

New-Item -ItemType Directory -Force -Path $logs, $out, $state | Out-Null

function Log([string]$msg) {
    $line = "{0} {1}" -f (Get-Date -Format 'yyyy-MM-dd HH:mm:ss'), $msg
    Add-Content -LiteralPath $queueLog -Value $line -Encoding utf8
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

function Skip-Item([string]$id, [string]$reason) {
    Write-Json (Join-Path $state "$id.json") ([ordered]@{
        id            = $id
        status        = 'not_runnable'
        skipped_utc   = (Get-Date).ToString('s')
        reason        = $reason
        executed      = $false
    }) 5
    Log  "$id NOT RUNNABLE - $reason"
    Progress $id "SKIPPED (not runnable)"
    return $false
}

function Wait-GpuEnough {
    $deadline = (Get-Date).AddMinutes($gpuWaitMaxMinutes)
    while ($true) {
        $used = Get-UsedMiB
        if ($null -eq $used) { Log 'GPU probe unavailable - proceeding'; return $true }
        $free = $gpuTotalMiB - $used
        if ($free -ge $requiredFreeMiB) { return $true }
        if ((Get-Date) -gt $deadline) {
            Log ("GPU free {0} MiB < {1} MiB after {2} min wait - skipping step" -f $free, $requiredFreeMiB, $gpuWaitMaxMinutes)
            return $false
        }
        Log ("GPU free {0} MiB < {1} MiB - waiting {2}s" -f $free, $requiredFreeMiB, $gpuWaitSeconds)
        Start-Sleep -Seconds $gpuWaitSeconds
    }
}

function Invoke-GpuStep {
    param(
        [string]   $Id,
        [string[]] $PyArgs,
        [string]   $ArtifactDir,
        [string]   $SuccessArtifact = $null
    )

    if (-not (Wait-GpuEnough)) {
        Write-Json (Join-Path $state "$Id.json") ([ordered]@{
            id = $Id; status = 'skipped_no_gpu'; skipped_utc = (Get-Date).ToString('s')
        }) 4
        Progress $Id 'SKIPPED (insufficient GPU memory)'
        return $false
    }

    $stdoutPath = Join-Path $logs ("{0}.out" -f $Id)
    $stderrPath = Join-Path $logs ("{0}.err" -f $Id)
    $start      = Get-Date
    $baseUsed   = Get-UsedMiB
    $cmdLine    = '"{0}" {1}' -f $py, ($PyArgs -join ' ')

    Log ("{0} START  {1}" -f $Id, $cmdLine)

    $proc = Start-Process -FilePath $py -ArgumentList $PyArgs -NoNewWindow -PassThru `
                          -RedirectStandardOutput $stdoutPath `
                          -RedirectStandardError  $stderrPath

    $peak      = 0
    if ($null -ne $baseUsed) { $peak = $baseUsed }
    $ramKilled = $false
    $tick      = 0
    while (-not $proc.HasExited) {
        Start-Sleep -Seconds $sampleSeconds
        $tick++
        $u = Get-UsedMiB
        if ($null -ne $u -and $u -gt $peak) { $peak = $u }
        if (($tick % 4) -eq 0) {
            try {
                $proc.Refresh()
                $jobPeakMiB = [int]($proc.PeakWorkingSet64 / 1MB)
                $os = Get-CimInstance Win32_OperatingSystem
                $sysUsedPct = [math]::Round(100.0 * ($os.TotalVisibleMemorySize - $os.FreePhysicalMemory) / $os.TotalVisibleMemorySize, 1)
                Log ("{0} mem job_peak={1}MiB (limit {2}MiB) system_used={3}%" -f $Id, $jobPeakMiB, $ramStopMiB, $sysUsedPct)
                if ($jobPeakMiB -ge $ramStopMiB -and -not $proc.HasExited) {
                    Log ("{0} STOP RULE: step peak working set {1}MiB >= {2}% of physical RAM ({3}MiB) - terminating" -f $Id, $jobPeakMiB, $ramStopPercent, $ramStopMiB)
                    $ramKilled = $true
                    $proc.Kill()
                    break
                }
            } catch { }
        }
    }
    try { $proc.WaitForExit() } catch { }
    # On this host Start-Process -PassThru does not expose ExitCode (always null, verified
    # with a trivial `cmd /c exit 7` child), so the exit code is treated as "unknown" and the
    # step verdict falls back to the presence of its declared success artefact.
    $code = $null
    try { $proc.Refresh(); $code = $proc.ExitCode } catch { $code = $null }
    $codeKnown = ($null -ne $code)
    $artifactOk = $true
    if ($SuccessArtifact) { $artifactOk = Test-Path -LiteralPath $SuccessArtifact }
    $success = $artifactOk -and (-not $codeKnown -or $code -eq 0) -and (-not $ramKilled)
    $end  = Get-Date
    $secs = [int]($end - $start).TotalSeconds

    $artifacts = @()
    if (Test-Path -LiteralPath $ArtifactDir) {
        foreach ($f in Get-ChildItem -LiteralPath $ArtifactDir -Recurse -File -ErrorAction SilentlyContinue) {
            $artifacts += [ordered]@{
                path   = $f.FullName
                bytes  = $f.Length
                sha256 = (Get-FileHash -LiteralPath $f.FullName -Algorithm SHA256).Hash
            }
        }
    }

    Write-Json (Join-Path $state "$Id.json") ([ordered]@{
        id                  = $Id
        status              = if ($success) { 'completed' } else { 'failed' }
        command             = $cmdLine
        start_local         = $start.ToString('s')
        end_local           = $end.ToString('s')
        duration_seconds    = $secs
        exit_code           = $code
        exit_code_known     = $codeKnown
        stopped_by_ram_rule = $ramKilled
        success_artifact    = $SuccessArtifact
        success_artifact_ok = $artifactOk
        vram_baseline_mib   = $baseUsed
        vram_peak_mib       = $peak
        stdout_bytes        = (Get-Item -LiteralPath $stdoutPath -EA SilentlyContinue).Length
        stderr_bytes        = (Get-Item -LiteralPath $stderrPath -EA SilentlyContinue).Length
        stdout              = $stdoutPath
        stderr              = $stderrPath
        artifacts           = $artifacts
    }) 6

    Log ("{0} END success={1} exit={2} {3}s peak_vram={4}MiB ram_kill={5}" -f $Id, $success, $(if ($codeKnown) { $code } else { 'unknown' }), $secs, $peak, $ramKilled)
    Progress $Id ("success={0} exit={1} duration={2}s peak_vram={3}MiB artifacts={4}" -f $success, $(if ($codeKnown) { $code } else { 'unknown' }), $secs, $peak, $artifacts.Count)
    return $success
}

# --------------------------------------------------------------------------- #
# queue
# --------------------------------------------------------------------------- #
Log "=== queue start (A22 -> A11 -> A04 -> A08) base=$base ==="
Progress 'QUEUE' 'started'

# ---- A22 ------------------------------------------------------------------- #
# Pre-registered need: "在统一几何子集内并列展示 PatchCore 的两原生配置（448 与 224）".
# No script implements it: the harmonised toolchain (run_patchcore_harmonised.py,
# harmonised_common_region.py) deliberately collapses PatchCore to the single 448 column
# and its specs/rect rules assume short-side 448, so a native-224 column cannot be added
# without new code AND would break the subset's single-geometry premise.  The nearest
# existing driver (run_patchcore_harmonised.py) would only re-produce the already-complete
# 448 column and writes into the existing 05_baselines_harmonised_20260922 tree.
Skip-Item 'A22' 'no script implements the pre-registered protocol (second PatchCore native-224 column inside the single-geometry harmonised subset); existing harmonised drivers hard-code short side 448 and write only into the pre-existing 05_baselines_harmonised_20260922 tree'

# ---- A11 ------------------------------------------------------------------- #
# Pre-registered need: 3 ablations x (seed 0,1 x K 1,2,4,8) = 8 conditions x 2 datasets,
# with image-level paired 95% intervals.
# e2_shared_op_ablation.py exists but hard-codes SEEDS[dataset][:1] (seed 0 only), so the
# pre-registered seed-1 half cannot be produced; it computes no bootstrap intervals; and the
# companion step e2_abl_s_addendum.py has no CLI - it writes interaction_by_ablation.csv /
# ablation_metrics_abl_s_L.csv / E2_ADDENDUM_SUMMARY.json into the pre-existing
# E2_shared_op_ablation directory (same for --mode check -> V2_2_RESCALER_CHECK.json),
# i.e. it would overwrite existing artefacts.
Skip-Item 'A11' 'shipped script cannot produce the pre-registered grid (seed 1 hard-coded out: SEEDS[dataset][:1]) and computes no bootstrap intervals; its mandatory companion (e2_abl_s_addendum.py, and --mode check) writes into the pre-existing E2_shared_op_ablation directory and would overwrite existing artefacts'

# ---- A04 ------------------------------------------------------------------- #
# Pre-registered need: common metric x common perturbation across the six tested
# configurations, with image-level paired intervals.
# No script exists for it, and the pre-registration itself records that the axis
# definition is not settled (EXPERIMENT_GAP_ANALYSIS 7.2 D-01: define the axes first).
Skip-Item 'A04' 'no script exists for a common-metric x common-perturbation cross-method stability run; the pre-registration records that the comparison axes are not yet defined (EXPERIMENT_GAP_ANALYSIS D-01), so there is nothing to execute without inventing a protocol'

# ---- A08 ------------------------------------------------------------------- #
# Command corrected against the shipped argparse: the registered `--grid fullpixel` does not
# exist (grid is selected with `--stride`, 1 == full pixel) and the products are
# point_stride1.csv / E1_STATUS_stride1.json, not point_fullpixel.csv / E1_STATUS_fullpixel.json.
# `--mode verify` / `--mode validate` are NOT run: their output directory is hard-coded to the
# pre-existing E1_fullpixel_ci tree and would overwrite V1_CHECKS.json / V1_3_END_TO_END.json.
$a08dir = Join-Path $out 'A08'
New-Item -ItemType Directory -Force -Path $a08dir | Out-Null

$a08run = @(
    '-u',
    (Join-Path $root 'scripts\limitation_closure_20260915\e1_fullpixel_ci.py'),
    '--mode', 'run',
    '--stride', '1',
    '--replicates', '1000',
    '--datasets', 'mpdd', 'btad',
    '--output', $a08dir
)
$okFullpixel = Invoke-GpuStep -Id 'A08a_run_fullpixel' -PyArgs $a08run -ArtifactDir $a08dir `
                             -SuccessArtifact (Join-Path $a08dir 'replicate_stride1.npz')

if ($okFullpixel) {
    $a08report = @(
        '-u',
        (Join-Path $root 'scripts\limitation_closure_20260915\e1_report.py'),
        '--dir', $a08dir,
        '--strides', '1'
    )
    Invoke-GpuStep -Id 'A08b_report' -PyArgs $a08report -ArtifactDir $a08dir `
                   -SuccessArtifact (Join-Path $a08dir 'interaction_by_grid.csv') | Out-Null
} else {
    Log 'A08b_report SKIPPED - dependency A08a did not complete'
    Progress 'A08b_report' 'SKIPPED (dependency A08a failed or was skipped)'
}

Progress 'QUEUE' 'done'
Log '=== queue end ==='
