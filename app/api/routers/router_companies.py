from fastapi import APIRouter,Depends,HTTPException,Query
from sqlalchemy.ext.asyncio import AsyncSession
from app.db.session import get_db
from app.schemas.company_schema import CompanyResponse,CompanyCreate,CompanyUpdate
from app.services.company_service import CompanyService
from app.core.roles import require_admin,require_moderator
from typing import List,Optional


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

@router.get("/",response_model=CompanyResponse)
async def get_company(
    company_id:int,
    company_service: CompanyService = Depends(get_company_service)
):
    company = await company_service.get_company(company_id)
    if not company:
        raise HTTPException(status_code=404, detail="Company not found")
    return company

@router.patch("/{company_id}",response_model=CompanyUpdate)
async def update_company(
    company_id:int,
    company: CompanyUpdate,
    company_service: CompanyService = Depends(get_company_service),
    _user = Depends(require_admin)
):
    updated_company = await company_service.update_company(company_id,company)
    if not update_company:
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
    return {"message:" "Company deleted"}