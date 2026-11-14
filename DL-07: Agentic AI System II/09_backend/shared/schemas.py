# schemas.py
# Shared data structures used by all modules (owned by Module 09)
# Kept simple with Pydantic

from typing import Optional
from pydantic import BaseModel, Field

# Hazard severity 0-4 (proj-prompt Appendix C)
SEVERITY_TH = ["ปกติ", "เฝ้าระวัง", "ระวัง", "เตือนภัย", "อันตรายร้ายแรง"]
SEVERITY_EN = ["Normal", "Advisory", "Watch", "Warning", "Emergency"]

# The 4 main recommendations
ACTIONS = ["NORMAL", "CHANGE_ROUTE", "DELAY", "AVOID"]


class TripRequest(BaseModel):
    """What the user enters in the trip planner form."""
    origin: str = Field(min_length=1, max_length=200)
    destination: str = Field(min_length=1, max_length=200)
    departure_time: Optional[str] = None   # ISO, e.g. 2026-11-15T08:00 (Thai time); empty = now
    travel_mode: str = "CAR"
    question: Optional[str] = Field(default=None, max_length=1000)
    lang: str = "th"


class ChatRequest(BaseModel):
    """Chat message from the user + the current map center."""
    text: str = Field(min_length=1, max_length=2000)
    lang: str = "th"
    map_lat: Optional[float] = None
    map_lon: Optional[float] = None
    conversation_id: Optional[str] = None


class FeedbackRequest(BaseModel):
    request_id: str
    category: str   # HELPFUL, INCORRECT, STALE, UNSAFE, ROUTE_ISSUE
    comment: Optional[str] = Field(default=None, max_length=1000)
