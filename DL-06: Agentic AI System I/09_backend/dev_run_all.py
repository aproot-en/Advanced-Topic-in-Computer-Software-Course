### dev_run_all.py - developer helper only (not the real orchestrator)
### starts the backend (uvicorn --reload) and the frontend (npm run dev)
### Run: python 09_backend/dev_run_all.py, open http://localhost:3000 (Ctrl+C to stop)
### (normal users: web_app_std.bat at the project root)

import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
NPM = "npm.cmd" if sys.platform == "win32" else "npm"

### --reload-dir: reload when files in folders 02-09 change
reload_dirs = []
for name in ["02_api_backend", "03_ai_router_agent", "04_ai_model_selection", "05_retrieval_knowledge",
             "06_llm_generation", "07_response_logging", "08_monitoring_deployment", "09_backend"]:
    reload_dirs += ["--reload-dir", str(ROOT / name)]

processes = [
    subprocess.Popen([sys.executable, "-m", "uvicorn", "main:app", "--app-dir",
                      str(ROOT / "02_api_backend"), "--reload", *reload_dirs, "--port", "8000"],
                     cwd=ROOT / "09_backend"),
    subprocess.Popen([NPM, "run", "dev"], cwd=ROOT / "01_web_app" / "frontend"),
]
print("backend  : http://localhost:8000/docs")
print("frontend : http://localhost:3000")
try:
    for p in processes:
        p.wait()
except KeyboardInterrupt:
    for p in processes:
        p.terminate()
