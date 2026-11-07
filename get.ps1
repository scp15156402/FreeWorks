<#
  FreeWorks - one line to install or update (Windows PowerShell or PowerShell 7):

      irm https://raw.githubusercontent.com/scp15156402/FreeWorks/main/get.ps1 | iex

  - Not installed yet  -> installs the latest FreeWorks (D:\FreeWorks if drive D: exists and has
                          space, otherwise %LOCALAPPDATA%\Programs\FreeWorks) and starts it.
  - Already installed  -> updates FreeWorks, its add-ons and (when needed) FreeCAD in place.
                          Settings are kept; projects (Documents\FreeWorks) are never touched.

  Uninstall (one line, one confirmation):
      irm https://raw.githubusercontent.com/scp15156402/FreeWorks/main/uninstall.ps1 | iex

  Options: set before the one-liner, e.g.  $env:FREEWORKS_DIR = "E:\FreeWorks"
      FREEWORKS_DIR      install folder for a new installation
      FREEWORKS_CHANNEL  "stable" (default, released version) or "main" (development)
      FREEWORKS_FORCE    "1" = reinstall even if already up to date
#>
param(
    [string]$InstallDir = "",
    [switch]$UpdateOnly,
    [switch]$NoAddons,
    [switch]$WithRender,
    [switch]$NoShortcuts,
    [int]$WaitPid = 0,
    [switch]$Restart,
    [string]$Channel = ""
)

& {
    $ErrorActionPreference = "Stop"
    $ProgressPreference = "SilentlyContinue"
    [Net.ServicePointManager]::SecurityProtocol = [Net.ServicePointManager]::SecurityProtocol -bor [Net.SecurityProtocolType]::Tls12
    $Repo = "scp15156402/FreeWorks"
    $RegKey = "HKCU:\Software\FreeWorks"

    function Say($t, $c = "Cyan") { Write-Host $t -ForegroundColor $c }

    function Find-Install {
        if (Test-Path $RegKey) {
            $d = (Get-ItemProperty $RegKey -ErrorAction SilentlyContinue).InstallDir
            if ($d -and (Test-Path (Join-Path $d "FreeCAD\bin\freecad.exe"))) { return $d }
        }
        foreach ($d in @("D:\FreeWorks", "$env:LOCALAPPDATA\Programs\FreeWorks", "C:\FreeWorks")) {
            if (Test-Path (Join-Path $d "FreeCAD\bin\freecad.exe")) { return $d }
        }
        return $null
    }

    function Default-Dir {
        if ($env:FREEWORKS_DIR) { return $env:FREEWORKS_DIR }
        try {
            $d = Get-CimInstance Win32_LogicalDisk -Filter "DeviceID='D:'" -ErrorAction Stop
            if ($d -and $d.DriveType -eq 3 -and $d.FreeSpace -gt 4GB) { return "D:\FreeWorks" }
        } catch {}
        return (Join-Path $env:LOCALAPPDATA "Programs\FreeWorks")
    }

    function Running-In($dir) {
        Get-Process -Name freecad -ErrorAction SilentlyContinue | Where-Object {
            try { $_.Path -and $_.Path.StartsWith($dir, [StringComparison]::OrdinalIgnoreCase) } catch { $false }
        }
    }

    try {
        if ($env:OS -ne "Windows_NT") { throw "FreeWorks needs Windows 10 or 11." }
        if (-not [Environment]::Is64BitOperatingSystem) { throw "FreeWorks needs 64-bit Windows." }

        Write-Host ""
        Say "FreeWorks - SolidWorks-style CAD on FreeCAD" "White"

        $existing = Find-Install
        if ($InstallDir) { $dir = $InstallDir } elseif ($existing) { $dir = $existing } else { $dir = Default-Dir }
        $update = [bool]($existing -and ($existing.TrimEnd('\') -eq $dir.TrimEnd('\')))
        if ($UpdateOnly -and -not $update -and (Test-Path (Join-Path $dir "FreeCAD\bin\freecad.exe"))) { $update = $true }
        Say ("  " + $(if ($update) { "Updating FreeWorks in $dir" } else { "Installing FreeWorks into $dir" }))

        # never update under a running FreeWorks (unsaved work must not be lost)
        if ($WaitPid -gt 0) { try { Wait-Process -Id $WaitPid -Timeout 180 -ErrorAction SilentlyContinue } catch {} }
        if ($update -and (Running-In $dir)) {
            Say "  FreeWorks is open. Save your work and close it - the update continues automatically." "Yellow"
            while (Running-In $dir) { Start-Sleep -Seconds 2 }
        }

        # which version? the "stable" branch is the released version, "main" is development
        $ch = if ($Channel) { $Channel } elseif ($env:FREEWORKS_CHANNEL) { $env:FREEWORKS_CHANNEL } else { "stable" }
        $branch = if ($ch -eq "main") { "main" } else { "stable" }
        $hdr = @{ "User-Agent" = "FreeWorks-Installer" }
        $latest = $null
        try {
            $pkg = (Invoke-WebRequest -Uri "https://raw.githubusercontent.com/$Repo/$branch/Mod/FreeWorks/package.xml" -Headers $hdr -UseBasicParsing).Content
            if ("$pkg" -match "<version>([^<]+)</version>") { $latest = $Matches[1].Trim() }
        } catch {
            $branch = "main"   # stable branch not published yet
        }
        $url = "https://github.com/$Repo/archive/refs/heads/$branch.zip"
        $label = if ($latest) { "$latest ($branch)" } else { $branch }

        if ($update -and $latest -and -not $env:FREEWORKS_FORCE) {
            $cur = (Get-ItemProperty $RegKey -ErrorAction SilentlyContinue).Version
            if ($cur -and $cur -eq $latest) {
                Say "  FreeWorks is already up to date ($latest)." "Green"
                if ($Restart) { $exe = Join-Path $dir "FreeWorks.exe"; if (Test-Path $exe) { Start-Process $exe } }
                return
            }
        }

        $tmp = Join-Path $env:TEMP ("FreeWorks_" + [guid]::NewGuid().ToString("N"))
        New-Item -ItemType Directory -Force -Path $tmp | Out-Null
        $zip = Join-Path $tmp "FreeWorks.zip"
        Say "  Downloading FreeWorks $label ..."
        Invoke-WebRequest -Uri $url -OutFile $zip -Headers $hdr -UseBasicParsing
        Expand-Archive -Path $zip -DestinationPath (Join-Path $tmp "x") -Force
        $script = Get-ChildItem -Path (Join-Path $tmp "x") -Recurse -Filter "install.ps1" | Select-Object -First 1
        if (-not $script) { throw "install.ps1 not found in the download." }

        # run the installer in Windows PowerShell 5.1 (works under any execution policy)
        $a = @("-NoProfile", "-ExecutionPolicy", "Bypass", "-File", "`"$($script.FullName)`"", "-InstallDir", "`"$dir`"")
        if ($update)      { $a += "-UpdateOnly" }
        if ($NoAddons)    { $a += "-NoAddons" }
        if ($WithRender)  { $a += "-WithRender" }
        if ($NoShortcuts) { $a += "-NoShortcuts" }
        if ($latest)      { $a += @("-Version", $latest) }
        $ps = Join-Path $env:SystemRoot "System32\WindowsPowerShell\v1.0\powershell.exe"
        $p = Start-Process -FilePath $ps -ArgumentList $a -NoNewWindow -Wait -PassThru
        Remove-Item -Recurse -Force $tmp -ErrorAction SilentlyContinue
        if ($p.ExitCode -ne 0) { throw "the installer reported an error (log: $dir\install.log)" }

        if ($Restart -or -not $update) {
            $exe = Join-Path $dir "FreeWorks.exe"
            if (-not (Test-Path $exe)) { $exe = Join-Path $dir "FreeWorks.cmd" }
            if (Test-Path $exe) { Say "  Starting FreeWorks..."; Start-Process -FilePath $exe }
        }
    } catch {
        Write-Host ""
        Write-Host "FreeWorks setup failed: $($_.Exception.Message)" -ForegroundColor Red
        Write-Host "Nothing you created was touched. Run the same command again, or see https://github.com/$Repo/issues" -ForegroundColor Red
    }
}
