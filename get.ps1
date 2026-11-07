<#
  FreeWorks - one line to install or update (Windows PowerShell or PowerShell 7):

      [Net.ServicePointManager]::SecurityProtocol='Tls12'; iex $(try{irm https://raw.githubusercontent.com/scp15156402/FreeWorks/main/get.ps1 -TimeoutSec 20}catch{irm https://api.github.com/repos/scp15156402/FreeWorks/contents/get.ps1 -Headers @{Accept='application/vnd.github.raw'}})

  (The line turns on TLS 1.2, which Windows PowerShell 5.1 does not use by default, and fetches this
   script from GitHub's API when raw.githubusercontent.com is blocked - some Indian ISPs block it.)

  - Not installed yet  -> installs the latest FreeWorks (D:\FreeWorks if drive D: exists and has
                          space, otherwise %LOCALAPPDATA%\Programs\FreeWorks) and starts it.
  - Already installed  -> updates FreeWorks, its add-ons and (when needed) FreeCAD in place.
                          Settings are kept; projects (Documents\FreeWorks) are never touched.

  Roll back to the version you had before the last update (projects are never touched):
      in FreeWorks: Help > Roll Back to Previous Version...; or run the line above with
      $env:FREEWORKS_ROLLBACK = "1" set first.

  Uninstall (one line, one confirmation):
      [Net.ServicePointManager]::SecurityProtocol='Tls12'; iex $(try{irm https://raw.githubusercontent.com/scp15156402/FreeWorks/main/uninstall.ps1 -TimeoutSec 20}catch{irm https://api.github.com/repos/scp15156402/FreeWorks/contents/uninstall.ps1 -Headers @{Accept='application/vnd.github.raw'}})

  Options: set before the one-liner, e.g.  $env:FREEWORKS_DIR = "E:\FreeWorks"
      FREEWORKS_DIR      install folder for a new installation
      FREEWORKS_CHANNEL  "stable" (default, released version) or "main" (development)
      FREEWORKS_FORCE    "1" = reinstall even if already up to date
      FREEWORKS_ROLLBACK "1" = go back to the previous version
#>
param(
    [string]$InstallDir = "",
    [switch]$UpdateOnly,
    [switch]$NoAddons,
    [switch]$WithRender,
    [switch]$NoShortcuts,
    [int]$WaitPid = 0,
    [switch]$Restart,
    [string]$Channel = "",
    [switch]$Rollback
)

& {
    $ErrorActionPreference = "Stop"
    $ProgressPreference = "SilentlyContinue"
    try { [Net.ServicePointManager]::SecurityProtocol = [Net.ServicePointManager]::SecurityProtocol -bor [Net.SecurityProtocolType]::Tls12 } catch {}
    $Repo = "scp15156402/FreeWorks"
    $RegKey = "HKCU:\Software\FreeWorks"
    if ($env:FREEWORKS_ROLLBACK -eq "1") { $Rollback = $true }

    function Say($t, $c = "Cyan") { Write-Host $t -ForegroundColor $c }

    # A text file from the repository. raw.githubusercontent.com first; GitHub's API and jsDelivr
    # when raw is blocked (some Indian ISPs block it) or an antivirus web shield cuts the connection.
    function Get-RepoText($path, $ref) {
        $tries = @(
            @{ u = "https://raw.githubusercontent.com/$Repo/$ref/$path"; h = @{ "User-Agent" = "FreeWorks-Installer" } },
            @{ u = "https://api.github.com/repos/$Repo/contents/$($path)?ref=$ref"; h = @{ "User-Agent" = "FreeWorks-Installer"; "Accept" = "application/vnd.github.raw" } },
            @{ u = "https://cdn.jsdelivr.net/gh/$Repo@$ref/$path"; h = @{ "User-Agent" = "FreeWorks-Installer" } }
        )
        foreach ($t in $tries) {
            try {
                $r = Invoke-WebRequest -Uri $t.u -Headers $t.h -UseBasicParsing -TimeoutSec 20
                $c = $r.Content
                if ($c -is [byte[]]) { $c = [Text.Encoding]::UTF8.GetString($c) }
                if ($c) { return [string]$c }
            } catch {}
        }
        return $null
    }

    function Version-Of($xml) {
        if ("$xml" -match "<version>([^<]+)</version>") { return $Matches[1].Trim() }
        return $null
    }

    # File download: Windows' curl.exe first (clear errors, retries, resumes), then .NET.
    function Fetch($url, $dest) {
        $curl = Join-Path $env:SystemRoot "System32\curl.exe"
        if (Test-Path $curl) {
            & $curl -sS -L --fail --retry 3 --retry-delay 2 --connect-timeout 20 -A "FreeWorks-Installer" -o $dest $url
            if ($LASTEXITCODE -eq 0 -and (Test-Path $dest)) { return }
            Remove-Item -Force $dest -ErrorAction SilentlyContinue
        }
        Invoke-WebRequest -Uri $url -OutFile $dest -Headers @{ "User-Agent" = "FreeWorks-Installer" } -UseBasicParsing
    }

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

        if ($Rollback) {
            if (-not $existing) { throw "FreeWorks is not installed." }
            $prev = Join-Path $existing "_previous"
            if (-not (Test-Path (Join-Path $prev "Mod\FreeWorks"))) { Say "  There is no previous version to roll back to." "Yellow"; return }
            if (Running-In $existing) {
                Say "  FreeWorks is open. Save your work and close it - the rollback continues automatically." "Yellow"
                while (Running-In $existing) { Start-Sleep -Seconds 2 }
            }
            $reg = Get-ItemProperty $RegKey -ErrorAction SilentlyContinue
            $cur = $reg.Version; $curFC = $reg.FreeCADVersion
            $old = Get-Content (Join-Path $prev "version.txt") -TotalCount 1
            Say "  Rolling back FreeWorks $cur -> $old"
            $mod = Join-Path $existing "UserData\Mod"
            $swap = Join-Path $existing "_swap"
            if (Test-Path $swap) { Remove-Item -Recurse -Force $swap }
            New-Item -ItemType Directory -Force -Path (Join-Path $swap "Mod") | Out-Null
            foreach ($d in Get-ChildItem (Join-Path $prev "Mod") -Directory) {
                $live = Join-Path $mod $d.Name
                if (Test-Path $live) { Move-Item $live (Join-Path $swap ("Mod\" + $d.Name)) }
                Move-Item $d.FullName $live
            }
            $newFC = $curFC
            if (Test-Path (Join-Path $prev "FreeCAD\bin\freecad.exe")) {
                Move-Item (Join-Path $existing "FreeCAD") (Join-Path $swap "FreeCAD")
                Move-Item (Join-Path $prev "FreeCAD") (Join-Path $existing "FreeCAD")
                $newFC = Get-Content (Join-Path $prev "freecad_version.txt") -TotalCount 1
            }
            Set-Content -Path (Join-Path $swap "version.txt") -Value $cur
            Set-Content -Path (Join-Path $swap "freecad_version.txt") -Value $curFC
            Remove-Item -Recurse -Force $prev
            Rename-Item $swap "_previous"          # the newer version stays available for roll-forward
            Set-ItemProperty -Path $RegKey -Name Version -Value $old
            Set-ItemProperty -Path $RegKey -Name PreviousVersion -Value $cur
            if ($newFC) { Set-ItemProperty -Path $RegKey -Name FreeCADVersion -Value $newFC }
            Set-ItemProperty -Path "HKCU:\Software\Microsoft\Windows\CurrentVersion\Uninstall\FreeWorks" -Name DisplayVersion -Value $old -ErrorAction SilentlyContinue
            Set-Content -Path (Join-Path $existing "rolled_back_from.txt") -Value $cur
            Remove-Item -Force (Join-Path $existing "UserData\icons\.freeworks") -ErrorAction SilentlyContinue
            Say "  Rolled back to FreeWorks $old. Run the normal one-line command to update again." "Green"
            if ($Restart) { $exe = Join-Path $existing "FreeWorks.exe"; if (Test-Path $exe) { Start-Process $exe } }
            return
        }
        if ($update -and (Running-In $dir)) {
            Say "  FreeWorks is open. Save your work and close it - the update continues automatically." "Yellow"
            while (Running-In $dir) { Start-Sleep -Seconds 2 }
        }

        # which version? the "stable" branch is the released version, "main" is development
        $ch = if ($Channel) { $Channel } elseif ($env:FREEWORKS_CHANNEL) { $env:FREEWORKS_CHANNEL } else { "stable" }
        $branch = if ($ch -eq "main") { "main" } else { "stable" }
        $latest = Version-Of (Get-RepoText "Mod/FreeWorks/package.xml" $branch)
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
        $got = $false; $why = ""
        foreach ($url in @("https://github.com/$Repo/archive/refs/heads/$branch.zip",
                           "https://codeload.github.com/$Repo/zip/refs/heads/$branch",
                           "https://api.github.com/repos/$Repo/zipball/$branch")) {
            try { Fetch $url $zip; $got = $true; break } catch { $why = $_.Exception.Message }
        }
        if (-not $got) {
            throw ("could not download FreeWorks from GitHub ($why). Your network or antivirus is blocking " +
                   "github.com - try another network (e.g. a phone hotspot) or pause the antivirus web shield")
        }
        Expand-Archive -Path $zip -DestinationPath (Join-Path $tmp "x") -Force
        $script = Get-ChildItem -Path (Join-Path $tmp "x") -Recurse -Filter "install.ps1" | Select-Object -First 1
        if (-not $script) { throw "install.ps1 not found in the download." }

        # the downloaded files are the truth for the version (the check above can be blocked or cached)
        $pkgFile = Join-Path $script.DirectoryName "Mod\FreeWorks\package.xml"
        if (Test-Path $pkgFile) {
            $v = Version-Of (Get-Content -Raw $pkgFile)
            if ($v) { $latest = $v }
        }
        if ($update -and $latest -and -not $env:FREEWORKS_FORCE) {
            $cur = (Get-ItemProperty $RegKey -ErrorAction SilentlyContinue).Version
            if ($cur -and $cur -eq $latest) {
                Remove-Item -Recurse -Force $tmp -ErrorAction SilentlyContinue
                Say "  FreeWorks is already up to date ($latest)." "Green"
                if ($Restart) { $exe = Join-Path $dir "FreeWorks.exe"; if (Test-Path $exe) { Start-Process $exe } }
                return
            }
        }

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
