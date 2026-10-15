@echo off
setlocal
cd /d "%~dp0"
if exist "..\..\work\deps" set "PYTHONPATH=%~dp0..\..\work\deps"
if exist ".venv\Scripts\python.exe" (.venv\Scripts\python.exe backend.py) else (python backend.py)
pause
