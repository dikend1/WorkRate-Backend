from datetime import datetime
from typing import List

from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession
from app.db.session import get_db
from app.schemas.company_schema import CompanyResponse
from app.schemas.review_schema import ReviewResponse
from app.schemas.salary_schema import SalaryResponse
from app.services.search_service import SearchService


router = APIRouter(prefix="/search",tags=["Search"])

def get_search_service(db:AsyncSession = Depends(get_db)):
    return SearchService(db)


@router.get("/companies", response_model=List[CompanyResponse])
async def search_companies(
    name: str | None = Query(None),
    industry: str | None = Query(None),
    location: str | None = Query(None),
    min_rating: float | None = Query(None, ge=0),
    max_rating: float | None = Query(None, ge=0),
    founded_year: int | None = Query(None),
    sort_by: str | None = Query(None, pattern="^(rating|name|created_at)$"),
    search_service: SearchService = Depends(get_search_service)
):
    return await search_service.search_companies(
        name=name,
        industry=industry,
        location=location,
        min_rating=min_rating,
        max_rating=max_rating,
        founded_year=founded_year,
        sort_by=sort_by
    )


@router.get("/reviews", response_model=List[ReviewResponse])
async def search_reviews(
    text: str | None = Query(None),
    title: str | None = Query(None),
    position: str | None = Query(None),
    min_rating: int | None = Query(None, ge=0),
    max_rating: int | None = Query(None, ge=0),
    start_date: datetime | None = Query(None),
    end_date: datetime | None = Query(None),
    status: str | None = Query(None),
    is_current_employee: bool | None = Query(None),
    search_service: SearchService = Depends(get_search_service)
):
    return await search_service.search_reviews(
        text=text,
        title=title or position,
        min_rating=min_rating,
        max_rating=max_rating,
        start_date=start_date,
        end_date=end_date,
        status=status,
        is_current_employee=is_current_employee
    )


@router.get("/salaries", response_model=List[SalaryResponse])
async def search_salaries(
    min_salary: float | None = Query(None, ge=0),
    max_salary: float | None = Query(None, ge=0),
    position: str | None = Query(None),
    company_id: int | None = Query(None),
    location: str | None = Query(None),
    currency: str | None = Query(None),
    employment_type: str | None = Query(None),
    start_date: datetime | None = Query(None),
    end_date: datetime | None = Query(None),
    search_service: SearchService = Depends(get_search_service)
):
    return await search_service.search_salaries(
        min_salary=min_salary,
        max_salary=max_salary,
        position=position,
        company_id=company_id,
        location=location,
        currency=currency,
        employment_type=employment_type,
        start_date=start_date,
        end_date=end_date
    )
