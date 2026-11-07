@echo off
rem Update FreeWorks and the add-ons to the latest GitHub release, keeping FreeCAD and your settings
powershell.exe -NoProfile -ExecutionPolicy Bypass -Command "$s = Invoke-RestMethod -Uri 'https://raw.githubusercontent.com/scp15156402/FreeWorks/main/get.ps1' -Headers @{'User-Agent'='FreeWorks'}; & ([scriptblock]::Create($s)) -InstallDir 'D:\FreeWorks' -UpdateOnly"
echo.
pause
