@echo off
title AutoSender v1.1 - Avvio Rapido
echo ===================================================
echo        AUTOSENDER v1.1 - Avvio in corso...
echo ===================================================
echo.

:: Torna alla cartella principale (repository)
cd %~dp0..\..

echo [INFO] Avvio dei servizi in background e dell'interfaccia...
node start.js

echo.
echo L'applicazione si e' chiusa.
pause
