@echo off
title Logminer - Collecte Windows privilegiee
cd /d "F:\Cours\TFE"
powershell.exe -NoProfile -ExecutionPolicy Bypass -File "F:\Cours\TFE\scripts\collect_windows_events.ps1" -Days 2 -RawDirectory "data\raw\windows_events_admin" -OutputDirectory "data\processed" -CopyLogs "Application,System,Security"
echo.
echo Collecte terminee. Vous pouvez fermer cette fenetre.
pause
