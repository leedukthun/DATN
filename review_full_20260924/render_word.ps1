$ErrorActionPreference = 'Stop'
$sourceDoc = 'E:\Downloads\CNTT_2022606983_LeDucThuan_BaoCao.docx'
$reviewDir = 'D:\DATN\he_thong_phat_hien_khong_doi_mu_VSCode_scrollfix\review_full_20260924'
$wordApp = $null
$reportDoc = $null
try {
    $wordApp = New-Object -ComObject Word.Application
    $wordApp.Visible = $false
    $wordApp.DisplayAlerts = 0
    $reportDoc = $wordApp.Documents.Open($sourceDoc, $false, $true, $false)
    $reportDoc.Repaginate()
    $pageCount = $reportDoc.ComputeStatistics(2)
    $reportDoc.ExportAsFixedFormat((Join-Path $reviewDir 'report.pdf'), 17)
    $map = @()
    foreach ($p in $reportDoc.Paragraphs) {
        $range = $p.Range
        $map += [PSCustomObject]@{start=$range.Start;page=$range.Information(3);printed=$range.Information(1);text=$range.Text}
    }
    $map | ConvertTo-Json -Depth 4 | Set-Content -LiteralPath (Join-Path $reviewDir 'word_pages.json') -Encoding utf8
    Write-Output "Exported $pageCount pages using Word in read-only mode"
} finally {
    if ($null -ne $reportDoc) { $reportDoc.Close(0) }
    if ($null -ne $wordApp) { $wordApp.Quit() }
}
