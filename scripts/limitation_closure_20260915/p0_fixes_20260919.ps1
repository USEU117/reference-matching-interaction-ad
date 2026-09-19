# P0 recomputation driver (2026-09-19): four fixes found by the completeness audit.
#
# 1. s4_extra_encoders re-emits the aggregate rows for reused units, so `new_method_metrics.csv`
#    is complete instead of a 5-byte header.  Both scopes are refreshed so the wide-scope copy is
#    no longer the broken one:
#      a. wide  scope (seed {0,1,2} x K {1,2,4,8}) -> wide_scope/ keeps the labelled secondary
#      b. matched scope (seed {0,1} x K {1,4}, the scope S and D use) -> the default tables, so
#         the shipped S10 numbers agree with its documented scope
# 2. c5_generalization_interactions rebuilds interaction_generalization.csv with an honest
#    `conditions` list (btad uses 8 of the 12 pairs) and the MPDD/BTAD `point_delta_fullpixel`
#    read from the unified-support full-pixel table.
# 3. d3_seed_variance's VD.3 regression gate now compares macro with macro instead of comparing
#    the published dataset macro average against a single category.
#
# Pure ASCII on purpose (Windows PowerShell 5.1 decodes BOM-less .ps1 as GBK).

$ErrorActionPreference = 'Continue'
$root  = 'D:\STUDY\My_github\sci_project'
$night = Join-Path $root 'scripts\limitation_closure_20260915\_night2_20260918'
$py    = Join-Path $root '.venv-anomalyclip\Scripts\python.exe'
$rep   = Join-Path $root 'scripts\representation_matching_interaction_20260914'
$close = Join-Path $root 'scripts\limitation_closure_20260915'
$E     = Join-Path $root 'experiments\dynamic_fusion\representation_matching_interaction_20260914\05_extra_encoders'
$log   = Join-Path $night 'p0_fixes.log'
$statusFile = Join-Path $night 'p0_fixes_status.txt'

function Log([string]$msg) {
    $line = "{0} {1}" -f (Get-Date -Format 'yyyy-MM-dd HH:mm:ss'), $msg
    Add-Content -LiteralPath $statusFile -Value $line -Encoding utf8
    Write-Host $line
}

function Invoke-Step([string]$id, [string[]]$stepArgs) {
    Log "step $id started"
    $global:LASTEXITCODE = 0
    & $py @stepArgs *>> $log
    $code = $LASTEXITCODE
    if ($null -eq $code) { $code = 0 }
    Log "step $id exit=$code"
    return $code
}

function Save-BranchTables([string]$destRoot) {
    foreach ($b in @('E1', 'E2', 'E3')) {
        $dest = Join-Path $destRoot $b
        New-Item -ItemType Directory -Force -Path $dest | Out-Null
        Copy-Item (Join-Path $E "$b\*") -Destination $dest -Include *.csv, *.json, *.npz -Force
    }
}

function Save-S10([string]$dest) {
    New-Item -ItemType Directory -Force -Path $dest | Out-Null
    Copy-Item (Join-Path $E 'S10_SUMMARY.json') -Destination $dest -Force
    foreach ($name in @('encoder_comparison_three.csv', 'encoder_vs_S_difference.csv')) {
        if (Test-Path (Join-Path $E $name)) { Copy-Item (Join-Path $E $name) -Destination $dest -Force }
    }
}

$s4 = Join-Path $rep 's4_extra_encoders.py'
$s10 = Join-Path $rep 's10_encoder_comparison.py'

# ---- 1a. wide scope, refreshed tables (in place), then kept as the labelled secondary
Log 'refreshing the wide-scope branch tables'
foreach ($b in @('E1', 'E2', 'E3')) {
    $c = Invoke-Step "s4_wide_$b" @('-u', $s4, '--branch', $b, '--seeds', '0', '1', '2',
        '--shots', '1', '2', '4', '8', '--device', 'cuda', '--workers', '4', '--skip-existing',
        '--fast-replicates')
    if ($c -ne 0) { Log 'stopped: wide s4 failed'; exit 1 }
}
[void](Invoke-Step 's10_wide' @('-u', $s10))
Save-S10 (Join-Path $E 'wide_scope')
Save-BranchTables (Join-Path $E 'wide_scope')
Log 'wide-scope artifacts refreshed in wide_scope/'

# ---- 1b. matched scope becomes the default
Log 'recomputing the matched-scope (seed {0,1} x K {1,4}) branch tables'
foreach ($b in @('E1', 'E2', 'E3')) {
    $c = Invoke-Step "s4_matched_$b" @('-u', $s4, '--branch', $b, '--seeds', '0', '1',
        '--shots', '1', '4', '--device', 'cuda', '--workers', '4', '--skip-existing',
        '--fast-replicates')
    if ($c -ne 0) { Log 'stopped: matched s4 failed'; exit 1 }
}
[void](Invoke-Step 's10_matched' @('-u', $s10))
Save-S10 (Join-Path $E 'matched_scope')
Save-BranchTables (Join-Path $E 'matched_scope')
Log 'default tables are now the matched scope; copies kept in matched_scope/'

# ---- 2. C5 with the corrected conditions list and point column
$c = Invoke-Step 'c5' @('-u', (Join-Path $close 'c5_generalization_interactions.py'))
if ($c -ne 0) { Log 'stopped: c5 failed'; exit 1 }

# ---- 3. d3 seed variance with the macro-vs-macro VD.3 gate
$cache = Join-Path $close '_night_20260917\_series_cache'
$d3Args = @('-u', (Join-Path $close 'd3_seed_variance.py'))
if (Test-Path $cache) { $d3Args += @('--series-cache', $cache) }
$c = Invoke-Step 'd3' $d3Args
if ($c -ne 0) { Log 'stopped: d3 failed'; exit 1 }

Log 'P0 recomputation done'
exit 0
