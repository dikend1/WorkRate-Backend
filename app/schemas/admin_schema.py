from pydantic import BaseModel, Field

from app.schemas.review_schema import ReviewResponse


class ReviewStatsSchema(BaseModel):
    total: int
    pending: int
    verified: int
    rejected: int


class AdminDashboardSchema(BaseModel):
    reviews: ReviewStatsSchema
    latest_reviews: list[ReviewResponse]


class ReviewModerationSchema(BaseModel):
    status: str = Field(pattern="^(pending|verified|rejected)$")
    moderator_decision: str
    ai_score: float | None = Field(default=None, ge=0, le=1)
    flagged_words: dict | None = None


class ReviewScanResponseSchema(BaseModel):
    review_id: int
    ai_score: float
    flagged_words: dict
    requires_attention: bool
