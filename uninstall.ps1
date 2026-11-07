<#
  Uninstall FreeWorks - one line, one confirmation:

      irm https://raw.githubusercontent.com/scp15156402/FreeWorks/main/uninstall.ps1 | iex

  Also available in Windows Settings > Apps > FreeWorks.
  Removes the FreeWorks folder (program, FreeCAD copy, settings), shortcuts and registry entries.
  Your projects and macros in Documents\FreeWorks are NOT removed.
#>
param([string]$InstallDir = "")

& {
    $RegKey = "HKCU:\Software\FreeWorks"
    $UninstKey = "HKCU:\Software\Microsoft\Windows\CurrentVersion\Uninstall\FreeWorks"

    $dir = $InstallDir
    if (-not $dir -and (Test-Path $RegKey)) { $dir = (Get-ItemProperty $RegKey -ErrorAction SilentlyContinue).InstallDir }
    if (-not $dir -and $PSCommandPath) {
        $here = Split-Path -Parent $PSCommandPath
        if (Test-Path (Join-Path $here "FreeCAD\bin")) { $dir = $here }
    }
    if (-not $dir) {
        foreach ($d in @("D:\FreeWorks", "$env:LOCALAPPDATA\Programs\FreeWorks", "C:\FreeWorks")) {
            if (Test-Path (Join-Path $d "FreeCAD\bin")) { $dir = $d; break }
        }
    }
    if (-not $dir -or -not (Test-Path $dir)) {
        Write-Host "FreeWorks is not installed on this PC." -ForegroundColor Yellow
        return
    }
    # safety: only ever delete a folder that really is a FreeWorks installation
    if (-not ((Test-Path (Join-Path $dir "FreeCAD\bin")) -or (Test-Path (Join-Path $dir "UserData\Mod\FreeWorks")))) {
        Write-Host "$dir does not look like a FreeWorks installation - nothing removed." -ForegroundColor Yellow
        return
    }
    $projects = (Get-ItemProperty $RegKey -ErrorAction SilentlyContinue).ProjectsDir
    if (-not $projects) { $projects = Join-Path ([Environment]::GetFolderPath("MyDocuments")) "FreeWorks" }

    Write-Host ""
    Write-Host "Remove FreeWorks from $dir ?" -ForegroundColor White
    Write-Host "Your projects and macros in $projects are kept." -ForegroundColor Gray
    $ans = Read-Host "Type y to uninstall"
    if ($ans -notmatch '^\s*[yY]') { Write-Host "Cancelled - nothing was changed."; return }

    $running = Get-Process -Name freecad -ErrorAction SilentlyContinue | Where-Object {
        try { $_.Path -and $_.Path.StartsWith($dir, [StringComparison]::OrdinalIgnoreCase) } catch { $false } }
    if ($running) {
        Write-Host "FreeWorks is open - save your work and close it; uninstall continues automatically..." -ForegroundColor Yellow
        while (Get-Process -Id ($running.Id) -ErrorAction SilentlyContinue) { Start-Sleep -Seconds 2 }
    }

    foreach ($f in @([Environment]::GetFolderPath("Desktop"), [Environment]::GetFolderPath("Programs"))) {
        foreach ($n in @("FreeWorks.lnk", "FreeWorks (Safe Mode).lnk")) {
            $l = Join-Path $f $n
            if (Test-Path $l) { Remove-Item -Force $l -ErrorAction SilentlyContinue }
        }
    }
    Remove-Item -Path $RegKey -Recurse -Force -ErrorAction SilentlyContinue
    Remove-Item -Path $UninstKey -Recurse -Force -ErrorAction SilentlyContinue
    Set-Location $env:TEMP
    Remove-Item -Path $dir -Recurse -Force -ErrorAction SilentlyContinue
    if (Test-Path $dir) {
        Write-Host "Some files in $dir are in use and could not be removed; delete the folder after restarting Windows." -ForegroundColor Yellow
    } else {
        Write-Host "FreeWorks has been removed. Your projects are still in $projects." -ForegroundColor Green
    }
    if ($PSCommandPath) { Start-Sleep -Seconds 6 }   # started from Windows Settings: keep the message visible
}
