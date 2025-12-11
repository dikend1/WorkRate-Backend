from pydantic import BaseModel
from datetime import datetime
from typing import Any

class ModerationLogBase(BaseModel):
    review_id: int
    ai_score: float
    flagged_words: dict[str, Any] | None = None
    moderator_decision: str
    moderated_at: datetime

class ModerationLogCreate(ModerationLogBase):
    pass

class ModerationLogResponse(ModerationLogBase):
    id: int

    model_config = {"from_attributes": True}