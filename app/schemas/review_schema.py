from pydantic import BaseModel
from datetime import datetime, date

class ReviewBase(BaseModel):
    company_id: int
    rating: float
    title: str
    content: str
    pros: str | None = None
    cons: str | None = None
    is_current_employee: bool = True
    employment_end_date: date | None = None
    is_anonymous: bool = False
    recommendations: str | None = None
    work_location: str | None = None

class ReviewCreate(ReviewBase):
    pass

class ReviewUpdate(BaseModel):
    rating: float | None = None
    title: str | None = None
    content: str | None = None
    pros: str | None = None
    cons: str | None = None
    is_current_employee: bool | None = None
    employment_end_date: date | None = None
    is_anonymous: bool | None = None
    recommendations: str | None = None
    work_location: str | None = None

class ReviewResponse(ReviewBase):
    id: int
    user_id: int
    status: str
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True