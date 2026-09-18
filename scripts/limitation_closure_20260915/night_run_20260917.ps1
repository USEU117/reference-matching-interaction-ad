# One-shot night driver for 2026-09-17/18.  Launched detached, it runs the whole sequence
# unattended and writes a machine-readable status file after every phase, so a monitor (or a later
# reader) can tell what finished without trusting exit codes.
#
#   phase 0  preflight            interpreters, GPU, disk, canonical caches, Swin weights
#   phase 1  VisA matrix          the 69 outstanding units, 3-way GPU, supervised with a stall test
#   phase 2  analysis chain       d2b + fullpixel + stats_v2 + analyze_conditions + c5  (background,
#                                 started ONLY on a complete VisA matrix)
#   phase 3  BTAD-03 matrix       32 units (8 seeds x K1/2/4/8) so workflow G has three categories
#   phase 4  Swin-T (E3) + S10    the fifth branch and the five-encoder table
#   phase 5  chain result         BOUNDED wait, recorded, never blocking phases 3/4/6
#   phase 6  d3 support variance  needs only phase 3
#   phase 7  close-out            NIGHT_RUN_STATUS.json + NIGHT_RUN_REPORT_CN.md for the morning
#
# Interruption rules, learned from the 2026-09-17 night:
#   * single instance: a lock file holds this process id, so a double launch cannot put two
#     dispatchers on the same VisA queue
#   * the phase-1 dispatcher is supervised, not merely awaited: a stall is "no new DONE.json for
#     VisAStallMinutes while the log is not reporting throttling" (a throttled run is healthy and is
#     never killed), with a hard cap as the backstop.  Killing it costs only the in-flight units,
#     because the queue is rebuilt from the DONE.json files on the next launch.
#   * E3 and d3 must NOT sit behind the analysis chain.  The chain is the longest CPU stage and the
#     one most likely to stall; in the first version of this script a stalled chain would have
#     blocked both remaining phases until the deadline, wasting the night.  Only the bounded
#     chain-result wait (phase 5) depends on it, and it proceeds regardless of the outcome.
#   * the chain must not run on a partial VisA matrix: run_analysis.ps1 deliberately proceeds after
#     its own stall window, which would produce statistics and a C5 table computed on fewer units
#     while still reporting success.  Those tables go into the paper, so the gate is here.
#   * every long task is a separate process; this script owns the sequence, not the terminal
#   * a phase is judged by the artefact it must have produced, never by `$LASTEXITCODE`
#     (`Start-Process -PassThru` does not expose ExitCode on this box, and killed children return
#     -1 without a traceback)
#   * every phase first checks for its own output, so re-launching this script after a crash skips
#     finished work instead of recomputing it (the VisA dispatcher, run_matrix --resume and
#     s4 --skip-existing are all idempotent for the same reason)
#   * a failing phase never deletes anything and never blocks an independent phase
#   * THIS FILE IS ASCII-ONLY, and it must stay that way.  Windows PowerShell 5.1 decodes a .ps1 as
#     ANSI (GBK here) unless it carries a UTF-8 BOM, so a single non-ASCII literal corrupts the
#     parse and the script will not load at all.  Chinese text belongs in night_report.py, which
#     Python reads as UTF-8.
#
# Usage (detached, which is the only safe way):
#   Start-Process powershell -ArgumentList '-NoProfile','-ExecutionPolicy','Bypass','-File',
#     'scripts\limitation_closure_20260915\night_run_20260917.ps1' -WindowStyle Hidden
#
# Safe validation without starting anything (takes no lock, writes no status file):
#   powershell -NoProfile -ExecutionPolicy Bypass -File night_run_20260917.ps1 -PreflightOnly
#
# Monitoring from another terminal:
#   powershell -NoProfile -ExecutionPolicy Bypass -File scripts\limitation_closure_20260915\night_watch.ps1

param(
    [string]$Python = '.venv-anomalyclip\Scripts\python.exe',
    [int]$VisAConcurrency = 3,
    [double]$MaxHours = 11,
    [int]$ChainWaitMaxMinutes = 240,
    [int]$VisAStallMinutes = 20,
    [int]$VisAHardCapMinutes = 240,
    [switch]$SkipG,
    [switch]$SkipSwinT,
    [switch]$PreflightOnly
)

$ErrorActionPreference = 'Continue'
$repo = (Resolve-Path (Join-Path $PSScriptRoot '..\..')).Path
$py = Join-Path $repo $Python
$sub = Join-Path $repo 'experiments\dynamic_fusion\seeds_extension_20260917'
$gen = Join-Path $repo 'experiments\dynamic_fusion\generalization_mvtec_visa_20260915'
$new = Join-Path $repo 'experiments\dynamic_fusion\representation_matching_interaction_20260914'
$closure = Join-Path $repo 'scripts\limitation_closure_20260915'
$scripts = Join-Path $repo 'scripts\unified_fusion_paper_support_v1'
$out = Join-Path $closure '_night_20260917'
$statusPath = Join-Path $out 'NIGHT_RUN_STATUS.json'
$deadline = (Get-Date).AddHours($MaxHours)

New-Item -ItemType Directory -Force -Path $out | Out-Null

# ------------------------------------------------------------------ single-instance lock
# Launching this script twice (a double click, or a re-launch before the first one finished) would
# put two VisA dispatchers on the same queue.  run_matrix would not corrupt anything, but units
# would be recomputed concurrently and the status file would be overwritten by whichever process
# wrote last, which is exactly the confusion the status file exists to prevent.
$lockPath = Join-Path $out 'RUNNING.lock'
$otherPid = 0
if (Test-Path $lockPath) {
    try { $otherPid = [int]((Get-Content $lockPath -Raw).Trim()) } catch { $otherPid = 0 }
}
if ($otherPid -gt 0) {
    $other = Get-Process -Id $otherPid -ErrorAction SilentlyContinue
    if ($other -and $other.ProcessName -eq 'powershell') {
        if ($PreflightOnly) {
            "another night run is alive (pid $otherPid); preflight only, nothing written" | Write-Output
            exit 0
        }
        "[night] refusing to start: another night run is alive (pid $otherPid)" |
            Add-Content (Join-Path $out 'logs_night.txt')
        exit 2
    }
    "[night] stale lock from pid $otherPid; taking over" | Add-Content (Join-Path $out 'logs_night.txt')
}
if (-not $PreflightOnly) {
    # a validation pass must not take the lock, or a night run starting at the same moment would see
    # it and refuse to start
    $PID | Set-Content -LiteralPath $lockPath -Encoding ascii
}

# ------------------------------------------------------------------ bookkeeping helpers
$script:state = [ordered]@{ started = (Get-Date -Format s); phases = @{}; finished = $null }

function Set-Phase([string]$name, [string]$result, [string]$note, $extra) {
    $entry = [ordered]@{ result = $result; note = $note; at = (Get-Date -Format s) }
    if ($extra) { foreach ($key in $extra.Keys) { $entry[$key] = $extra[$key] } }
    $script:state.phases[$name] = $entry
    $script:state | ConvertTo-Json -Depth 8 | Set-Content -LiteralPath $statusPath -Encoding utf8
    "[night] $name -> $result : $note" | Add-Content (Join-Path $out 'logs_night.txt')
}

function Get-Log([string]$name) { return (Join-Path $out ("phase_{0}.log" -f $name)) }

function Count-Done([string]$matrixRoot, [string]$pattern) {
    $units = Join-Path $matrixRoot 'units'
    if (-not (Test-Path $units)) { return 0 }
    return @(Get-ChildItem $units -Recurse -Filter 'DONE.json' -ErrorAction SilentlyContinue |
             Where-Object { $pattern -eq '' -or $_.FullName -match $pattern }).Count
}

function Count-CategoryDone([string]$matrixRoot, [string]$dataset, [string]$category) {
    $units = Join-Path $matrixRoot 'units'
    if (-not (Test-Path $units)) { return 0 }
    return @(Get-ChildItem $units -Recurse -Directory -ErrorAction SilentlyContinue |
             Where-Object { $_.Name -eq $category -and $_.Parent.Name -like "$dataset`_s*" -and
                            (Test-Path (Join-Path $_.FullName 'DONE.json')) }).Count
}

function Get-FreeGb { return (Get-CimInstance Win32_OperatingSystem).FreePhysicalMemory / 1MB }

function Get-FreeVramMb {
    $raw = (& nvidia-smi --query-gpu=memory.free --format=csv,noheader,nounits) 2>$null
    if (-not $raw) { return -1 }
    return [int](($raw -replace '[^0-9]', ''))
}

function Read-Json([string]$path) {
    if (-not (Test-Path $path)) { return $null }
    try { return (Get-Content $path -Raw | ConvertFrom-Json) } catch { return $null }
}

# ------------------------------------------------------------------ phase 0: preflight
$pre = [ordered]@{}
$pre.python_exists = Test-Path $py
$pre.gpu_free_mb = Get-FreeVramMb
$pre.ram_free_gb = [math]::Round((Get-FreeGb), 1)
$pre.disk_free_gb = [math]::Round((Get-PSDrive D).Free / 1GB, 1)
$pre.canonical_default = Test-Path (Join-Path $repo 'outputs\dynamic_fusion\unified_fusion_paper_support_20260913\canonical')
$pre.canonical_generalization = Test-Path (Join-Path $gen 'canonical')
$pre.btad03_all_seeds = $true
for ($seed = 0; $seed -lt 8; $seed++) {
    if (-not (Test-Path (Join-Path $repo ("outputs\dynamic_fusion\unified_fusion_paper_support_20260913\canonical\B\btad_s{0}_k8\03.npz" -f $seed)))) {
        $pre.btad03_all_seeds = $false
    }
}
$pre.swin_weights_cached = @(Get-ChildItem (Join-Path $env:USERPROFILE '.cache\huggingface\hub\models--timm--swin_tiny_patch4_window7_224.ms_in1k\snapshots') -Recurse -Filter 'model.safetensors' -ErrorAction SilentlyContinue).Count -gt 0
$pre.visa_done_before = Count-Done (Join-Path $gen 'p1_matrix') 'visa_s'
$pre.btad03_done_before = Count-CategoryDone (Join-Path $sub 'p1_matrix_btad') 'btad' '03'
"[night] preflight: $($pre | ConvertTo-Json -Compress)" | Add-Content (Join-Path $out 'logs_night.txt')

$usable = -not (-not $pre.python_exists -or $pre.gpu_free_mb -lt 0 -or $pre.disk_free_gb -lt 20 -or
    -not $pre.canonical_default -or -not $pre.canonical_generalization -or
    -not $pre.btad03_all_seeds -or -not $pre.swin_weights_cached)

if ($PreflightOnly) {
    # Validation mode reports what phase 0 sees and starts nothing.  It is deliberately
    # side-effect-free: it takes no lock and writes no status file, because both belong to a real
    # run and a stale record with finished = null would make night_watch report a phantom run.
    $pre | ConvertTo-Json | Write-Output
    if ($usable) { exit 0 }
    "preflight says the environment is not usable; a real run would refuse to start" | Write-Output
    exit 1
}

if (-not $usable) {
    Set-Phase 'preflight' 'FAILED' 'environment not usable; nothing was started' $pre
    $script:state.finished = (Get-Date -Format s)
    $script:state | ConvertTo-Json -Depth 8 | Set-Content -LiteralPath $statusPath -Encoding utf8
    Remove-Item -LiteralPath $lockPath -ErrorAction SilentlyContinue
    exit 1
}
Set-Phase 'preflight' 'pass' 'environment ok' $pre


# the machine must not fall asleep while the box is unattended.  This cannot override a "close the
# lid and sleep" power policy, which is the one thing the operator has to check by hand.
Add-Type -TypeDefinition @'
using System;
using System.Runtime.InteropServices;
public static class NightPowerRequest {
    [DllImport("kernel32.dll", SetLastError=true)]
    public static extern uint SetThreadExecutionState(uint flags);
}
'@
[void][NightPowerRequest]::SetThreadExecutionState([uint32]2147483649)
"[night] keep-awake armed for the lifetime of this process" | Add-Content (Join-Path $out 'logs_night.txt')

# ------------------------------------------------------------------ phase 1: VisA matrix
$visaLog = Get-Log 'visa'
$visaStart = Get-Date
$visaBefore = Count-Done (Join-Path $gen 'p1_matrix') 'visa_s'
$statusFile = Join-Path $gen 'p1_matrix\STATUS.json'
$visaStatus = 'unknown'
if (Test-Path $statusFile) { $visaStatus = (Read-Json $statusFile).state }
if ($visaBefore -ge 144 -and $visaStatus -eq 'completed') {
    Set-Phase 'visa_matrix' 'skipped_already_done' "144/144 units, STATUS=completed" `
        ([ordered]@{ before = $visaBefore; after = $visaBefore; state = $visaStatus })
} else {
    $dispatcherLog = Join-Path $gen 'log_matrix_visa_parallel.txt'
    $disp = Start-Process powershell -ArgumentList '-NoProfile', '-ExecutionPolicy', 'Bypass', '-File',
        (Join-Path $closure 'run_visa_parallel.ps1'), '-Concurrency', "$VisAConcurrency", '-Device',
        'cuda', '-Python', $py -WindowStyle Hidden -PassThru
    # Supervised, not just awaited: the dispatcher loops forever on its own queue, so a single hung
    # unit process would otherwise cost the whole night.  A stall is "no new DONE.json for
    # VisAStallMinutes while the log is not reporting throttling"; a throttled dispatcher is healthy
    # and must not be killed.  The hard cap bounds the phase even if the stall test never fires.
    $hardCap = (Get-Date).AddMinutes($VisAHardCapMinutes)
    $lastCount = $visaBefore
    $idleSince = Get-Date
    $stalled = $false
    while (-not $disp.HasExited) {
        Start-Sleep -Seconds 60
        $now = Count-Done (Join-Path $gen 'p1_matrix') 'visa_s'
        $lastLine = ''
        if (Test-Path $dispatcherLog) {
            $lastLine = ((Get-Content $dispatcherLog -Tail 1 -ErrorAction SilentlyContinue) -join ' ')
        }
        if ($now -gt $lastCount) { $lastCount = $now; $idleSince = Get-Date }
        elseif ($lastLine -match 'throttled') { $idleSince = Get-Date }
        if ($now -lt 144 -and ((Get-Date) - $idleSince).TotalMinutes -gt $VisAStallMinutes) {
            $stalled = $true
            "[night] visa dispatcher stalled: $now/144 and no new unit for $VisAStallMinutes min" |
                Add-Content (Join-Path $out 'logs_night.txt')
            break
        }
        if ((Get-Date) -gt $hardCap) {
            $stalled = $true
            "[night] visa dispatcher hit the $VisAHardCapMinutes min cap at $now/144" |
                Add-Content (Join-Path $out 'logs_night.txt')
            break
        }
        if ((Get-Date) -gt $deadline) { break }
    }
    if ($stalled) {
        # units are independent and the queue is rebuilt from the DONE.json files, so stopping here
        # only loses the in-flight units; a relaunch resumes instead of recomputing
        Get-Process python -ErrorAction SilentlyContinue | Stop-Process -Force -ErrorAction SilentlyContinue
        Stop-Process -Id $disp.Id -Force -ErrorAction SilentlyContinue
    }
    $visaAfter = Count-Done (Join-Path $gen 'p1_matrix') 'visa_s'
    if (Test-Path $statusFile) { $visaStatus = (Read-Json $statusFile).state }
    if ($visaAfter -ge 144 -and $visaStatus -ne 'completed') {
        # the dispatcher's closing `run_matrix --resume` is what writes STATUS.json = completed, and
        # the analysis chain's phase 0 waits for exactly that; re-running it here is idempotent and
        # is the difference between a chain that starts now and one that idles for its stall window
        $env:FUSION_CANONICAL_ROOT = Join-Path $gen 'canonical'
        & $py -u (Join-Path $scripts 'run_matrix.py') --output (Join-Path $gen 'p1_matrix') `
            --datasets mvtec visa --seeds 0 1 2 --shots 1 2 4 8 --device cuda --resume *>> $visaLog
        Remove-Item Env:FUSION_CANONICAL_ROOT -ErrorAction SilentlyContinue
        if (Test-Path $statusFile) { $visaStatus = (Read-Json $statusFile).state }
    }
    if ($visaAfter -ge 144) {
        Set-Phase 'visa_matrix' 'pass' "144/144 units, STATUS=$visaStatus" `
            ([ordered]@{ before = $visaBefore; after = $visaAfter; state = $visaStatus
                         minutes = [int]((Get-Date) - $visaStart).TotalMinutes; log = $visaLog })
    } else {
        Set-Phase 'visa_matrix' 'needs_attention' "only $visaAfter/144 units; see $visaLog" `
            ([ordered]@{ before = $visaBefore; after = $visaAfter; state = $visaStatus; stalled = $stalled })
    }
}

# ------------------------------------------------------------------ phase 2: analysis chain (background)
# The chain may only start on a COMPLETE VisA matrix.  run_analysis.ps1 is written to proceed after
# its stall window even if the batch never finished, which is right for an interactive session but
# wrong here: it would compute the MVTec/VisA statistics and the C5 interaction table on a partial
# dataset and report success.  Those tables feed the paper, so a partial matrix must stop the chain
# rather than quietly shrink it.
$chainMarker = Join-Path $sub 'ANALYSIS_CHAIN.json'
$visaResult = $script:state.phases['visa_matrix'].result
if ($visaResult -ne 'pass' -and $visaResult -ne 'skipped_already_done') {
    Set-Phase 'analysis_chain' 'skipped' "VisA matrix is $visaResult; the chain is not started on a partial dataset"
} elseif (Test-Path $chainMarker) {
    Set-Phase 'analysis_chain' 'skipped_already_done' 'ANALYSIS_CHAIN.json already present'
    $script:chainStarted = $null
} else {
    $script:chainStarted = Start-Process powershell -ArgumentList '-NoProfile', '-ExecutionPolicy',
        'Bypass', '-File', (Join-Path $closure 'run_analysis.ps1') -WindowStyle Hidden -PassThru
    Set-Phase 'analysis_chain' 'started' "pid $($script:chainStarted.Id); waits for the VisA batch itself, then d2b + fullpixel + stats + conditions + c5"
}

# ------------------------------------------------------------------ phase 3: BTAD-03 matrix
$btadDone = Count-CategoryDone (Join-Path $sub 'p1_matrix_btad') 'btad' '03'
if ($SkipG) {
    Set-Phase 'btad03_matrix' 'skipped' 'SkipG'
} elseif ($btadDone -ge 32) {
    Set-Phase 'btad03_matrix' 'skipped_already_done' "$btadDone/32 units already present"
} else {
    $btadLog = Get-Log 'btad03'
    $btadStart = Get-Date
    Remove-Item Env:FUSION_CANONICAL_ROOT -ErrorAction SilentlyContinue
    & $py -u (Join-Path $scripts 'run_matrix.py') `
        --output (Join-Path $sub 'p1_matrix_btad') --datasets btad --categories 03 `
        --seeds 0 1 2 3 4 5 6 7 --shots 1 2 4 8 --branches B S C `
        --device cuda --chunk 256 --stride 8 --resume `
        --code-amendment-reason 'workflow G: add BTAD-03 so the cross-seed variance covers three categories' *>> $btadLog
    $btadDone = Count-CategoryDone (Join-Path $sub 'p1_matrix_btad') 'btad' '03'
    if ($btadDone -ge 32) {
        Set-Phase 'btad03_matrix' 'pass' "$btadDone/32 units" `
            ([ordered]@{ before = $pre.btad03_done_before; after = $btadDone;
                         minutes = [int]((Get-Date) - $btadStart).TotalMinutes; log = $btadLog })
    } else {
        Set-Phase 'btad03_matrix' 'FAILED' "only $btadDone/32 units; see $btadLog" `
            ([ordered]@{ before = $pre.btad03_done_before; after = $btadDone })
    }
}

# ------------------------------------------------------------------ phase 4: Swin-T (E3) + S10
# deliberately before the chain wait: E3 needs only the GPU, which is free again after phase 3
if ($SkipSwinT) {
    Set-Phase 'swin_t' 'skipped' 'SkipSwinT'
} else {
    $e3Log = Get-Log 'e3'
    $e3Summary = Join-Path $new '05_extra_encoders\E3\E3_SUMMARY.json'
    $e3Verify = Join-Path $new '05_extra_encoders\E3\VERIFICATION.json'
    $gate = Read-Json $e3Verify
    if ((Test-Path $e3Summary) -and $gate -and $gate.VE_2_single_branch_auroc.pass) {
        Set-Phase 'swin_t' 'skipped_already_done' 'E3 artefacts already present and VE.2 passed'
    } else {
        $env:HF_HUB_OFFLINE = '1'
        & $py -u (Join-Path $repo 'scripts\representation_matching_interaction_20260914\s4_extra_encoders.py') `
            --branch E3 --device cuda --workers 4 --skip-existing *>> $e3Log
        Remove-Item Env:HF_HUB_OFFLINE -ErrorAction SilentlyContinue
        $gate = Read-Json $e3Verify
        if ((Test-Path $e3Summary) -and $gate -and $gate.VE_2_single_branch_auroc.pass) {
            Set-Phase 'swin_t' 'pass' "E3 encoded, VE.2 min AUROC $($gate.VE_2_single_branch_auroc.min_auroc)" `
                ([ordered]@{ log = $e3Log; summary = $e3Summary })
        } else {
            Set-Phase 'swin_t' 'FAILED' "E3 artefact or VE.2 gate missing; see $e3Log" `
                ([ordered]@{ log = $e3Log
                             gate_pass = ($gate -and $gate.VE_2_single_branch_auroc.pass) })
        }
    }
    # the five-encoder table is cheap and is what the paper quotes, so it is refreshed whenever E3
    # exists, even if this run skipped re-encoding
    if (Test-Path $e3Summary) {
        & $py -u (Join-Path $repo 'scripts\representation_matching_interaction_20260914\s10_encoder_comparison.py') *>> $e3Log
        $s10 = Join-Path $new '05_extra_encoders\S10_SUMMARY.json'
        if (Test-Path $s10) {
            $script:state.phases['swin_t'].s10 = $s10
            $script:state | ConvertTo-Json -Depth 8 | Set-Content -LiteralPath $statusPath -Encoding utf8
        } else {
            "[night] s10 did not write its summary; see $e3Log" | Add-Content (Join-Path $out 'logs_night.txt')
        }
    }
}

# ------------------------------------------------------------------ phase 5: bounded chain wait
# This is the only phase that waits on the analysis chain, and it never blocks anything else: the
# wait is capped by -ChainWaitMaxMinutes and by the overall deadline, and it records a timeout as
# a result rather than throwing.
$chainLog = Join-Path $sub 'logs_analysis.txt'
$chainResult = $script:state.phases['analysis_chain'].result
if ($chainResult -eq 'skipped' -or $chainResult -eq 'skipped_already_done') {
    # nothing to wait for: either the chain was never started, or its marker is already on disk
} else {
    $waitStop = (Get-Date).AddMinutes($ChainWaitMaxMinutes)
    while (-not (Test-Path $chainMarker) -and (Get-Date) -lt $waitStop -and (Get-Date) -lt $deadline) {
        Start-Sleep -Seconds 60
    }
}
if (Test-Path $chainMarker) {
    $chainReport = Read-Json $chainMarker
    $steps = @($chainReport.steps)
    $bad = @($steps | Where-Object { $_.exit_code -ne 0 })
    Set-Phase 'analysis_chain' $(if ($bad.Count -eq 0) { 'pass' } else { 'needs_attention' }) `
        "$($steps.Count) steps, $($bad.Count) with a non-zero exit code" `
        ([ordered]@{ steps = $steps })
} else {
    # not a failure of this driver: the chain is a background process whose partial results are
    # still usable, and d3 does not depend on it
    Set-Phase 'analysis_chain' 'needs_attention' `
        "no ANALYSIS_CHAIN.json after $ChainWaitMaxMinutes min (cap) or the deadline; chain log tail: $((Get-Content $chainLog -Tail 1 -ErrorAction SilentlyContinue) -join ' ')"
}

# if the chain never started because the VisA matrix was incomplete, say so in the status file
if (-not (Test-Path $chainMarker) -and $chainResult -eq 'skipped') {
    Set-Phase 'analysis_chain' 'skipped' "VisA matrix was incomplete, so the chain was never started"
}

# ------------------------------------------------------------------ phase 6: d3 support-set variance
$d3Log = Get-Log 'd3'
$d3Out = Join-Path $sub 'interaction_seed_variance.json'
$btadDone = Count-CategoryDone (Join-Path $sub 'p1_matrix_btad') 'btad' '03'
if ($SkipG -or $btadDone -lt 32) {
    Set-Phase 'd3_seed_variance' 'skipped' "BTAD-03 matrix incomplete ($btadDone/32); d3 needs all three categories"
} elseif ((Get-Date) -gt $deadline) {
    Set-Phase 'd3_seed_variance' 'skipped' 'past the deadline'
} else {
    $d3Start = Get-Date
    & $py -u (Join-Path $closure 'd3_seed_variance.py') *>> $d3Log
    if (Test-Path $d3Out) {
        $report = Read-Json $d3Out
        $btadKeys = @($report.VD_4_variance.PSObject.Properties.Name | Where-Object { $_ -like 'btad|*' })
        $reg = $report.VD_3_regression.btad
        Set-Phase 'd3_seed_variance' 'pass' "wrote $d3Out (btad blocks: $($btadKeys.Count))" `
            ([ordered]@{ minutes = [int]((Get-Date) - $d3Start).TotalMinutes; log = $d3Log
                         vd3_btad_n_compared = $reg.n_compared
                         vd3_btad_max_abs_delta = $reg.max_abs_delta
                         vd3_btad_within_1e_9 = $reg.tolerance_1e_9 })
    } else {
        Set-Phase 'd3_seed_variance' 'FAILED' "no $d3Out; see $d3Log"
    }
}

# ------------------------------------------------------------------ phase 7: close-out
# NOTE: this file is deliberately ASCII-only.  Windows PowerShell 5.1 decodes a .ps1 as ANSI
# (GBK here) unless it has a UTF-8 BOM, so any non-ASCII literal would corrupt the parse - that is
# exactly how the first version of this script failed to load.  The Chinese report is rendered by
# night_report.py, which Python reads as UTF-8.
$checks = [ordered]@{
    'C  visa units'                    = "{0}/144" -f (Count-Done (Join-Path $gen 'p1_matrix') 'visa_s')
    'G  btad-03 units'                 = "{0}/32" -f (Count-CategoryDone (Join-Path $sub 'p1_matrix_btad') 'btad' '03')
    'C  p1_statistics'                 = Test-Path (Join-Path $gen 'p1_statistics\bootstrap_samples.npz')
    'C  p4_fullpixel'                  = Test-Path (Join-Path $gen 'p4_fullpixel\fullpixel_metrics.csv')
    'C  p2_conditions'                 = Test-Path (Join-Path $gen 'p2_conditions')
    'C  C5_SUMMARY.json'               = Test-Path (Join-Path $gen 'C5_SUMMARY.json')
    'D  d3 interaction_by_seed.csv'    = Test-Path (Join-Path $sub 'interaction_by_seed.csv')
    'D  d3 interaction_seed_variance'  = Test-Path $d3Out
    'E3 E3_SUMMARY.json'               = Test-Path (Join-Path $new '05_extra_encoders\E3\E3_SUMMARY.json')
    'E  S10 five-encoder table'        = Test-Path (Join-Path $new '05_extra_encoders\S10_SUMMARY.json')
}
$report = Join-Path $out 'NIGHT_RUN_REPORT_CN.md'

$script:state.finished = (Get-Date -Format s)
$script:state.checks = $checks
$script:state.report = $report
$script:state | ConvertTo-Json -Depth 8 | Set-Content -LiteralPath $statusPath -Encoding utf8

& $py -u (Join-Path $closure 'night_report.py') --status $statusPath --out $report *>> (Join-Path $out 'logs_night.txt')
[void][NightPowerRequest]::SetThreadExecutionState([uint32]2147483648)
Remove-Item -LiteralPath $lockPath -ErrorAction SilentlyContinue
"[night] all phases done; report in $report" | Add-Content (Join-Path $out 'logs_night.txt')
exit 0
