@echo off
rem Update FreeWorks and the add-ons, keeping FreeCAD and your settings
powershell.exe -NoProfile -ExecutionPolicy Bypass -File "%~dp0install.ps1" -InstallDir "D:\FreeWorks" -UpdateOnly %*
echo.
pause
