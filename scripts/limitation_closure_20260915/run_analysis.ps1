# Runs everything that comes after the matrices, so no stage needs a manual kick.
#
#   phase 0  wait for the VisA matrix batch to stop producing units
#   phase 1  d2b  cross-run query-encoding drift          (workflow D, needs the GPU)
#   phase 2  d3   support-set variance over eight seeds   (workflow D, VD.2/VD.3/VD.4)   [opt-in]
#   phase 3  run_fullpixel + stats_v2 + analyze_conditions for MVTec/VisA (workflow C)
#   phase 4  c5   the four-dataset interaction table      (workflow C, VC.5)
#
# d3 is deliberately NOT part of the default chain: it is a single-threaded 100-minute CPU stage,
# and running it inside the chain idles the GPU-free window and delays phases 3-4.  Run it in
# parallel (or in a first pass) and then launch this file; pass -IncludeD3 only if you really want
# one sequential run.  Either order is safe because d3 and phases 3-4 read different artefacts.
#
# Every phase records its exit code, and a failure does not stop the later phases: a missing
# statistics file is reported as such rather than silently shrinking the table.  The driver writes
# ANALYSIS_CHAIN.json at the end; launch it detached with Start-Process so terminal churn cannot
# kill it.

param([switch]$IncludeD3)

$ErrorActionPreference = 'Continue'
$repo = (Resolve-Path (Join-Path $PSScriptRoot '..\..')).Path
$py = Join-Path $repo '.venv-anomalyclip\Scripts\python.exe'
$sub = Join-Path $repo 'experiments\dynamic_fusion\seeds_extension_20260917'
$gen = Join-Path $repo 'experiments\dynamic_fusion\generalization_mvtec_visa_20260915'
$scripts = Join-Path $repo 'scripts\unified_fusion_paper_support_v1'
$closure = Join-Path $repo 'scripts\limitation_closure_20260915'
$log = Join-Path $sub 'logs_analysis.txt'
$marker = Join-Path $sub 'ANALYSIS_CHAIN.json'

$steps = New-Object System.Collections.ArrayList
function Record-Step([string]$name, [int]$code, [string]$note) {
    [void]$steps.Add(@{ step = $name; exit_code = $code; note = $note;
                        at = (Get-Date -Format s) })
    "[analysis] $name -> exit $code  $note" | Add-Content $log
}

"[analysis] chain start $(Get-Date -Format s)" | Add-Content $log

# ---------------------------------------------------------------- phase 0: wait
$matrix = Join-Path $gen 'p1_matrix'
$deadline = (Get-Date).AddHours(8)
$lastCount = -1
$stallSeconds = 1200
while ((Get-Date) -lt $deadline) {
    $done = @(Get-ChildItem (Join-Path $matrix 'units') -Recurse -Filter 'DONE.json' `
        -ErrorAction SilentlyContinue | Where-Object { $_.FullName -match 'visa_s' })
    $n = $done.Count
    $state = 'unknown'
    $statusPath = Join-Path $matrix 'STATUS.json'
    if (Test-Path $statusPath) { $state = (Get-Content $statusPath -Raw | ConvertFrom-Json).state }
    $newest = if ($n -gt 0) { ($done | Sort-Object LastWriteTime -Descending | Select-Object -First 1).LastWriteTime } else { $null }
    $age = if ($newest) { ((Get-Date) - $newest).TotalSeconds } else { 0 }
    if ($state -eq 'completed') {
        "[analysis] visa matrix completed with $n/144 units" | Add-Content $log
        break
    }
    if ($state -eq 'needs_attention' -or ($age -gt $stallSeconds -and $n -eq $lastCount)) {
        "[analysis] visa matrix stopped: state=$state units=$n idle=$([int]$age)s" | Add-Content $log
        break
    }
    $lastCount = $n
    Start-Sleep -Seconds 60
}

# ---------------------------------------------------------------- phase 1: d2b
& $py -u (Join-Path $closure 'd2b_query_drift.py') --device cuda *>> $log
Record-Step 'd2b_query_drift' $LASTEXITCODE 'cross-run query drift, GPU'

# ---------------------------------------------------------------- phase 2: d3 (opt-in)
if ($IncludeD3) {
    & $py -u (Join-Path $closure 'd3_seed_variance.py') *>> $log
    Record-Step 'd3_seed_variance' $LASTEXITCODE 'support-set variance over seeds 0..7'
} else {
    # the `+` must end the first line: PowerShell treats a complete expression followed by a newline
    # inside parentheses as the end of the statement, which made the whole script fail to parse
    Record-Step 'd3_seed_variance' 0 ('skipped by design; run it separately or in parallel, then ' +
        'add -IncludeD3 to chain it')
}

# ------------------------------------------------- phase 3: generalization statistics
$env:FUSION_CANONICAL_ROOT = Join-Path $gen 'canonical'
& $py -u (Join-Path $scripts 'run_fullpixel.py') --run-root $matrix `
    --output (Join-Path $gen 'p4_fullpixel') --datasets mvtec visa `
    --seeds 0 1 2 --shots 1 2 4 8 --resume *>> $log
Record-Step 'run_fullpixel_mvtec_visa' $LASTEXITCODE 'stride-1 point table'

& $py -u (Join-Path $scripts 'stats_v2.py') --run-root $matrix `
    --output (Join-Path $gen 'p1_statistics') --datasets mvtec visa --seeds 0 1 2 `
    --shots 1 2 4 8 *>> $log
Record-Step 'stats_v2_mvtec_visa' $LASTEXITCODE 'bootstrap samples'

& $py -u (Join-Path $scripts 'analyze_conditions.py') --matrix $matrix `
    --statistics (Join-Path $gen 'p1_statistics') --output (Join-Path $gen 'p2_conditions') *>> $log
Record-Step 'analyze_conditions_mvtec_visa' $LASTEXITCODE 'condition tables'

# ---------------------------------------------------------------- phase 4: c5
& $py -u (Join-Path $closure 'c5_generalization_interactions.py') *>> $log
Record-Step 'c5_generalization_interactions' $LASTEXITCODE 'four-dataset interaction table'

$payload = @{ finished_utc = (Get-Date -Format s); steps = $steps } | ConvertTo-Json -Depth 5
$payload | Set-Content $marker -Encoding utf8
"[analysis] chain done $(Get-Date -Format s)" | Add-Content $log
