### config.py - all backend settings (from environment / .env)
### no real secrets here; put them in 09_backend/.env

import os
from pathlib import Path

try:
    from dotenv import load_dotenv
    load_dotenv(Path(__file__).parent / ".env")
except ImportError:
    pass

### data folders of each stage (04-08)
BASE_DIR = Path(__file__).resolve().parent
ROOT_DIR = BASE_DIR.parent
TRAIN_DATA = ROOT_DIR / "04_ai_model_selection" / "data" / "train_text.json"
MODEL_DIR = ROOT_DIR / "04_ai_model_selection" / "models"
KB_DIR = ROOT_DIR / "05_retrieval_knowledge" / "data"
INDEX_DIR = ROOT_DIR / "05_retrieval_knowledge" / "index"
LOG_DATA_DIR = ROOT_DIR / "07_response_logging" / "data"
EVAL_DIR = ROOT_DIR / "08_monitoring_deployment" / "data"


def env(name, default):
    ### read an env value and convert it to the default's type
    value = os.getenv(name)
    if value is None or value == "":
        return default
    if isinstance(default, bool):
        return value.lower() in ("1", "true", "yes")
    if isinstance(default, int):
        return int(value)
    if isinstance(default, float):
        return float(value)
    return value


### 02 API / Backend
DATABASE_PATH = env("DATABASE_PATH", str(LOG_DATA_DIR / "app.db"))
CORS_ALLOWED_ORIGINS = env("CORS_ALLOWED_ORIGINS", "http://localhost:3000").split(",")
AUTH_ENABLED = env("AUTH_ENABLED", False)
JWT_SECRET_KEY = env("JWT_SECRET_KEY", "dev-only-change-me")
JWT_ALGORITHM = env("JWT_ALGORITHM", "HS256")
MAX_UPLOAD_MB = env("MAX_UPLOAD_MB", 10)
RATE_LIMIT_PER_MINUTE = env("RATE_LIMIT_PER_MINUTE", 20)
MAX_MESSAGE_CHARS = 2000

### 03 Router
ROUTE_CONFIDENCE_MIN = env("ROUTE_CONFIDENCE_MIN", 0.7)
CLARIFY_THRESHOLD = env("CLARIFY_THRESHOLD", 0.5)
MAX_CONTEXT_TOKENS = env("MAX_CONTEXT_TOKENS", 2000)

### 04 Engines / Local AI
ENGINE_TIMEOUT_MS = env("ENGINE_TIMEOUT_MS", 8000)
LOCAL_MODEL_DEVICE = env("LOCAL_MODEL_DEVICE", "cuda")

### 05 Retrieval
EMBEDDING_MODEL = env("EMBEDDING_MODEL", "BAAI/bge-m3")
RERANKER_MODEL = env("RERANKER_MODEL", "BAAI/bge-reranker-v2-m3")
RERANK_ENABLED = env("RERANK_ENABLED", True)
THAI_TOKENIZER_ENGINE = env("THAI_TOKENIZER_ENGINE", "newmm")
CHUNK_SIZE_TOKENS = env("CHUNK_SIZE_TOKENS", 500)
CHUNK_OVERLAP_TOKENS = env("CHUNK_OVERLAP_TOKENS", 50)
RETRIEVAL_TOP_K = env("RETRIEVAL_TOP_K", 20)
RERANK_TOP_N = env("RERANK_TOP_N", 5)
RRF_K = env("RRF_K", 60)
RERANK_MIN_SCORE = env("RERANK_MIN_SCORE", 0.05)

### 06 Generation (no API key = offline mode, answers taken from documents)
### API key: paste it in 09_backend/.env (the "API key" block), never here
OPENAI_API_KEY = env("OPENAI_API_KEY", "")
GENERATION_MODEL = env("GENERATION_MODEL", "gpt-4o-mini")
TEMPERATURE_REGULATION = env("TEMPERATURE_REGULATION", 0.2)
TEMPERATURE_GENERAL = env("TEMPERATURE_GENERAL", 0.7)
MAX_OUTPUT_TOKENS = env("MAX_OUTPUT_TOKENS", 800)
CITATION_REQUIRED = env("CITATION_REQUIRED", True)
STAFF_CONTACT_URL = env("STAFF_CONTACT_URL", "https://example.ac.th/contact")

### 07 Response / Log
HISTORY_TURNS = env("HISTORY_TURNS", 10)
FEEDBACK_WEBHOOK_URL = env("FEEDBACK_WEBHOOK_URL", "")
RETENTION_DAYS_CONVERSATION = env("RETENTION_DAYS_CONVERSATION", 180)
RETENTION_DAYS_UPLOADS = env("RETENTION_DAYS_UPLOADS", 30)

### 08 Monitoring
LOG_LEVEL = env("LOG_LEVEL", "INFO")
