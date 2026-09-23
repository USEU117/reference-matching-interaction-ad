$taskRoot = (Resolve-Path (Join-Path $PSScriptRoot '../../..')).Path
$taskTemp = Join-Path $taskRoot '.tmp_revision_20260923'
$taskIndex = Get-Content -LiteralPath (Join-Path $taskRoot 'docs/paper_complete_review_20260920/FIGURE_SLIDE_INDEX.json') -Raw | ConvertFrom-Json
$taskApp = New-Object -ComObject PowerPoint.Application
try {
    $taskDeck = $taskApp.Presentations.Open((Join-Path $taskTemp 'all_images.pptx'), $false, $false, $false)
    foreach ($entry in ($taskIndex | Where-Object { $_.native })) {
        if ($entry.key -eq 'framework') {
            $taskSource = Join-Path $taskRoot 'docs/main_figure_revision_20260920/Main_Figure_Editable_Final_20260920.pptx'
            $taskSourceIndex = 1
        } else {
            $taskSource = Join-Path $taskRoot '.tmp_complete_figures_20260920/methods/methods.pptx'
            $taskSourceIndex = $entry.native - 1
        }
        $taskDeck.Slides.Item([int]$entry.slide).Delete()
        $taskDeck.Slides.InsertFromFile($taskSource, ([int]$entry.slide-1), [int]$taskSourceIndex, [int]$taskSourceIndex) | Out-Null
        $taskSlide = $taskDeck.Slides.Item([int]$entry.slide)
        $taskSlide.NotesPage.Shapes.Placeholders.Item(2).TextFrame.TextRange.Text = ('Figure '+$entry.figure+': '+$entry.caption)
    }
    $taskDeck.SaveAs((Join-Path $taskTemp 'assembled.pptx'),24)
    Write-Output ('Assembled '+$taskDeck.Slides.Count+' slides with native diagrams')
    $taskDeck.Close()
} finally { $taskApp.Quit() }
