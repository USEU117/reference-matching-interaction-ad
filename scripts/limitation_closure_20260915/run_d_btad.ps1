# Completes the BTAD arm of the seed 0..7 matrix.
#
# The frozen BTAD canonical cache only ever carried seeds 0 and 1: the support manifest lists seed
# 2, but `btad_s2_k8` was never exported, so `run_matrix.py` died on a missing B npz.  This driver
# first exports seed 2 from the study's own frozen manifest (so seed 2 sits in exactly the same
# geometry and support convention as seeds 0/1, and is NOT given the shared seed-3 query block),
# then resumes the BTAD matrix, which skips the units that already have DONE.json.
#
# Launched detached with Start-Process, so no terminal churn can kill it.

$ErrorActionPreference = 'Continue'
$repo = (Resolve-Path (Join-Path $PSScriptRoot '..\..')).Path
$py = Join-Path $repo '.venv-anomalyclip\Scripts\python.exe'
$ex = Join-Path $repo 'scripts\unified_fusion_paper_support_v1\export_k8_cache.py'
$rm = Join-Path $repo 'scripts\unified_fusion_paper_support_v1\run_matrix.py'
$sub = Join-Path $repo 'experiments\dynamic_fusion\seeds_extension_20260917'
$frozen = Join-Path $repo 'experiments\dynamic_fusion\unified_fusion_paper_support_20260913\p0_support'
$canonical = Join-Path $repo 'outputs\dynamic_fusion\unified_fusion_paper_support_20260913\canonical'
$log = Join-Path $sub 'logs_matrix_btad.txt'

Remove-Item Env:FUSION_CANONICAL_ROOT -ErrorAction SilentlyContinue

"[btad] export seed 2 $(Get-Date -Format s)" | Add-Content $log
foreach ($branch in @('B', 'S', 'C')) {
    & $py -u $ex --dataset btad --branch $branch --seeds 2 --device cuda `
        --output-root $canonical --support-manifest "$frozen\support_manifest_btad.json" *>> $log
}

"[btad] matrix resume $(Get-Date -Format s)" | Add-Content $log
& $py -u $rm --output "$sub\p1_matrix_btad" --datasets btad --categories 01 02 `
    --seeds 0 1 2 3 4 5 6 7 --shots 1 2 4 8 --device cuda --resume *>> $log

"[btad] done $(Get-Date -Format s)" | Add-Content $log
