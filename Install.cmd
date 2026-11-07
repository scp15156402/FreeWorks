@echo off
rem Install FreeWorks from this folder (D:\FreeWorks if drive D: exists, otherwise your user folder)
powershell.exe -NoProfile -ExecutionPolicy Bypass -File "%~dp0install.ps1" %*
echo.
pause
