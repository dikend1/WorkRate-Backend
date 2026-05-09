from fastapi import APIRouter,Depends,HTTPException,Query
from sqlalchemy.ext.asyncio import AsyncSession
from app.db.session import get_db
from datetime import datetime
from app.schemas.company_schema import CompanyPageResponse, CompanyResponse,CompanyCreate,CompanyUpdate
from app.services.company_service import CompanyService
from app.core.roles import require_admin
from typing import List


router = APIRouter(prefix="/companies", tags=["Companies"])


# Dependency для сервисов
def get_company_service(db:AsyncSession = Depends(get_db)):
    return CompanyService(db)


@router.post("/",response_model=CompanyResponse)
async def create_company(
    company: CompanyCreate,
    company_service: CompanyService = Depends(get_company_service),
    user = Depends(require_admin)
):
    return await company_service.create_company(company)

@router.get("/", response_model=List[CompanyResponse])
async def get_companies(
    name: str | None = Query(None),
    location: str | None = Query(None),
    industry: str | None = Query(None),
    min_rating: float | None = Query(None, ge=0),
    start_date: datetime | None = Query(None),
    end_date: datetime | None = Query(None),
    company_service: CompanyService = Depends(get_company_service)
):
    return await company_service.get_all_companies(
        name=name,
        location=location,
        industry=industry,
        min_rating=min_rating,
        start_date=start_date,
        end_date=end_date
    )

@router.get("/{company_id}/page", response_model=CompanyPageResponse)
async def get_company_page(
    company_id:int,
    company_service: CompanyService = Depends(get_company_service)
):
    company_page = await company_service.get_company_page(company_id)
    if not company_page:
        raise HTTPException(status_code=404,detail="Company not found")
    return company_page

@router.get("/{company_id}",response_model=CompanyResponse)
async def get_company(
    company_id:int,
    company_service: CompanyService = Depends(get_company_service)
):
    company = await company_service.get_company(company_id)
    if not company:
        raise HTTPException(status_code=404,detail="Company not found")
    return company

@router.patch("/{company_id}",response_model=CompanyResponse)
async def update_company(
    company_id:int,
    company: CompanyUpdate,
    company_service: CompanyService = Depends(get_company_service),
    _user = Depends(require_admin)
):
    updated_company = await company_service.update_company(company_id,company)
    if not updated_company:
        raise HTTPException(status_code=404,detail="Company not found")
    return updated_company

@router.delete("/{company_id}")
async def delete_company(
    company_id:int,
    company_service:CompanyService = Depends(get_company_service),
    _user = Depends(require_admin)
):
    deleted = await company_service.delete_company(company_id)
    if not deleted:
        raise HTTPException(status_code=404,detail="Company not found")
    return {"message": "Company deleted"}
