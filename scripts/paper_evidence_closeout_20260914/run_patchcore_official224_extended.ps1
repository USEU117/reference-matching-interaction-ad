<#
.SYNOPSIS
  Batch driver for the PatchCore "official224" baseline, extended to MVTec (15 classes)
  and VisA (12 classes) on top of the original MPDD (6) + BTAD (3).

.DESCRIPTION
  Thin orchestrator around scripts/paper_evidence_closeout_20260914/run_baseline_patchcore.py
  (the script that produced experiments/.../05_baselines/patchcore_official224/).  It runs
  ONE unit per process (unit = <dataset>_s<seed>_k<shot>), so a crash or Ctrl-C only loses
  the current unit, and re-running the same command resumes: --skip-existing is honoured
  per unit and only skips units that already cover every category of their dataset.

  Exact per-unit protocol (unchanged; see patchcore_state_official224.json for the original
  recorded command lines):
    .venv-patchcore\Scripts\python.exe bin/run_patchcore.py --gpu 0 --seed <seed>
      --dump_predictions --log_group <dataset>_s<seed>_k<shot>
      --log_project <dataset>_official224 outputs\patchcore\closeout_official224
      patch_core -b wideresnet50 -le layer2 -le layer3
      --pretrain_embed_dimension 1024 --target_embed_dimension 1024
      --anomaly_scorer_num_nn 1 --patchsize 3 --faiss_num_workers 1
      sampler -p 0.1 approx_greedy_coreset dataset --resize 256 --imagesize 224
      --batch_size 1 --num_workers 0 -d <cat> [-d <cat> ...]
      mvtec data\patchcore_closeout\<dataset>_s<seed>_k<shot>
    followed by scripts\evaluate_unified.py --apro-steps 200 --include-categories mvtec_<cat>...

.PARAMETER Datasets
  Subset of mpdd, btad, mvtec, visa.  Default: mvtec, visa.

.PARAMETER Categories
  Optional subset of categories (applies to every dataset in -Datasets).  WARNING: a
  restricted run rewrites that unit's per_category/per_image/summary to cover only those
  categories, so use a dedicated -Out for partial-category batches.

.PARAMETER Seeds / Shots
  Few-shot conditions.  Default 0,1 and 1,4 (the S4 protocol).

.PARAMETER Out
  Results root that holds patchcore_official224\, logs\, patchcore_state_official224.json
  and patchcore_failures_official224.json.

.EXAMPLE
  # What does the driver cover, and what is already finished?
  .\scripts\paper_evidence_closeout_20260914\run_patchcore_official224_extended.ps1 -List

.EXAMPLE
  # Full MVTec + VisA matrix, resumable, into the canonical S4 baseline folder.
  .\scripts\paper_evidence_closeout_20260914\run_patchcore_official224_extended.ps1 -SkipExisting

.EXAMPLE
  # One category, one condition, into a scratch folder (smoke test).
  .\scripts\paper_evidence_closeout_20260914\run_patchcore_official224_extended.ps1 `
      -Datasets mvtec -Categories bottle -Seeds 0 -Shots 1 -SkipExisting `
      -Out experiments\dynamic_fusion\representation_matching_interaction_20260914\_smoke
#>
param(
    [string[]]$Datasets = @('mvtec', 'visa'),
    [string[]]$Categories = @(),
    [int[]]$Seeds = @(0, 1),
    [int[]]$Shots = @(1, 4),
    [string]$Out = 'experiments\dynamic_fusion\representation_matching_interaction_20260914\05_baselines',
    [switch]$SkipExisting,
    [switch]$List,
    [switch]$DryRun
)

$ErrorActionPreference = 'Stop'
$Root = (Resolve-Path (Join-Path $PSScriptRoot '..\..')).Path
$Python = Join-Path $Root '.venv-anomalyclip\Scripts\python.exe'
$Wrapper = Join-Path $Root 'scripts\paper_evidence_closeout_20260914\run_baseline_patchcore.py'
$OutPath = if ([System.IO.Path]::IsPathRooted($Out)) { $Out } else { Join-Path $Root $Out }

# `-Datasets mvtec,visa` binds as one array in-session but as the single string "mvtec,visa"
# when the script is started with `powershell -File`; accept both spellings.
function Expand-List([string[]]$Values) {
    return @($Values | ForEach-Object { $_ -split ',' } | Where-Object { $_ -ne '' } | ForEach-Object { $_.Trim() })
}
$Datasets = Expand-List $Datasets
$Categories = Expand-List $Categories

if (-not (Test-Path -LiteralPath $Python)) { throw "missing interpreter: $Python" }
if (-not (Test-Path -LiteralPath $Wrapper)) { throw "missing wrapper: $Wrapper" }

$listArgs = @($Wrapper, '--out', $OutPath, '--config', 'official224',
              '--datasets') + $Datasets + @('--seeds') + $Seeds + @('--shots') + $Shots + @('--list')
if ($Categories.Count -gt 0) { $listArgs += @('--categories') + $Categories }
& $Python @listArgs
if ($LASTEXITCODE -ne 0) { throw "inventory failed (exit $LASTEXITCODE)" }
if ($List) { return }

# Unit list ---------------------------------------------------------------
$units = @()
foreach ($dataset in $Datasets) {
    foreach ($seed in $Seeds) {
        foreach ($shot in $Shots) {
            $units += [pscustomobject]@{ Dataset = $dataset; Seed = $seed; Shot = $shot
                                         Unit = "${dataset}_s${seed}_k${shot}" }
        }
    }
}
Write-Host "[driver] $($units.Count) units for datasets $($Datasets -join ', '): $($units.Unit -join ', ')"
if ($DryRun) { return }

# Run --------------------------------------------------------------------
$failed = @()
foreach ($u in $units) {
    $summary = Join-Path $OutPath "patchcore_official224\$($u.Unit)\per_category.csv"
    if ($SkipExisting -and (Test-Path -LiteralPath $summary)) {
        Write-Host "[driver] $($u.Unit) already has per_category.csv; the wrapper re-checks full coverage" -ForegroundColor DarkGray
    }
    $callArgs = @($Wrapper, '--out', $OutPath, '--config', 'official224',
                  '--datasets', $u.Dataset, '--only-unit', $u.Unit,
                  '--seeds', $u.Seed, '--shots', $u.Shot)
    if ($Categories.Count -gt 0) { $callArgs += @('--categories') + $Categories }
    if ($SkipExisting) { $callArgs += '--skip-existing' }
    & $Python @callArgs
    if ($LASTEXITCODE -ne 0) {
        Write-Host "[driver] $($u.Unit) FAILED (exit $LASTEXITCODE)" -ForegroundColor Red
        $failed += $u.Unit
    }
}

# Summary ----------------------------------------------------------------
Write-Host ''
Write-Host '[driver] result inventory'
foreach ($u in $units) {
    $dir = Join-Path $OutPath "patchcore_official224\$($u.Unit)"
    $rows = 0
    if (Test-Path -LiteralPath (Join-Path $dir 'per_category.csv')) {
        $rows = (Import-Csv -LiteralPath (Join-Path $dir 'per_category.csv')).Count
    }
    $flag = if ($failed -contains $u.Unit) { 'FAILED' } elseif ($rows -gt 0) { 'ok' } else { 'missing' }
    Write-Host ("  {0,-14} per_category rows = {1,-3} {2}" -f $u.Unit, $rows, $flag)
}
Write-Host "[driver] failures file: $(Join-Path $OutPath 'patchcore_failures_official224.json')"
if ($failed.Count -gt 0) { exit 1 }
