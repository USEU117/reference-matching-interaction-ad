# Export slide 1 of the editable Figure 1 master to the current manuscript figure directory.
# Migrated from `.tmp_figure_revision_20260920/export_pptx.ps1` on 2026-09-23: paths are now
# repository-relative and the output defaults to the live figure directory.
param(
  [string]$DeckPath,
  [string]$OutPath,
  [int]$Slide = 1,
  [int]$Width = 2560,
  [int]$Height = 2120
)
$root = (Resolve-Path (Join-Path $PSScriptRoot '../..')).Path
if (-not $DeckPath) { $DeckPath = Join-Path $root 'docs/main_figure_revision_20260920/Main_Figure_Editable_Final_20260925.pptx' }
if (-not $OutPath)  { $OutPath  = Join-Path $root 'docs/paper_complete_review_20260920/figures/fig1_framework.png' }
$dir = Split-Path -Parent $OutPath
if (-not (Test-Path $dir)) { New-Item -ItemType Directory -Path $dir -Force | Out-Null }
$app = New-Object -ComObject PowerPoint.Application
try {
  $presentation = $app.Presentations.Open($DeckPath, $true, $false, $false)
  $presentation.Slides.Item($Slide).Export($OutPath, 'PNG', $Width, $Height)
  $presentation.Close()
  Write-Output $OutPath
} finally { $app.Quit() }
