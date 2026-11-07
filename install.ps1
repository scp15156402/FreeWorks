<#
  FreeWorks installer - SolidWorks-style FreeCAD, self-contained in one folder.

  Default location: D:\FreeWorks
     D:\FreeWorks\FreeCAD      portable FreeCAD 1.1.4 (official build)
     D:\FreeWorks\UserData     FreeWorks settings, add-ons (Mod), macros - isolated
                                from any other FreeCAD on this PC
     D:\FreeWorks\FreeWorks.exe launcher (Desktop + Start Menu shortcuts point here)

  Usage (from Install.cmd, or a Windows PowerShell prompt):
     powershell -ExecutionPolicy Bypass -File install.ps1 [-InstallDir D:\FreeWorks]
               [-UpdateOnly] [-NoAddons] [-WithRender] [-NoShortcuts]
#>
param(
    [string]$InstallDir = "D:\FreeWorks",
    [switch]$UpdateOnly,      # refresh FreeWorks + add-ons, keep FreeCAD and settings
    [switch]$NoAddons,        # skip community add-ons
    [switch]$WithRender,      # also install the Render workbench (photo-realistic rendering)
    [switch]$NoShortcuts
)

$ErrorActionPreference = "Stop"
$ProgressPreference = "SilentlyContinue"
[Net.ServicePointManager]::SecurityProtocol = [Net.SecurityProtocolType]::Tls12

$FreeCADVersion = "1.1.4"
$FreeCADArchive = "FreeCAD_$FreeCADVersion-Windows-x86_64-py311.7z"
$FreeCADSetup   = "FreeCAD_$FreeCADVersion-Windows-x86_64-py311-installer.exe"
$FreeCADBase    = "https://github.com/FreeCAD/FreeCAD/releases/download/$FreeCADVersion"

$Addons = @(
    @{ Name = "SheetMetal"; Url = "https://github.com/shaise/FreeCAD_SheetMetal/archive/refs/heads/master.zip"; Why = "Sheet Metal tab" },
    @{ Name = "fasteners";  Url = "https://github.com/shaise/FreeCAD_FastenersWB/archive/refs/heads/master.zip"; Why = "Toolbox / standard hardware" },
    @{ Name = "Curves";     Url = "https://github.com/tomate44/CurvesWB/archive/refs/heads/main.zip"; Why = "advanced surfaces, zebra / curvature analysis" }
)
if ($WithRender) {
    $Addons += @{ Name = "Render"; Url = "https://github.com/FreeCAD/FreeCAD-render/archive/refs/heads/master.zip"; Why = "photo-realistic rendering (needs an external renderer)" }
}

$Here = Split-Path -Parent $MyInvocation.MyCommand.Path
$App  = Join-Path $InstallDir "FreeCAD"
$Data = Join-Path $InstallDir "UserData"
$Mod  = Join-Path $Data "Mod"
$Dl   = Join-Path $InstallDir "_downloads"

function Step($t)  { Write-Host ""; Write-Host "==> $t" -ForegroundColor Cyan }
function Ok($t)    { Write-Host "    $t" -ForegroundColor Green }
function Warn($t)  { Write-Host "    WARNING: $t" -ForegroundColor Yellow }

function Download($url, $dest) {
    if ((Test-Path $dest) -and ((Get-Item $dest).Length -gt 0)) { Ok "already downloaded: $(Split-Path -Leaf $dest)"; return }
    Write-Host "    downloading $(Split-Path -Leaf $dest) ..."
    $tmp = "$dest.part"
    $wc = New-Object System.Net.WebClient
    $wc.Headers.Add("User-Agent", "FreeWorks-Installer")
    $wc.DownloadFile($url, $tmp)
    Move-Item -Force $tmp $dest
    Ok ("downloaded {0:N0} MB" -f ((Get-Item $dest).Length / 1MB))
}

function Get-7z {
    foreach ($p in @("$env:ProgramFiles\7-Zip\7z.exe", "${env:ProgramFiles(x86)}\7-Zip\7z.exe")) { if ($p -and (Test-Path $p)) { return $p } }
    $z = Join-Path $Dl "7zr.exe"
    try { Download "https://www.7-zip.org/a/7zr.exe" $z; return $z } catch { Warn "could not get 7-Zip: $($_.Exception.Message)"; return $null }
}

# ---------------------------------------------------------------- checks
Write-Host "FreeWorks installer" -ForegroundColor White
$drive = Split-Path -Qualifier $InstallDir
if (-not (Test-Path "$drive\")) { throw "Drive $drive does not exist. Run with -InstallDir <folder> to choose another location." }
if (-not (Test-Path (Join-Path $Here "Mod\FreeWorks\InitGui.py"))) { throw "Run this script from the extracted FreeWorks package folder." }
New-Item -ItemType Directory -Force -Path $InstallDir, $Data, $Mod, $Dl | Out-Null
$free = (Get-PSDrive ($drive.TrimEnd(':'))).Free
if (-not $UpdateOnly -and $free -lt 3GB) { Warn ("only {0:N1} GB free on {1}; about 2.5 GB is needed" -f ($free / 1GB), $drive) }

# ---------------------------------------------------------------- FreeCAD
$exe = Join-Path $App "bin\freecad.exe"
if ($UpdateOnly -and (Test-Path $exe)) {
    Step "FreeCAD $FreeCADVersion already installed - keeping it"
} elseif (Test-Path $exe) {
    Step "FreeCAD found in $App - keeping it (delete the folder to reinstall)"
} else {
    Step "Installing FreeCAD $FreeCADVersion (portable) into $App"
    $arc = Join-Path $Dl $FreeCADArchive
    $done = $false
    try {
        Download "$FreeCADBase/$FreeCADArchive" $arc
        $x = Join-Path $Dl "extract"
        if (Test-Path $x) { Remove-Item -Recurse -Force $x }
        New-Item -ItemType Directory -Force -Path $x | Out-Null
        $z = Get-7z
        if ($z) {
            Write-Host "    extracting with 7-Zip (a few minutes) ..."
            & $z x $arc "-o$x" -y | Out-Null
            if ($LASTEXITCODE -ne 0) { throw "7-Zip exit code $LASTEXITCODE" }
        } else {
            Write-Host "    extracting with Windows tar ..."
            & tar.exe -xf $arc -C $x
            if ($LASTEXITCODE -ne 0) { throw "tar could not extract the .7z archive" }
        }
        $found = Get-ChildItem -Path $x -Recurse -Depth 3 -Filter "freecad.exe" | Where-Object { $_.Directory.Name -eq "bin" } | Select-Object -First 1
        if (-not $found) { throw "freecad.exe not found in archive" }
        $root = $found.Directory.Parent.FullName
        if (Test-Path $App) { Remove-Item -Recurse -Force $App }
        Move-Item $root $App
        Remove-Item -Recurse -Force $x
        $done = $true
        Ok "FreeCAD extracted"
    } catch {
        Warn "portable install failed ($($_.Exception.Message)); trying the official installer silently"
    }
    if (-not $done) {
        $setup = Join-Path $Dl $FreeCADSetup
        Download "$FreeCADBase/$FreeCADSetup" $setup
        $p = Start-Process -FilePath $setup -ArgumentList "/S", "/D=$App" -Wait -PassThru
        if (-not (Test-Path $exe)) { throw "FreeCAD installation failed (installer exit code $($p.ExitCode))" }
        Ok "FreeCAD installed"
    }
}

# ---------------------------------------------------------------- branding
Step "Applying FreeWorks branding (window title, icon, splash screen)"
$bin = Join-Path $App "bin"
foreach ($f in @("branding.xml", "freeworks.png", "splash.png")) { Copy-Item -Force -Path (Join-Path $Here "branding\$f") -Destination $bin }
Copy-Item -Force (Join-Path $Here "branding\freeworks.ico") $InstallDir
Ok "done"

# ---------------------------------------------------------------- FreeWorks
Step "Installing the FreeWorks add-on"
$fw = Join-Path $Mod "FreeWorks"
if (Test-Path $fw) { Remove-Item -Recurse -Force $fw }
Copy-Item -Recurse -Force (Join-Path $Here "Mod\FreeWorks") $fw
# force the icon theme to refresh after an update
$stamp = Join-Path $Data "icons\.freeworks"
if (Test-Path $stamp) { Remove-Item -Force $stamp }
Ok "FreeWorks -> $fw"

# ---------------------------------------------------------------- add-ons
if (-not $NoAddons) {
    Step "Installing community add-ons"
    foreach ($a in $Addons) {
        try {
            $zip = Join-Path $Dl ("addon_" + $a.Name + ".zip")
            if (Test-Path $zip) { Remove-Item -Force $zip }   # always fetch the latest
            Download $a.Url $zip
            $x = Join-Path $Dl ("x_" + $a.Name)
            if (Test-Path $x) { Remove-Item -Recurse -Force $x }
            Expand-Archive -Path $zip -DestinationPath $x -Force
            $inner = Get-ChildItem -Path $x -Directory | Select-Object -First 1
            $dest = Join-Path $Mod $a.Name
            if (Test-Path $dest) { Remove-Item -Recurse -Force $dest }
            Move-Item $inner.FullName $dest
            Remove-Item -Recurse -Force $x
            Ok "$($a.Name)  ($($a.Why))"
        } catch {
            Warn "$($a.Name) could not be installed: $($_.Exception.Message)"
        }
    }
}

# ---------------------------------------------------------------- launcher
Step "Creating the FreeWorks launcher"
$launcher = Join-Path $InstallDir "FreeWorks.exe"
$src = @"
using System;
using System.Diagnostics;
using System.IO;
public static class FreeWorksLauncher {
    [STAThread]
    public static void Main(string[] args) {
        string root = AppDomain.CurrentDomain.BaseDirectory;
        string exe = Path.Combine(root, "FreeCAD", "bin", "freecad.exe");
        ProcessStartInfo psi = new ProcessStartInfo(exe);
        psi.UseShellExecute = false;
        psi.WorkingDirectory = Path.Combine(root, "FreeCAD", "bin");
        psi.EnvironmentVariables["FREECAD_USER_HOME"] = Path.Combine(root, "UserData");
        string a = "";
        foreach (string s in args) { a += "\"" + s + "\" "; }
        psi.Arguments = a;
        try { Process.Start(psi); }
        catch (Exception e) { File.WriteAllText(Path.Combine(root, "launcher-error.txt"), e.ToString()); }
    }
}
"@
$made = $false
try {
    if (Test-Path $launcher) { Remove-Item -Force $launcher }
    $cp = New-Object System.CodeDom.Compiler.CompilerParameters
    $cp.GenerateExecutable = $true
    $cp.GenerateInMemory = $false
    $cp.OutputAssembly = $launcher
    $cp.CompilerOptions = "/target:winexe /win32icon:`"$(Join-Path $InstallDir 'freeworks.ico')`""
    $cp.MainClass = "FreeWorksLauncher"
    Add-Type -TypeDefinition $src -Language CSharp -CompilerParameters $cp | Out-Null
    $made = Test-Path $launcher
} catch {
    Warn "could not build FreeWorks.exe ($($_.Exception.Message)); using FreeWorks.cmd instead"
}
$cmd = Join-Path $InstallDir "FreeWorks.cmd"
Set-Content -Path $cmd -Encoding ASCII -Value @(
    "@echo off",
    "set FREECAD_USER_HOME=%~dp0UserData",
    "start `"`" `"%~dp0FreeCAD\bin\freecad.exe`" %*"
)
if (-not $made) { $launcher = $cmd }
Ok "launcher: $launcher"

# ---------------------------------------------------------------- shortcuts
if (-not $NoShortcuts) {
    Step "Creating Desktop and Start Menu shortcuts"
    $sh = New-Object -ComObject WScript.Shell
    $targets = @([Environment]::GetFolderPath("Desktop"), [Environment]::GetFolderPath("Programs"))
    foreach ($dir in $targets) {
        $lnk = $sh.CreateShortcut((Join-Path $dir "FreeWorks.lnk"))
        $lnk.TargetPath = $launcher
        $lnk.WorkingDirectory = $InstallDir
        $lnk.IconLocation = (Join-Path $InstallDir "freeworks.ico") + ",0"
        $lnk.Description = "FreeWorks - SolidWorks-style FreeCAD"
        if ($launcher -like "*.cmd") { $lnk.WindowStyle = 7 }
        $lnk.Save()
    }
    Ok "shortcuts created"
}

# ---------------------------------------------------------------- uninstaller
Copy-Item -Force (Join-Path $Here "uninstall.ps1") $InstallDir -ErrorAction SilentlyContinue
Copy-Item -Force (Join-Path $Here "README.md") $InstallDir -ErrorAction SilentlyContinue

Step "FreeWorks is installed"
Write-Host "    Start it from the Desktop shortcut or $launcher" -ForegroundColor White
Write-Host "    To update FreeWorks later: run Install.cmd again (your settings are kept)." -ForegroundColor Gray
Write-Host ""
