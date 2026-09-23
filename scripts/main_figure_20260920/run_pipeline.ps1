# Figure 1 (framework) end-to-end reproduction chain.
# Migrated into version control on 2026-09-23 (previously the whole chain lived in the gitignored
# `.tmp_figure_revision_20260920/` scratch directory).
#
# Prerequisites (all external to this repository):
#   * node (tested with v20.19.0)
#   * @oai/artifact-tool runtime  -> override with $env:ARTIFACT_TOOL
#   * the presentation skill cache (artifact_tool_utils.mjs) -> override with $env:PRESENTATION_SKILL
#   * Microsoft PowerPoint (COM) for the final 2560x2120 raster export
#   * Python with lxml (defaults to .venv-anomalyclip)
#
# Usage:
#   powershell -File scripts/main_figure_20260920/run_pipeline.ps1
#   powershell -File scripts/main_figure_20260920/run_pipeline.ps1 -SkipFinalize -OutPath <png>
param(
  [string]$Python,
  [string]$OutPath,
  [string]$Scratch,
  [switch]$SkipFinalize
)
$ErrorActionPreference = 'Stop'
$root = (Resolve-Path (Join-Path $PSScriptRoot '../..')).Path
if (-not $Python)  { $Python  = Join-Path $root '.venv-anomalyclip/Scripts/python.exe' }
if (-not $Scratch) { $Scratch = Join-Path $root '.tmp_figure_revision_20260920' }
$env:FIG1_SCRATCH = $Scratch

Write-Output '[1/4] build_main.mjs (native editable candidate)'
node (Join-Path $PSScriptRoot 'build_main.mjs')

Write-Output '[2/4] patch_math.py (native sub/superscript baselines)'
& $Python (Join-Path $PSScriptRoot 'patch_math.py')

if (-not $SkipFinalize) {
  Write-Output '[3/4] finalize_figure.mjs (editable master)'
  node (Join-Path $PSScriptRoot 'finalize_figure.mjs')
} else {
  Write-Output '[3/4] finalize_figure.mjs skipped'
}

Write-Output '[4/4] export_slide.ps1 (PowerPoint COM raster)'
& (Join-Path $PSScriptRoot 'export_slide.ps1') -OutPath $OutPath
