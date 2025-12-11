from pydantic import BaseModel
from datetime import datetime

class CompanyBase(BaseModel):
    name:str
    description: str | None = None
    website: str | None = None
    industry: str | None = None
    location: str | None = None
    logo_url: str | None = None
    founded_year: int | None = None
    tax_contributions: float | None = None
    stock_price: float | None = None
    is_public: bool = False

class CompanyCreate(CompanyBase):
    pass

class CompanyUpdate(BaseModel):
    description: str | None = None
    website: str | None = None
    industry: str | None = None
    location: str | None = None
    logo_url: str | None = None
    founded_year: int | None = None
    tax_contributions: float | None = None
    stock_price: float | None = None
    is_public: bool | None = None

class CompanyResponse(CompanyBase):
    id:int
    rating:float
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True