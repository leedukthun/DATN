param([string]$InputDocx, [string]$OutputPdf)
$ErrorActionPreference = 'Stop'
$reviewWord = $null
$reviewDoc = $null
$reviewOwnInstance = $false
try {
    $reviewWord = New-Object -ComObject Word.Application
    $reviewOwnInstance = ($reviewWord.Documents.Count -eq 0)
    if ($reviewOwnInstance) {
        $reviewWord.Visible = $false
        $reviewWord.DisplayAlerts = 0
    }
    $reviewDoc = $reviewWord.Documents.Open($InputDocx, $false, $true, $false)
    $reviewDoc.Repaginate()
    $reviewDoc.ExportAsFixedFormat($OutputPdf, 17)
    Write-Output "Exported PDF: $OutputPdf"
    Write-Output "Pages: $($reviewDoc.ComputeStatistics(2))"
}
finally {
    if ($null -ne $reviewDoc) { $reviewDoc.Close(0) }
    if ($null -ne $reviewWord -and $reviewOwnInstance) { $reviewWord.Quit() }
    if ($null -ne $reviewDoc) { [void][Runtime.InteropServices.Marshal]::ReleaseComObject($reviewDoc) }
    if ($null -ne $reviewWord) { [void][Runtime.InteropServices.Marshal]::ReleaseComObject($reviewWord) }
}
