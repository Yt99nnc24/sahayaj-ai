@echo off
setlocal
cd /d "%~dp0"
rem A separate fictional database; existing clinic records are not changed.
set "SAHAYAJ_DATABASE=%~dp0instance\demo.db"
set "SAHAYAJ_PORT=5015"
set "SAHAYAJ_SECURE_COOKIE=0"
if exist "..\..\work\deps" set "PYTHONPATH=%~dp0..\..\work\deps"
if exist ".venv\Scripts\python.exe" (set "SAHAYAJ_PYTHON=.venv\Scripts\python.exe") else (set "SAHAYAJ_PYTHON=python")
%SAHAYAJ_PYTHON% backend.py --demo
if errorlevel 1 goto failed
echo Open http://127.0.0.1:5015/ - General / unsure branch has the demo doctor.
echo Change the doctor's branch in My profile to test another medical branch.
%SAHAYAJ_PYTHON% backend.py
:failed
pause
