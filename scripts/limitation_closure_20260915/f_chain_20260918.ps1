# F confirmation-set chain (KolektorSDD2), steps 3-9 of night-run phase 2.
#
# Why this exists: the night run's phase 2 has fail-fast guards.  `export_k8_B` failed once
# on a transient torch.hub network hiccup (RemoteDisconnected) while validating the cached
# DINOv2 repo; the branch was re-exported successfully by hand afterwards, but the guard had
# already skipped `run_matrix` and everything chained behind it.  The three canonical caches
# are now complete, so this driver runs the remaining steps in the same order and with the
# same arguments the orchestrator would have used.  Pure ASCII on purpose: Windows
# PowerShell 5.1 decodes BOM-less .ps1 as GBK and would mangle non-ASCII text.

$ErrorActionPreference = 'Continue'
$root  = 'D:\STUDY\My_github\sci_project'
$F     = Join-Path $root 'experiments\dynamic_fusion\confirmation_ksdd2_20260918'
$night = Join-Path $root 'scripts\limitation_closure_20260915\_night2_20260918'
$py    = Join-Path $root '.venv-anomalyclip\Scripts\python.exe'
$scripts = Join-Path $root 'scripts\unified_fusion_paper_support_v1'
$rep   = Join-Path $root 'scripts\representation_matching_interaction_20260914'

$env:FUSION_CANONICAL_ROOT = Join-Path $F 'canonical'
$statusFile = Join-Path $night 'fchain_status.txt'

function Log([string]$msg) {
    $line = "{0} {1}" -f (Get-Date -Format 'yyyy-MM-dd HH:mm:ss'), $msg
    Add-Content -LiteralPath $statusFile -Value $line -Encoding utf8
    Write-Host $line
}

function Invoke-FStep([string]$id, [string[]]$stepArgs) {
    $log = Join-Path $night "fchain_$id.log"
    $err = Join-Path $night "fchain_$id.err"
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

Log "chain start (canonical root $env:FUSION_CANONICAL_ROOT)"

# 3. the 12-unit matrix, strictly serial
$code = Invoke-FStep 'run_matrix' @('-u', (Join-Path $scripts 'run_matrix.py'),
    '--datasets', 'ksdd2', '--seeds', '0', '1', '2', '--shots', '1', '2', '4', '8',
    '--device', 'cuda', '--output', (Join-Path $F 'p1_matrix'), '--resume')
if ($code -ne 0) { Log 'chain stopped: run_matrix failed'; exit 1 }

# 4. full-pixel metrics, single process
$code = Invoke-FStep 'run_fullpixel' @('-u', (Join-Path $scripts 'run_fullpixel.py'),
    '--run-root', (Join-Path $F 'p1_matrix'), '--output', (Join-Path $F 'p4_fullpixel'),
    '--datasets', 'ksdd2', '--seeds', '0', '1', '2', '--shots', '1', '2', '4', '8', '--resume')
if ($code -ne 0) { Log 'chain stopped: run_fullpixel failed'; exit 1 }

# 5. bootstrap statistics on the fast path
$code = Invoke-FStep 'stats_v2' @('-u', (Join-Path $scripts 'stats_v2.py'),
    '--run-root', (Join-Path $F 'p1_matrix'), '--output', (Join-Path $F 'p1_statistics'),
    '--datasets', 'ksdd2', '--seeds', '0', '1', '2', '--shots', '1', '2', '4', '8',
    '--workers', '4', '--fast-replicates')
if ($code -ne 0) { Log 'chain stopped: stats_v2 failed'; exit 1 }

# 6. interaction aggregates
$code = Invoke-FStep 's1_interaction' @('-u', (Join-Path $rep 's1_interaction.py'),
    '--study-root', $F, '--output', (Join-Path $F '02_interaction'))
if ($code -ne 0) { Log 'chain stopped: s1_interaction failed'; exit 1 }

# 7. robustness / K curve / per-category
$code = Invoke-FStep 's2_robustness' @('-u', (Join-Path $rep 's2_robustness.py'),
    '--study-root', $F, '--interaction-root', $F, '--output', (Join-Path $F '03_robustness'))
if ($code -ne 0) { Log 'chain stopped: s2_robustness failed'; exit 1 }

# 8. the D branch (WideResNet50-2) with support-aware encoding
$code = Invoke-FStep 's3_new_encoder' @('-u', (Join-Path $rep 's3_new_encoder.py'),
    '--datasets', 'ksdd2', '--seeds', '0', '1', '2', '--shots', '1', '2', '4', '8',
    '--device', 'cuda', '--out', (Join-Path $F '04_new_encoder'),
    '--support-dir', (Join-Path $F 'p0_support'),
    '--study-statistics', (Join-Path $F 'p1_statistics\bootstrap_samples.npz'),
    '--workers', '4', '--fast-replicates')
if ($code -ne 0) { Log 'chain stopped: s3_new_encoder failed'; exit 1 }

# 9. condition-level tables
$code = Invoke-FStep 'analyze_conditions' @('-u', (Join-Path $scripts 'analyze_conditions.py'),
    '--matrix', (Join-Path $F 'p1_matrix'), '--statistics', (Join-Path $F 'p1_statistics'),
    '--output', (Join-Path $F 'p2_conditions'))
if ($code -ne 0) { Log 'chain stopped: analyze_conditions failed'; exit 1 }

Log 'chain complete: all seven steps exit=0'
exit 0
