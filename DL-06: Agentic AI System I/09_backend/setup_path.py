### setup_path.py - lets files in folders 02-09 import each other
### folder names start with a digit, so they can't be Python packages
### fix: add every folder to sys.path and import by file name (import router_agent)
### scripts run directly (main.py, ingest.py, ...) import this first

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
STAGE_FOLDERS = [
    "09_backend",               ### config, schemas, thai_text, embedder (shared)
    "02_api_backend",           ### main.py (FastAPI)
    "03_ai_router_agent",       ### router_agent.py
    "04_ai_model_selection",    ### engines.py, local_ai.py, train_local_ai.py
    "05_retrieval_knowledge",   ### ingest.py, retrieval.py, import_curriculum.py
    "06_llm_generation",        ### generation.py
    "07_response_logging",      ### response_log.py
    "08_monitoring_deployment", ### monitoring.py, evaluate.py
]

for name in STAGE_FOLDERS:
    path = str(ROOT / name)
    if path not in sys.path:
        sys.path.append(path)
