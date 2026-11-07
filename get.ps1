<#
  FreeWorks one-line installer / updater.

  Install (Windows PowerShell):
     irm https://raw.githubusercontent.com/scp15156402/FreeWorks/main/get.ps1 | iex

  With options (e.g. another folder, or the Render add-on):
     & ([scriptblock]::Create((irm https://raw.githubusercontent.com/scp15156402/FreeWorks/main/get.ps1))) -InstallDir "E:\FreeWorks" -WithRender

  Downloads the latest FreeWorks release (or the main branch if no release exists
  yet) and runs install.ps1 from it.
#>
param(
    [string]$InstallDir = "D:\FreeWorks",
    [switch]$UpdateOnly,
    [switch]$NoAddons,
    [switch]$WithRender,
    [switch]$NoShortcuts,
    [int]$WaitPid = 0,        # used by the in-app updater: wait for FreeWorks to close
    [switch]$Restart          # used by the in-app updater: start FreeWorks afterwards
)
$ErrorActionPreference = "Stop"
$ProgressPreference = "SilentlyContinue"
[Net.ServicePointManager]::SecurityProtocol = [Net.SecurityProtocolType]::Tls12

$Repo = "scp15156402/FreeWorks"
$Headers = @{ "User-Agent" = "FreeWorks-Installer"; "Accept" = "application/vnd.github+json" }

if ($WaitPid -gt 0) {
    Write-Host "Waiting for FreeWorks to close..."
    try { Wait-Process -Id $WaitPid -Timeout 120 -ErrorAction SilentlyContinue } catch {}
}

$tmp = Join-Path $env:TEMP ("FreeWorks_get_" + [guid]::NewGuid().ToString("N"))
New-Item -ItemType Directory -Force -Path $tmp | Out-Null
$zip = Join-Path $tmp "FreeWorks.zip"
$label = "main branch"
try {
    $rel = Invoke-RestMethod -Uri "https://api.github.com/repos/$Repo/releases/latest" -Headers $Headers
    $asset = $rel.assets | Where-Object { $_.name -like "*.zip" } | Select-Object -First 1
    $url = if ($asset) { $asset.browser_download_url } else { $rel.zipball_url }
    $label = "release $($rel.tag_name)"
} catch {
    $url = "https://github.com/$Repo/archive/refs/heads/main.zip"
}
Write-Host "Downloading FreeWorks ($label)..." -ForegroundColor Cyan
Invoke-WebRequest -Uri $url -OutFile $zip -Headers @{ "User-Agent" = "FreeWorks-Installer" } -UseBasicParsing
Expand-Archive -Path $zip -DestinationPath (Join-Path $tmp "x") -Force
$script = Get-ChildItem -Path (Join-Path $tmp "x") -Recurse -Filter "install.ps1" | Select-Object -First 1
if (-not $script) { throw "install.ps1 not found in the downloaded package" }

$args2 = @{ InstallDir = $InstallDir }
if ($UpdateOnly)  { $args2.UpdateOnly = $true }
if ($NoAddons)    { $args2.NoAddons = $true }
if ($WithRender)  { $args2.WithRender = $true }
if ($NoShortcuts) { $args2.NoShortcuts = $true }
& $script.FullName @args2

Remove-Item -Recurse -Force $tmp -ErrorAction SilentlyContinue
if ($Restart) {
    $exe = Join-Path $InstallDir "FreeWorks.exe"
    if (-not (Test-Path $exe)) { $exe = Join-Path $InstallDir "FreeWorks.cmd" }
    if (Test-Path $exe) { Start-Process -FilePath $exe }
}
