<#  Removes FreeWorks: its folder and its shortcuts. Nothing else on the PC is touched. #>
param([string]$InstallDir = $(Split-Path -Parent $MyInvocation.MyCommand.Path))
$ErrorActionPreference = "Continue"
if (-not (Test-Path (Join-Path $InstallDir "FreeCAD\bin")) -and -not (Test-Path (Join-Path $InstallDir "UserData"))) {
    Write-Host "$InstallDir does not look like a FreeWorks installation." -ForegroundColor Yellow; exit 1
}
$ans = Read-Host "Delete $InstallDir and the FreeWorks shortcuts? Your own part files elsewhere are not touched. (y/N)"
if ($ans -notmatch '^[yY]') { exit 0 }
foreach ($dir in @([Environment]::GetFolderPath("Desktop"), [Environment]::GetFolderPath("Programs"))) {
    $l = Join-Path $dir "FreeWorks.lnk"; if (Test-Path $l) { Remove-Item -Force $l }
}
Set-Location $env:TEMP
Remove-Item -Recurse -Force $InstallDir
Write-Host "FreeWorks removed." -ForegroundColor Green
