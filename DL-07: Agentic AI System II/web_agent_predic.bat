@echo off
REM ===================================================================
REM  web_agent_predic.bat
REM  Start the whole ProJ-7 Agent II system in THIS ONE window (local)
REM    01 Web App (map)   http://127.0.0.1:3000
REM    02 API / Backend   http://127.0.0.1:8000   (docs: /docs)
REM    03-08 services     ports 8001-8006
REM  Press Ctrl+C or close this window to stop everything.
REM  (Docker files are prepared in 09_backend but not used here.)
REM ===================================================================
chcp 65001 >nul
title ProJ-7 Agent II
cd /d "%~dp0"
set PYTHONIOENCODING=utf-8
set PY=.venv\Scripts\python.exe

echo.
echo  === ProJ-7 Agent II : Hazard Map + Travel Assistant ===
echo.

REM ---- 1) create the Python environment the first time ----
if not exist "%PY%" (
    echo [setup] Creating Python environment .venv ...
    where uv >nul 2>nul
    if not errorlevel 1 (
        uv venv .venv --python 3.12
        uv pip install --python "%PY%" -r 09_backend\requirements.txt
    ) else (
        python -m venv .venv
        "%PY%" -m pip install --upgrade pip
        "%PY%" -m pip install -r 09_backend\requirements.txt
    )
)
if not exist "%PY%" (
    echo ERROR: could not create .venv - please install Python 3.12 or uv first.
    pause
    exit /b 1
)

REM ---- optional free Llama API key (see 09_backend\.env.example) ----
if exist ".env" (echo [setup] .env found - Llama API is used if LLM_API_KEY is set) else (echo [setup] no .env - using rules and templates only)
echo.

REM ---- 2) start every service in this window ----
"%PY%" 09_backend\scripts\run_all.py

echo.
echo System stopped.
pause
