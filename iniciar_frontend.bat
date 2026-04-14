@echo off
setlocal

set "FRONTEND_DIR=C:\Users\Usuario\Documents\New project\frontend\dist"
start "Expense Frontend" cmd /k "cd /d "%FRONTEND_DIR%" && py -3 -m http.server 4173"

echo Frontend iniciado em http://127.0.0.1:4173
endlocal
