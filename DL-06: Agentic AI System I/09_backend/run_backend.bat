@echo off
REM ============================================================================
REM  run_backend.bat - Run the UniRAG backend (stages 02-07) at http://localhost:8000
REM
REM  Code lives in the stage folders 02-08; 09_backend holds shared code + scripts.
REM
REM  Usage:
REM    run_backend.bat          start the API (builds index/models on first run)
REM    run_backend.bat setup    rebuild knowledge base index + retrain local models
REM    run_backend.bat test     run pytest + evaluation gate (stop the API first: GPU)
REM ============================================================================
setlocal
chcp 65001 >nul
set PYTHONIOENCODING=utf-8
set "ROOT=%~dp0.."
cd /d "%~dp0"

if /i "%~1"=="setup" goto setup
if /i "%~1"=="test" goto test

if not exist "%ROOT%\05_retrieval_knowledge\index\embeddings.pt" call :setup_steps || goto failed
if not exist "%ROOT%\04_ai_model_selection\models\router.pt" call :setup_steps || goto failed

echo Starting API at http://localhost:8000  (docs: http://localhost:8000/docs)
python -m uvicorn main:app --app-dir "%ROOT%\02_api_backend" --port 8000
goto end

:setup
call :setup_steps || goto failed
goto end

:setup_steps
echo [1/3] 05 Import curriculum (CPE RMUTT 2568) into the knowledge base
python "%ROOT%\05_retrieval_knowledge\import_curriculum.py" || exit /b 1
echo [2/3] 05 Build index (clean, chunk, embed)
python "%ROOT%\05_retrieval_knowledge\ingest.py" || exit /b 1
echo [3/3] 04 Train local PyTorch models (router, request type, risk)
python "%ROOT%\04_ai_model_selection\train_local_ai.py" || exit /b 1
exit /b 0

:test
python -m pytest -q -p no:warnings tests
python "%ROOT%\08_monitoring_deployment\evaluate.py"
goto end

:failed
echo [ERROR] Setup failed. See the messages above.
pause

:end
endlocal
