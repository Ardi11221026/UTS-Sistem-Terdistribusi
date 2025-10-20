from pydantic import BaseModel, Field
from typing import Any, Dict

class Event(BaseModel):
    topic: str = Field(..., min_length=1)
    event_id: str = Field(..., min_length=1)
    timestamp: str
    source: str
    payload: Dict[str, Any] = {}
