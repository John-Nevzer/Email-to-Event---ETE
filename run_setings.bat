@echo off
REM -------------------------------------------
REM Batch file pro spuštění settings.py s venv
REM -------------------------------------------

REM 1. Nastav aktuální adresář na ten, kde je tento bat soubor
cd /d %~dp0

REM 2. Zkontroluj settings.py
if not exist "settings.py" (
    echo ERROR: settings.py nebyl nalezen ve slozce %cd%
    pause
    exit /b 1
)

REM 3. Zkontroluj python.exe ve venv
if not exist "venv\Scripts\python.exe" (
    echo ERROR: python.exe nebyl nalezen ve slozce venv\Scripts
    pause
    exit /b 1
)

REM 4. Spust main.py s python.exe z venv
echo Spoustim settings.py s venv...
venv\Scripts\python.exe settings.py

REM Hotovo
pause
