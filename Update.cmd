@echo off
rem Update FreeWorks to the newest version (same as the one-line command). Projects and settings are kept.
powershell.exe -NoProfile -ExecutionPolicy Bypass -Command "[Net.ServicePointManager]::SecurityProtocol='Tls12'; iex $(try{irm https://raw.githubusercontent.com/scp15156402/FreeWorks/main/get.ps1 -TimeoutSec 20}catch{irm https://api.github.com/repos/scp15156402/FreeWorks/contents/get.ps1 -Headers @{Accept='application/vnd.github.raw'}})"
echo.
pause
