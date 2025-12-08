from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime

class SalaryBase(BaseModel):
    company_id: int
    position: str
    salary_amount: float
    currency: str | None = "USD"
    experience_years: float | None = None
    location: str | None = None

class SalaryCreate(SalaryBase):
    pass

class SalaryUpdate(BaseModel):
    position: str | None = None
    salary_amount: float | None = None
    currency: str | None = None
    experience_years: float | None = None
    location: str | None = None

class SalaryResponse(SalaryBase):
    id: int
    user_id: int
    created_at: datetime

    class Config:
        from_attributes = True