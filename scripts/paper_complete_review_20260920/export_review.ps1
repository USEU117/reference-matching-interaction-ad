# Export the active review manuscript to PDF, and refresh the Word statistics record.
#
# Verified working path (2026-09-25, on this machine):
#   * Word COM PDF export does NOT complete for this document.  Five attempts of
#     Open -> Repaginate -> ExportAsFixedFormat (2-arg and 12-arg with DocStructureTags off,
#     print and on-screen optimisation, default and PDF printer) ran 11-45 min with no file and
#     no error, at a steady 30-40% of one core and with no modal dialog.  The same Word COM
#     statistics pass on the same document finishes in 4.9 s, and a one-page control document
#     exports to PDF in 4.9 s through the identical call, so the PDF subsystem and the document
#     model are healthy; only this document's export stalls.
#   * The usable DOCX -> PDF toolchain on this machine is the installed WPS Office Writer COM
#     server (`KWPS.Application`): Open -> ExportAsFixedFormat(path, 17) writes the PDF in
#     11.5 s (61 pages / 10,875,228 B for the 2026-09-25 manuscript).  Its page count matches the
#     Word statistics page count (61), so the PDF stays in step with the DOCX.
#   * The Word COM statistics pass supplies word_review.json (pages / words / tables / inline
#     figures / table page ranges) used by the delivery check.
#
# Usage (from the repository root):
#   powershell -NoProfile -ExecutionPolicy Bypass -File scripts/paper_complete_review_20260920/export_review.ps1
#   powershell ... -File scripts/paper_complete_review_20260920/export_review.ps1 -Engine word   # may stall
#
# Outputs:
#   docs/paper_complete_review_20260920/Reference_Matching_Complete_English_20260925.pdf
#   .tmp_revision_20260925/word_review.json
#   .tmp_revision_20260925/pdf_export.json   (engine, elapsed seconds, pdf bytes)
param([ValidateSet('wps','word')][string]$Engine='wps')

$taskStart=Get-Date
$taskRoot=(Resolve-Path (Join-Path $PSScriptRoot '../..')).Path
$taskTemp=Join-Path $taskRoot '.tmp_revision_20260925'
if(-not (Test-Path -LiteralPath $taskTemp)){New-Item -ItemType Directory -Path $taskTemp | Out-Null}
$taskDoc=Join-Path $taskRoot 'docs/paper_complete_review_20260920/Reference_Matching_Complete_English_20260925.docx'
$taskPdf=Join-Path $taskRoot 'docs/paper_complete_review_20260920/Reference_Matching_Complete_English_20260925.pdf'

# --- PDF export -----------------------------------------------------------------------------
switch ($Engine) {
    'wps' {
        $taskWord=New-Object -ComObject KWPS.Application
        try { $taskWord.Visible=$false } catch {}
        try { $taskWord.DisplayAlerts=0 } catch {}
        try {
            $taskPaper=$taskWord.Documents.Open($taskDoc)
            $taskPaper.ExportAsFixedFormat($taskPdf,17)   # 17 = wdExportFormatPDF
            $taskPaper.Close(0)
        } finally { try { $taskWord.Quit() } catch {} }
    }
    'word' {
        $taskWord=New-Object -ComObject Word.Application
        $taskWord.Visible=$false
        $taskWord.DisplayAlerts=0
        $taskWord.ScreenUpdating=$false
        try {
            $taskPaper=$taskWord.Documents.Open($taskDoc,$false,$true)
            $taskPaper.Repaginate()
            try {
                # OptimizeFor=0, Range=0, From=0, To=0, Item=0, IncludeDocProps, KeepIRM,
                # CreateBookmarks=0, DocStructureTags=$false.  [Type]::Missing for the optional
                # Long arguments raises "Value does not fall within the expected range".
                $taskPaper.ExportAsFixedFormat($taskPdf,17,$false,0,0,0,0,0,$true,$true,0,$false)
            } catch { $taskPaper.SaveAs2($taskPdf,17) }
            $taskPaper.Close(0)
        } finally { $taskWord.Quit() }
    }
}
# Wait until the written file stops growing.
$taskPrev=-1
for($i=0;$i -lt 240;$i++){
    Start-Sleep -Milliseconds 500
    $taskLen=if(Test-Path -LiteralPath $taskPdf){(Get-Item -LiteralPath $taskPdf).Length}else{-1}
    if($taskLen -gt 0 -and $taskLen -eq $taskPrev){break}
    $taskPrev=$taskLen
}

# --- Word statistics record -----------------------------------------------------------------
Copy-Item -LiteralPath $taskPdf -Destination (Join-Path $taskTemp 'paper.pdf') -Force
$taskStatsWord=New-Object -ComObject Word.Application
$taskStatsWord.Visible=$false
$taskStatsWord.DisplayAlerts=0
$taskStatsWord.ScreenUpdating=$false
$taskStatsPages=$null
try {
    $taskPaper=$taskStatsWord.Documents.Open($taskDoc,$false,$true)
    $taskPaper.Repaginate()
    $taskStatsPages=$taskPaper.ComputeStatistics(2)
    $taskStats=[ordered]@{pages=$taskStatsPages;words=$taskPaper.ComputeStatistics(0);tables=$taskPaper.Tables.Count;images=$taskPaper.InlineShapes.Count;tablePages=@()}
    foreach($taskTable in $taskPaper.Tables){
        $taskS=$taskTable.Range.Duplicate;$taskS.Collapse(1)
        $taskE=$taskTable.Range.Duplicate;$taskE.Collapse(0)
        $taskStats.tablePages+=@{start=$taskS.Information(3);end=$taskE.Information(3)}
    }
    $taskStats | ConvertTo-Json -Depth 8 | Set-Content -LiteralPath (Join-Path $taskTemp 'word_review.json') -Encoding utf8
    $taskPaper.Close(0)
} finally { $taskStatsWord.Quit() }

$taskElapsed=[math]::Round(((Get-Date)-$taskStart).TotalSeconds,1)
$taskPdfBytes=if(Test-Path -LiteralPath $taskPdf){(Get-Item -LiteralPath $taskPdf).Length}else{0}
$taskSummary=[ordered]@{engine=$Engine;elapsedSec=$taskElapsed;pdfBytes=$taskPdfBytes;docxPages=$taskStatsPages;pdfPages=$null;ts=(Get-Date).ToString('s')}
[ordered]@{engine=$Engine;elapsedSec=$taskElapsed;pdfBytes=$taskPdfBytes;docxPages=$taskStatsPages} | ConvertTo-Json | Set-Content -LiteralPath (Join-Path $taskTemp 'pdf_export.json') -Encoding utf8
$taskSummary | ConvertTo-Json
