@echo off
setlocal

set "PROJECT_DIR=C:\Users\Usuario\Documents\New project"
set "BACKEND_DIR=%PROJECT_DIR%\backend"
set "FRONTEND_DIR=%PROJECT_DIR%\frontend\dist"

start "Expense Backend" cmd /k "cd /d "%BACKEND_DIR%" && py -3 -m uvicorn app.main:app --reload"
start "Expense Frontend" cmd /k "cd /d "%FRONTEND_DIR%" && py -3 -m http.server 4173"

timeout /t 3 >nul
start "" http://127.0.0.1:4173

echo Sistema iniciado.
echo Frontend: http://127.0.0.1:4173
echo Backend: http://127.0.0.1:8000/api/health
endlocal
