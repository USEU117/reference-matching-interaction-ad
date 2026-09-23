$taskRoot=(Resolve-Path (Join-Path $PSScriptRoot '../..')).Path
$taskTemp=Join-Path $taskRoot '.tmp_revision_20260923'
$taskDoc=Join-Path $taskRoot 'docs/paper_complete_review_20260920/Reference_Matching_Complete_English_20260923.docx'
$taskWord=New-Object -ComObject Word.Application
$taskWord.Visible=$false
$taskWord.DisplayAlerts=$false
try {
    $taskPaper=$taskWord.Documents.Open($taskDoc,$false,$true)
    $taskPaper.Fields.Update() | Out-Null
    $taskPaper.Repaginate()
    $taskPaper.ExportAsFixedFormat((Join-Path $taskTemp 'paper.pdf'),17)
    $taskStats=[ordered]@{pages=$taskPaper.ComputeStatistics(2);words=$taskPaper.ComputeStatistics(0);tables=$taskPaper.Tables.Count;images=$taskPaper.InlineShapes.Count;tablePages=@()}
    foreach($taskTable in $taskPaper.Tables){
        $taskStart=$taskTable.Range.Duplicate;$taskStart.Collapse(1)
        $taskEnd=$taskTable.Range.Duplicate;$taskEnd.Collapse(0)
        $taskStats.tablePages+=@{start=$taskStart.Information(3);end=$taskEnd.Information(3)}
    }
    $taskStats | ConvertTo-Json -Depth 8 | Set-Content -LiteralPath (Join-Path $taskTemp 'word_review.json') -Encoding utf8
    $taskPaper.Close(0)
    $taskStats | ConvertTo-Json -Depth 3
} finally {$taskWord.Quit()}
