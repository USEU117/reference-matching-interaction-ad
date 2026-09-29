# Export the five-seed revision manuscript to PDF.
#
# The 2026-09-25 revision established the working path on this machine: Word COM PDF export
# stalls on this document, while the installed WPS Office Writer COM server
# (`KWPS.Application`) writes the PDF in seconds with a page count that matches Word's own
# statistics pass.  The same path is used here.
#
# Usage (from the repository root):
#   powershell -NoProfile -ExecutionPolicy Bypass -File scripts/paper_revision_five_seed_20260928/export_revision.ps1
#
# Output: docs/paper_revision_five_seed_20260928/Reference_Matching_Complete_English_20260929.pdf
$ErrorActionPreference='Stop'
$root=(Resolve-Path (Join-Path $PSScriptRoot '../..')).Path
$doc=Join-Path $root 'docs/paper_revision_five_seed_20260928/Reference_Matching_Complete_English_20260929.docx'
$pdf=Join-Path $root 'docs/paper_revision_five_seed_20260928/Reference_Matching_Complete_English_20260929.pdf'
if(-not (Test-Path -LiteralPath $doc)){throw "missing $doc"}
if(Test-Path -LiteralPath $pdf){Remove-Item -LiteralPath $pdf -Force}
$start=Get-Date
$word=New-Object -ComObject KWPS.Application
try{$word.Visible=$false}catch{}
try{$word.DisplayAlerts=0}catch{}
$paper=$word.Documents.Open($doc,$false,$true)
try{
    $paper.ExportAsFixedFormat($pdf,17)
}finally{
    $paper.Close($false)
    $word.Quit()
}
$seconds=[math]::Round(((Get-Date)-$start).TotalSeconds,1)
$bytes=(Get-Item -LiteralPath $pdf).Length
Write-Output "pdf=$pdf bytes=$bytes seconds=$seconds"
