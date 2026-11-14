@echo off
REM ============================================================================
REM  web_app_std.bat - Start the whole UniRAG system locally and open the app
REM
REM    backend  (FastAPI, stages 02-07)  http://localhost:8000
REM    frontend (Next.js, stage 01)      http://localhost:3000
REM
REM  Usage:
REM    web_app_std.bat          start backend + frontend (hidden), then open the browser
REM    web_app_std.bat stop     stop both servers
REM
REM  Both servers run hidden in the background (no extra terminal windows).
REM  This window closes by itself after the app opens. Server output goes to
REM  09_backend\logs\ (backend.log, backend.err.log, frontend.log, frontend.err.log).
REM  Code: stage folders 02-08 (one per PATCH), shared code + scripts in 09_backend.
REM ============================================================================
setlocal
chcp 65001 >nul
set "ROOT=%~dp0"
set "BACKEND=%ROOT%09_backend"
set "FRONTEND=%ROOT%01_web_app\frontend"
set "LOGDIR=%ROOT%09_backend\logs"
set "PIDFILE=%LOGDIR%\pids.txt"
set PYTHONIOENCODING=utf-8
set PYTHONUNBUFFERED=1
if not exist "%LOGDIR%" mkdir "%LOGDIR%"

if /i "%~1"=="stop" goto stop

echo ===== UniRAG Assistant =====

REM ---------- 1) check tools ----------
where python >nul 2>nul || (echo [ERROR] Python not found. Activate the conda env first, e.g. "conda activate tf_cpe" & pause & exit /b 1)
where node >nul 2>nul || (echo [ERROR] Node.js not found. Install Node.js 20 LTS or newer. & pause & exit /b 1)
where curl >nul 2>nul || (echo [ERROR] curl not found ^(needed to check the servers^). & pause & exit /b 1)

REM ---------- 2) first run: knowledge base index + local PyTorch models ----------
if not exist "%ROOT%05_retrieval_knowledge\index\embeddings.pt" goto setup
if not exist "%ROOT%04_ai_model_selection\models\router.pt" goto setup
goto start_backend

:setup
echo [setup] First run: building knowledge base and training local models...
python "%ROOT%05_retrieval_knowledge\import_curriculum.py" || goto setup_failed
python "%ROOT%05_retrieval_knowledge\ingest.py" || goto setup_failed
python "%ROOT%04_ai_model_selection\train_local_ai.py" || goto setup_failed
goto start_backend

:setup_failed
echo [ERROR] Setup failed. See the messages above.
pause
exit /b 1

REM ---------- 3) backend (hidden) ----------
:start_backend
curl -s -o nul http://localhost:8000/health && (echo [1/3] Backend already running.& goto start_frontend)
echo [1/3] Starting backend  http://localhost:8000
powershell -NoProfile -Command "$p = Start-Process python -ArgumentList '-m uvicorn main:app --port 8000' -WorkingDirectory '%ROOT%02_api_backend' -WindowStyle Hidden -RedirectStandardOutput '%LOGDIR%\backend.log' -RedirectStandardError '%LOGDIR%\backend.err.log' -PassThru; Add-Content -Path '%PIDFILE%' -Value $p.Id"

echo       Waiting for backend (loading AI models can take about 1 minute)...
set /a TRIES=0
:wait_backend
ping -n 4 127.0.0.1 >nul
curl -s -o nul http://localhost:8000/health && goto backend_ready
set /a TRIES+=1
if %TRIES% lss 60 goto wait_backend
echo [ERROR] Backend did not start in 3 minutes. Last lines of 09_backend\logs\backend.err.log:
powershell -NoProfile -Command "Get-Content '%LOGDIR%\backend.err.log' -Tail 15"
pause
exit /b 1
:backend_ready
echo       Backend ready.

REM ---------- 4) frontend (hidden) ----------
:start_frontend
REM point the web app at the real backend (not the mock API)
> "%FRONTEND%\.env.local" (
  echo NEXT_PUBLIC_API_BASE_URL=http://localhost:8000
  echo NEXT_PUBLIC_STAFF_CONTACT_URL=https://example.ac.th/contact
  echo NEXT_PUBLIC_DEFAULT_LOCALE=th
)
curl -s -o nul http://localhost:3000 && (echo [2/3] Frontend already running.& goto open_app)
echo [2/3] Starting frontend http://localhost:3000
if not exist "%FRONTEND%\node_modules\" (
  echo       Installing npm packages...
  pushd "%FRONTEND%"
  call npm install --no-fund --no-audit || (popd & echo [ERROR] npm install failed. & pause & exit /b 1)
  popd
)
powershell -NoProfile -Command "$p = Start-Process cmd.exe -ArgumentList '/c npx next dev -p 3000' -WorkingDirectory '%FRONTEND%' -WindowStyle Hidden -RedirectStandardOutput '%LOGDIR%\frontend.log' -RedirectStandardError '%LOGDIR%\frontend.err.log' -PassThru; Add-Content -Path '%PIDFILE%' -Value $p.Id"

set /a TRIES=0
:wait_frontend
ping -n 3 127.0.0.1 >nul
curl -s -o nul http://localhost:3000 && goto open_app
set /a TRIES+=1
if %TRIES% lss 60 goto wait_frontend
echo [ERROR] Frontend did not start in 2 minutes. Last lines of 09_backend\logs\frontend.err.log:
powershell -NoProfile -Command "Get-Content '%LOGDIR%\frontend.err.log' -Tail 15"
pause
exit /b 1

REM ---------- 5) open the app, then close this window ----------
:open_app
echo [3/3] Opening http://localhost:3000
start "" http://localhost:3000
echo.
echo  System is running in the background:
echo    App      http://localhost:3000
echo    API docs http://localhost:8000/docs
echo  Stop:  web_app_std.bat stop
echo  (this window closes in a few seconds)
ping -n 6 127.0.0.1 >nul
goto end

REM ---------- stop ----------
:stop
echo Stopping UniRAG servers...
REM 1) the processes this script started (saved PIDs, with their child processes)
if exist "%PIDFILE%" (
  for /f %%p in ('type "%PIDFILE%"') do taskkill /PID %%p /T /F >nul 2>nul
  del "%PIDFILE%" >nul 2>nul
)
REM 2) anything still listening on 8000 / 3000 (e.g. started another way)
for /f "tokens=5" %%p in ('netstat -ano ^| findstr "LISTENING" ^| findstr /c:":8000 " /c:":3000 "') do taskkill /PID %%p /T /F >nul 2>nul
echo Done.
ping -n 3 127.0.0.1 >nul

:end
endlocal
