$taskRoot=(Resolve-Path (Join-Path $PSScriptRoot '../..')).Path
$taskOut=Join-Path $taskRoot '.tmp_revision_20260925/slides'
New-Item -ItemType Directory -Force -Path $taskOut | Out-Null
$taskApp=New-Object -ComObject PowerPoint.Application
try {
 $taskDeck=$taskApp.Presentations.Open((Join-Path $taskRoot 'docs/paper_complete_review_20260920/All_Figures_Complete_20260925.pptx'),$true,$false,$false)
 for($i=1;$i -le $taskDeck.Slides.Count;$i++){
   $taskDeck.Slides.Item($i).Export((Join-Path $taskOut ('slide-'+$i+'.png')),'PNG',1600,1325)
 }
 $taskDeck.Close()
 Write-Output 'Exported current deck in native PowerPoint'
} finally {$taskApp.Quit()}
