@echo off
setlocal

set "BACKEND_DIR=C:\Users\Usuario\Documents\New project\backend"
start "Expense Backend" cmd /k "cd /d "%BACKEND_DIR%" && py -3 -m uvicorn app.main:app --reload"

echo Backend iniciado em http://127.0.0.1:8000
endlocal
