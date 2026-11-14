### schemas.py — SHARED CONTRACT
### [C1] ChatResponse = Unified Response Schema (02 -> web app)
### [C2] EngineResult = Engine Result Schema (04 -> 06, internal)

from typing import List, Optional, Literal
from pydantic import BaseModel, Field

ResponseType = Literal["answer", "answer_with_citations", "local_task", "clarify", "decline"]
EngineName = Literal["general_ai", "university_rag", "local_ai", "none"]


### request from the web app (POST /api/chat and /api/chat/stream)
class ChatRequest(BaseModel):
    session_id: Optional[str] = None
    message: str = Field(min_length=1, max_length=2000)
    method: Literal["hybrid_rrf", "bm25", "vector"] = "hybrid_rrf"
    top_k: int = Field(default=5, ge=1, le=10)
    locale: Literal["th", "en"] = "th"
    attachments: List[str] = []


class Source(BaseModel):
    ref: int
    title: str
    url: str = ""
    page: Optional[int] = None
    published_at: str
    category: str


### [C1] Unified Response Schema
class ChatResponse(BaseModel):
    message_id: str
    session_id: str
    response_type: ResponseType
    answer: str
    clarify_options: List[str] = []
    sources: List[Source] = []
    engine_used: EngineName
    confidence: float
    data_freshness: Optional[str] = None
    degraded_services: List[str] = []
    latency_ms: int
    trace_id: str
    timestamp: str


### [C2] Engine Result Schema
class EngineResult(BaseModel):
    engine: Literal["general_ai", "university_rag", "local_ai"]
    content: Optional[str] = None
    chunks: List[dict] = []
    label: Optional[str] = None
    score: Optional[float] = None
    passthrough: bool = False
    model_version: Optional[str] = None
    latency_ms: int = 0
    error: Optional[str] = None


class FeedbackRequest(BaseModel):
    message_id: str
    rating: Literal["up", "down"]
    comment: Optional[str] = Field(default=None, max_length=500)
