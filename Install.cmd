@echo off
rem FreeWorks installer - installs to D:\FreeWorks (edit the line below to change)
powershell.exe -NoProfile -ExecutionPolicy Bypass -File "%~dp0install.ps1" -InstallDir "D:\FreeWorks" %*
echo.
pause
