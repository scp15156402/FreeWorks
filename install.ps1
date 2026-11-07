<#
  FreeWorks installer / updater (Windows PowerShell 5.1). Normally started by get.ps1 or
  Install.cmd. Everything FreeWorks needs lives in one folder:

     <InstallDir>\FreeCAD\       official portable FreeCAD (version from versions.json)
     <InstallDir>\UserData\      FreeWorks settings and add-ons (kept on update)
     <InstallDir>\FreeWorks.exe  launcher
  Projects and macros live in Documents\FreeWorks and are never touched.

  -UpdateOnly : existing installation; keep settings, replace FreeWorks and add-ons, upgrade
                FreeCAD only if versions.json pins a different version (side-by-side swap).
#>
param(
    [string]$InstallDir = "",
    [switch]$UpdateOnly,
    [switch]$NoAddons,
    [switch]$WithRender,
    [switch]$NoShortcuts,
    [string]$Version = ""
)

$ErrorActionPreference = "Stop"
$ProgressPreference = "SilentlyContinue"
[Net.ServicePointManager]::SecurityProtocol = [Net.ServicePointManager]::SecurityProtocol -bor [Net.SecurityProtocolType]::Tls12

$Here = Split-Path -Parent $MyInvocation.MyCommand.Path
$RegKey = "HKCU:\Software\FreeWorks"
$UninstKey = "HKCU:\Software\Microsoft\Windows\CurrentVersion\Uninstall\FreeWorks"

function Step($t)  { Write-Host ""; Write-Host "==> $t" -ForegroundColor Cyan }
function Ok($t)    { Write-Host "    $t" -ForegroundColor Green }
function Info($t)  { Write-Host "    $t" }
function Warn($t)  { Write-Host "    WARNING: $t" -ForegroundColor Yellow }

# ------------------------------------------------------------------ manifest
$manifest = Get-Content -Raw -Path (Join-Path $Here "versions.json") | ConvertFrom-Json
$FC = $manifest.freecad
if (-not $Version) {
    $Version = (Select-String -Path (Join-Path $Here "Mod\FreeWorks\package.xml") -Pattern "<version>(.*)</version>").Matches[0].Groups[1].Value
}

# ------------------------------------------------------------------ location
if (-not $InstallDir) {
    $InstallDir = $null
    if (Test-Path $RegKey) { $InstallDir = (Get-ItemProperty $RegKey -ErrorAction SilentlyContinue).InstallDir }
    if (-not $InstallDir) {
        $d = Get-CimInstance Win32_LogicalDisk -Filter "DeviceID='D:'" -ErrorAction SilentlyContinue
        $InstallDir = if ($d -and $d.DriveType -eq 3 -and $d.FreeSpace -gt 4GB) { "D:\FreeWorks" } else { Join-Path $env:LOCALAPPDATA "Programs\FreeWorks" }
    }
}
$App  = Join-Path $InstallDir "FreeCAD"
$Data = Join-Path $InstallDir "UserData"
$Mod  = Join-Path $Data "Mod"
$Dl   = Join-Path $InstallDir "_downloads"
New-Item -ItemType Directory -Force -Path $InstallDir, $Data, $Mod, $Dl | Out-Null
try { Start-Transcript -Path (Join-Path $InstallDir "install.log") -Append | Out-Null } catch {}

$exitCode = 0
try {
    Write-Host "FreeWorks $Version  ->  $InstallDir" -ForegroundColor White

    # -------------------------------------------------------------- preflight
    if (-not [Environment]::Is64BitOperatingSystem) { throw "64-bit Windows is required." }
    $os = [Environment]::OSVersion.Version
    if ($os.Major -lt 10) { throw "Windows 10 or 11 is required." }
    $drive = (Split-Path -Qualifier $InstallDir)
    $free = (Get-PSDrive ($drive.TrimEnd(':'))).Free
    $needFreeCAD = -not (Test-Path (Join-Path $App "bin\freecad.exe"))
    $installedFC = $null
    if (Test-Path $RegKey) { $installedFC = (Get-ItemProperty $RegKey -ErrorAction SilentlyContinue).FreeCADVersion }
    if (-not $needFreeCAD -and $installedFC -and $installedFC -ne $FC.version) { $needFreeCAD = $true }
    if ($needFreeCAD -and $free -lt 3GB) { throw ("not enough disk space on {0}: {1:N1} GB free, about 3 GB needed" -f $drive, ($free / 1GB)) }

    $running = Get-Process -Name freecad -ErrorAction SilentlyContinue | Where-Object {
        try { $_.Path -and $_.Path.StartsWith($InstallDir, [StringComparison]::OrdinalIgnoreCase) } catch { $false } }
    if ($running) { throw "FreeWorks is running. Save your work, close it, and run the command again." }

    # -------------------------------------------------------------- helpers
    # curl.exe (in Windows 10 1803+) with retries and resume; returns curl's exit code
    function Curl-Get($url, $part, $extra) {
        $curl = Join-Path $env:SystemRoot "System32\curl.exe"
        if (-not (Test-Path $curl)) { return 99 }
        $a = @("-L", "--fail", "--retry", "3", "--retry-delay", "3", "--connect-timeout", "30", "-C", "-",
               "--progress-bar", "-A", "FreeWorks-Installer") + $extra + @("-o", $part, $url)
        & $curl @a
        return $LASTEXITCODE
    }

    # A host's real address from Cloudflare / Google over HTTPS (bypasses an ISP's DNS block)
    function Doh-IP($name) {
        foreach ($srv in @("https://cloudflare-dns.com/dns-query?name=$name&type=A", "https://dns.google/resolve?name=$name&type=A")) {
            try {
                $r = Invoke-WebRequest -Uri $srv -Headers @{ "Accept" = "application/dns-json" } -UseBasicParsing -TimeoutSec 15
                $c = $r.Content
                if ($c -is [byte[]]) { $c = [Text.Encoding]::UTF8.GetString($c) }
                $ip = (ConvertFrom-Json $c).Answer | Where-Object { $_.type -eq 1 } | Select-Object -First 1 -ExpandProperty data
                if ($ip) { return $ip }
            } catch {}
        }
        return $null
    }

    function Download($url, $dest) {
        # resumable: data goes to <dest>.part and is renamed only when complete
        if (Test-Path $dest) { Remove-Item -Force $dest }
        $part = "$dest.part"
        $name = Split-Path -Leaf $dest
        $curl = Join-Path $env:SystemRoot "System32\curl.exe"
        if (Test-Path $curl) {
            $code = Curl-Get $url $part @()
            if ($code -eq 0) { Move-Item -Force $part $dest; return }
            Warn "download of $name failed (curl code $code) - trying encrypted DNS (some networks block GitHub's download server)"
            # 1) curl 7.62+ resolves every host of the redirect chain over HTTPS itself
            foreach ($doh in @("https://cloudflare-dns.com/dns-query", "https://dns.google/dns-query")) {
                $code = Curl-Get $url $part @("--doh-url", $doh)
                if ($code -eq 0) { Ok "downloaded through encrypted DNS"; Move-Item -Force $part $dest; return }
                if ($code -eq 2) { break }   # this curl has no --doh-url
            }
            # 2) older curl: resolve the hosts of the redirect chain ourselves and pin them
            $pins = @(); $loc = $url
            for ($i = 0; $i -lt 6 -and $loc; $i++) {
                $h = ([Uri]$loc).Host
                $ip = Doh-IP $h
                if ($ip) { $pins += @("--resolve", "$($h):443:$ip") }
                $next = & $curl -s -I -o NUL -w "%{redirect_url}" -A "FreeWorks-Installer" @pins $loc
                if ($next -and $next -ne $loc) { $loc = "$next".Trim() } else { $loc = $null }
            }
            if ($pins.Count -gt 0) {
                $code = Curl-Get $url $part $pins
                if ($code -eq 0) { Ok "downloaded through encrypted DNS"; Move-Item -Force $part $dest; return }
            }
            Info "(encrypted DNS did not help either: curl code $code for $url)"
        }
        try {
            $wc = New-Object System.Net.WebClient
            $wc.Headers.Add("User-Agent", "FreeWorks-Installer")
            $wc.DownloadFile($url, $part)
            Move-Item -Force $part $dest
        } catch {
            throw ("could not download $name. Your network (or antivirus web shield) blocks GitHub's download " +
                   "server. Use another connection (for example a phone hotspot) or set this PC's DNS to " +
                   "1.1.1.1, then run the same command again - finished parts are kept.")
        }
    }

    function Sha256-Of($path) { (Get-FileHash -Algorithm SHA256 -Path $path).Hash.ToLower() }

    function Expected-Sha($assetName, $manifestHash) {
        if ($manifestHash) { return $manifestHash.ToLower() }
        try {
            $rel = Invoke-RestMethod -Uri "https://api.github.com/repos/FreeCAD/FreeCAD/releases/tags/$($FC.tag)" -Headers @{ "User-Agent" = "FreeWorks-Installer" }
            $a = $rel.assets | Where-Object { $_.name -eq $assetName } | Select-Object -First 1
            if ($a -and $a.digest -and $a.digest.StartsWith("sha256:")) { return $a.digest.Substring(7).ToLower() }
        } catch {}
        return $null
    }

    function Get-7z {
        foreach ($p in @("$env:ProgramFiles\7-Zip\7z.exe", "${env:ProgramFiles(x86)}\7-Zip\7z.exe", (Join-Path $Dl "7zr.exe"))) {
            if ($p -and (Test-Path $p)) { return $p }
        }
        try { Download "https://www.7-zip.org/a/7zr.exe" (Join-Path $Dl "7zr.exe"); return (Join-Path $Dl "7zr.exe") } catch { return $null }
    }

    # -------------------------------------------------------------- keep previous version (rollback)
    $Prev = Join-Path $InstallDir "_previous"
    if ($UpdateOnly) {
        if (Test-Path $Prev) { Remove-Item -Recurse -Force $Prev }
        New-Item -ItemType Directory -Force -Path (Join-Path $Prev "Mod") | Out-Null
        $oldVer = (Get-ItemProperty $RegKey -ErrorAction SilentlyContinue).Version
        if (-not $oldVer) { $oldVer = "unknown" }
        Set-Content -Path (Join-Path $Prev "version.txt") -Value $oldVer
        Set-Content -Path (Join-Path $Prev "freecad_version.txt") -Value $(if ($installedFC) { $installedFC } else { $FC.version })
    }
    Remove-Item -Force (Join-Path $InstallDir "rolled_back_from.txt") -ErrorAction SilentlyContinue

    # -------------------------------------------------------------- FreeCAD
    if (-not $needFreeCAD) {
        Step "FreeCAD $($FC.version) is installed - keeping it"
    } else {
        Step "Installing FreeCAD $($FC.version) (official portable build)"
        $base = "https://github.com/FreeCAD/FreeCAD/releases/download/$($FC.tag)"
        $arc = Join-Path $Dl $FC.windows_archive
        $staging = Join-Path $InstallDir "FreeCAD.new"
        if (Test-Path $staging) { Remove-Item -Recurse -Force $staging }
        $done = $false
        try {
            Download "$base/$($FC.windows_archive)" $arc
            $want = Expected-Sha $FC.windows_archive $FC.sha256.windows_archive
            if ($want) {
                $got = Sha256-Of $arc
                if ($got -ne $want) { Remove-Item -Force $arc; throw "checksum mismatch - the download was damaged (deleted, run again)" }
                Ok "checksum verified"
            } else { Info "(no published checksum for this FreeCAD build; integrity is checked while extracting)" }
            $x = Join-Path $Dl "extract"
            if (Test-Path $x) { Remove-Item -Recurse -Force $x }
            New-Item -ItemType Directory -Force -Path $x | Out-Null
            $z = Get-7z
            Info "extracting (a few minutes) ..."
            if ($z) { & $z x $arc "-o$x" -y | Out-Null } else { & tar.exe -xf $arc -C $x }
            if ($LASTEXITCODE -ne 0) { throw "extraction failed (code $LASTEXITCODE)" }
            $found = Get-ChildItem -Path $x -Recurse -Depth 3 -Filter "freecad.exe" | Where-Object { $_.Directory.Name -eq "bin" } | Select-Object -First 1
            if (-not $found) { throw "freecad.exe not found in the archive" }
            Move-Item $found.Directory.Parent.FullName $staging
            Remove-Item -Recurse -Force $x
            $done = $true
        } catch {
            Warn "portable FreeCAD failed: $($_.Exception.Message)"
        }
        if (-not $done) {
            Info "trying the official FreeCAD installer instead"
            $setup = Join-Path $Dl $FC.windows_installer
            Download "$base/$($FC.windows_installer)" $setup
            $p = Start-Process -FilePath $setup -ArgumentList "/S", "/D=$staging" -Wait -PassThru
            if (-not (Test-Path (Join-Path $staging "bin\freecad.exe"))) { throw "FreeCAD could not be installed (installer exit code $($p.ExitCode))" }
        }
        # swap in the new FreeCAD; on updates the old one is kept in _previous for rollback
        if (Test-Path $App) {
            if ($UpdateOnly) { Move-Item $App (Join-Path $Prev "FreeCAD") }
            else { Remove-Item -Recurse -Force $App }
        }
        Rename-Item $staging "FreeCAD"
        Remove-Item -Force $arc -ErrorAction SilentlyContinue
        Ok "FreeCAD $($FC.version) ready"
    }

    # -------------------------------------------------------------- branding
    Step "FreeWorks branding"
    $bin = Join-Path $App "bin"
    foreach ($f in @("branding.xml", "freeworks.png", "splash.png")) { Copy-Item -Force -Path (Join-Path $Here "branding\$f") -Destination $bin }
    Copy-Item -Force (Join-Path $Here "branding\freeworks.ico") $InstallDir
    Ok "done"

    # -------------------------------------------------------------- FreeWorks add-on
    Step "FreeWorks $Version"
    $fw = Join-Path $Mod "FreeWorks"
    if (Test-Path $fw) {
        if ($UpdateOnly) { Move-Item $fw (Join-Path $Prev "Mod\FreeWorks") } else { Remove-Item -Recurse -Force $fw }
    }
    Copy-Item -Recurse -Force (Join-Path $Here "Mod\FreeWorks") $fw
    $stamp = Join-Path $Data "icons\.freeworks"
    if (Test-Path $stamp) { Remove-Item -Force $stamp }
    Ok "installed"

    # -------------------------------------------------------------- add-ons
    if (-not $NoAddons) {
        Step "Community add-ons"
        $list = @($manifest.addons)
        if ($WithRender) { $list += @($manifest.optional_addons | Where-Object { $_.name -eq "Render" }) }
        foreach ($a in $list) {
            try {
                $zip = Join-Path $Dl ("addon_" + $a.name + ".zip")
                if (Test-Path $zip) { Remove-Item -Force $zip }
                Download ("https://github.com/" + $a.repo + "/archive/" + $a.ref + ".zip") $zip
                $x = Join-Path $Dl ("x_" + $a.name)
                if (Test-Path $x) { Remove-Item -Recurse -Force $x }
                Expand-Archive -Path $zip -DestinationPath $x -Force
                $inner = Get-ChildItem -Path $x -Directory | Select-Object -First 1
                $dest = Join-Path $Mod $a.name
                if (Test-Path $dest) {
                    if ($UpdateOnly) { Move-Item $dest (Join-Path $Prev ("Mod\" + $a.name)) } else { Remove-Item -Recurse -Force $dest }
                }
                Move-Item $inner.FullName $dest
                Remove-Item -Recurse -Force $x, $zip
                Ok ("{0,-11} {1}" -f $a.name, $a.purpose)
            } catch {
                Warn "$($a.name) could not be updated: $($_.Exception.Message) (keeping the installed copy)"
            }
        }
    }

    # -------------------------------------------------------------- projects folder
    $docs = [Environment]::GetFolderPath("MyDocuments")
    $projects = Join-Path $docs "FreeWorks"
    New-Item -ItemType Directory -Force -Path $projects, (Join-Path $projects "Macros") | Out-Null

    # -------------------------------------------------------------- launcher
    Step "Launcher"
    $launcher = Join-Path $InstallDir "FreeWorks.exe"
    $src = @"
using System;
using System.Diagnostics;
using System.IO;
using System.Runtime.InteropServices;
public static class FreeWorksLauncher {
    [DllImport("user32.dll")] static extern short GetAsyncKeyState(int vKey);
    [STAThread]
    public static void Main(string[] args) {
        string root = AppDomain.CurrentDomain.BaseDirectory;
        bool safe = (GetAsyncKeyState(0x10) & 0x8000) != 0;   // Shift held at launch = Safe Mode
        ProcessStartInfo psi = new ProcessStartInfo(Path.Combine(root, "FreeCAD", "bin", "freecad.exe"));
        psi.UseShellExecute = false;
        string projects = Path.Combine(Environment.GetFolderPath(Environment.SpecialFolder.MyDocuments), "FreeWorks");
        try { Directory.CreateDirectory(projects); psi.WorkingDirectory = projects; }
        catch { psi.WorkingDirectory = Path.Combine(root, "FreeCAD", "bin"); }
        psi.EnvironmentVariables["FREECAD_USER_HOME"] = Path.Combine(root, "UserData");
        string a = "";
        foreach (string s in args) {
            if (s == "--safe") { safe = true; continue; }
            a += "\"" + s + "\" ";
        }
        psi.Arguments = a;
        if (safe) { psi.EnvironmentVariables["FREEWORKS_SAFE"] = "1"; }
        try { Process.Start(psi); }
        catch (Exception e) { File.WriteAllText(Path.Combine(root, "launcher-error.txt"), e.ToString()); }
    }
}
"@
    $made = $false
    try {
        $tmpExe = Join-Path $Dl "FreeWorks.exe"
        if (Test-Path $tmpExe) { Remove-Item -Force $tmpExe }
        $cp = New-Object System.CodeDom.Compiler.CompilerParameters
        $cp.GenerateExecutable = $true
        $cp.GenerateInMemory = $false
        $cp.OutputAssembly = $tmpExe
        $cp.CompilerOptions = "/target:winexe /win32icon:`"$(Join-Path $InstallDir 'freeworks.ico')`""
        $cp.MainClass = "FreeWorksLauncher"
        Add-Type -TypeDefinition $src -Language CSharp -CompilerParameters $cp | Out-Null
        Copy-Item -Force $tmpExe $launcher
        $made = Test-Path $launcher
    } catch { Warn "could not build FreeWorks.exe ($($_.Exception.Message)); using FreeWorks.cmd" }
    $cmd = Join-Path $InstallDir "FreeWorks.cmd"
    Set-Content -Path $cmd -Encoding ASCII -Value @(
        "@echo off",
        "set FREECAD_USER_HOME=%~dp0UserData",
        "set ARGS=%*",
        "if /i `"%~1`"==`"--safe`" (set FREEWORKS_SAFE=1& set ARGS=%ARGS:--safe=%)",
        "if not exist `"%USERPROFILE%\Documents\FreeWorks`" mkdir `"%USERPROFILE%\Documents\FreeWorks`"",
        "cd /d `"%USERPROFILE%\Documents\FreeWorks`"",
        "start `"`" `"%~dp0FreeCAD\bin\freecad.exe`" %ARGS%"
    )
    if (-not $made) { $launcher = $cmd }
    Ok $launcher

    # -------------------------------------------------------------- shortcuts
    if (-not $NoShortcuts) {
        $sh = New-Object -ComObject WScript.Shell
        foreach ($dir in @([Environment]::GetFolderPath("Desktop"), [Environment]::GetFolderPath("Programs"))) {
            $lnk = $sh.CreateShortcut((Join-Path $dir "FreeWorks.lnk"))
            $lnk.TargetPath = $launcher
            $lnk.WorkingDirectory = $InstallDir
            $lnk.IconLocation = (Join-Path $InstallDir "freeworks.ico") + ",0"
            $lnk.Description = "FreeWorks - SolidWorks-style CAD"
            if ($launcher -like "*.cmd") { $lnk.WindowStyle = 7 }
            $lnk.Save()
        }
        $safeLnk = $sh.CreateShortcut((Join-Path ([Environment]::GetFolderPath("Programs")) "FreeWorks (Safe Mode).lnk"))
        $safeLnk.TargetPath = $launcher
        $safeLnk.Arguments = "--safe"
        $safeLnk.WorkingDirectory = $InstallDir
        $safeLnk.IconLocation = (Join-Path $InstallDir "freeworks.ico") + ",0"
        $safeLnk.Description = "FreeWorks without the FreeWorks interface (plain FreeCAD) - for troubleshooting"
        $safeLnk.Save()
        Ok "Desktop and Start Menu shortcuts (+ Safe Mode)"
    }

    # -------------------------------------------------------------- registration
    foreach ($f in @("uninstall.ps1", "README.md", "versions.json", "CHANGELOG.md")) {
        Copy-Item -Force (Join-Path $Here $f) $InstallDir -ErrorAction SilentlyContinue
    }
    New-Item -Path $RegKey -Force | Out-Null
    Set-ItemProperty -Path $RegKey -Name InstallDir -Value $InstallDir
    Set-ItemProperty -Path $RegKey -Name Version -Value $Version
    Set-ItemProperty -Path $RegKey -Name FreeCADVersion -Value $FC.version
    Set-ItemProperty -Path $RegKey -Name ProjectsDir -Value $projects
    Set-ItemProperty -Path $RegKey -Name UpdatedOn -Value (Get-Date -Format "yyyy-MM-dd HH:mm")
    if ($UpdateOnly -and (Test-Path (Join-Path $Prev "version.txt"))) {
        Set-ItemProperty -Path $RegKey -Name PreviousVersion -Value (Get-Content (Join-Path $Prev "version.txt") -TotalCount 1)
    }
    New-Item -Path $UninstKey -Force | Out-Null
    $size = [int]((Get-ChildItem $InstallDir -Recurse -File -ErrorAction SilentlyContinue | Measure-Object Length -Sum).Sum / 1KB)
    $vals = @{
        DisplayName = "FreeWorks"; DisplayVersion = $Version; Publisher = "FreeWorks (open source)";
        DisplayIcon = (Join-Path $InstallDir "freeworks.ico"); InstallLocation = $InstallDir;
        UninstallString = "powershell.exe -NoProfile -ExecutionPolicy Bypass -File `"$(Join-Path $InstallDir 'uninstall.ps1')`"";
        URLInfoAbout = "https://github.com/scp15156402/FreeWorks"
    }
    foreach ($k in $vals.Keys) { Set-ItemProperty -Path $UninstKey -Name $k -Value $vals[$k] }
    Set-ItemProperty -Path $UninstKey -Name EstimatedSize -Value $size -Type DWord
    Set-ItemProperty -Path $UninstKey -Name NoModify -Value 1 -Type DWord
    Set-ItemProperty -Path $UninstKey -Name NoRepair -Value 1 -Type DWord

    Step ("FreeWorks $Version is " + $(if ($UpdateOnly) { "updated" } else { "installed" }))
    Info "Program:   $InstallDir"
    Info "Projects:  $projects   (never touched by updates or uninstall)"
    Info "Update:    run the same one-line command again, or Help > Check for FreeWorks Updates"
    if ($UpdateOnly) { Info "Rollback:  Help > Roll Back to Previous Version (keeps your projects)" }
    Info "Uninstall: Windows Settings > Apps > FreeWorks (projects are kept)"
} catch {
    Write-Host ""
    Write-Host "ERROR: $($_.Exception.Message)" -ForegroundColor Red
    Write-Host "Log: $(Join-Path $InstallDir 'install.log')" -ForegroundColor Red
    $exitCode = 1
} finally {
    try { Stop-Transcript | Out-Null } catch {}
}
exit $exitCode
