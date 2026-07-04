@echo off
echo ==============================================
echo    Starting ProcureMind AI Software Platform
echo ==============================================
echo.
echo Installing dependencies and launching systems...

start cmd /k "cd microservices\unified_engine && pip install -r requirements.txt && python app.py"

echo Waiting 5 seconds for the software to initialize...
timeout /t 5 /nobreak > nul

echo Opening ProcureMind AI in your browser...
start http://127.0.0.1:8000/

echo Software is running successfully! You can view the backend logs in the newly opened black command window.
pause > nul
