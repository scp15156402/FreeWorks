@echo off
rem Update FreeWorks to the newest version (same as the one-line command). Projects and settings are kept.
powershell.exe -NoProfile -ExecutionPolicy Bypass -Command "irm https://raw.githubusercontent.com/scp15156402/FreeWorks/main/get.ps1 | iex"
echo.
pause
