@echo off
setlocal
set "OLLAMA_NO_CLOUD=1"
cd /d "%~dp0"
if exist "..\..\work\deps" set "PYTHONPATH=%~dp0..\..\work\deps"
if exist ".venv\Scripts\python.exe" (.venv\Scripts\python.exe backend.py) else (python backend.py)
pause
