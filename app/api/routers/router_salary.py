from datetime import datetime
from fastapi import APIRouter,Depends,HTTPException,Query
from sqlalchemy.ext.asyncio import AsyncSession
from app.db.session import get_db
from app.core.dependencies import get_current_user
from app.models.user_model import UserModel
from app.schemas.salary_schema import SalaryCreate,SalaryResponse,SalaryUpdate
from app.services.salary_service import SalaryService
from typing import List

router = APIRouter(prefix="/salaries",tags=["Salaries"])


def get_salary_service(db:AsyncSession = Depends(get_db)):
    return SalaryService(db)

@router.post('/',response_model=SalaryResponse)
async def create_salary(
    salary:SalaryCreate,
    salary_service:SalaryService = Depends(get_salary_service),
    user: UserModel = Depends(get_current_user)
):
    return await salary_service.create_salary(salary,user.id)

@router.get('/', response_model=List[SalaryResponse])
async def get_salaries(
    company_id: int | None = Query(None),
    position: str | None = Query(None),
    location: str | None = Query(None),
    currency: str | None = Query(None),
    min_salary: float | None = Query(None, ge=0),
    max_salary: float | None = Query(None, ge=0),
    min_experience: float | None = Query(None, ge=0),
    max_experience: float | None = Query(None, ge=0),
    employment_type: str | None = Query(None),
    start_date: datetime | None = Query(None),
    end_date: datetime | None = Query(None),
    skip: int = Query(0, ge=0),
    limit: int = Query(20, ge=1, le=100),
    salary_service: SalaryService = Depends(get_salary_service)
):
    return await salary_service.get_all_salaries(
        company_id=company_id,
        position=position,
        location=location,
        currency=currency,
        min_salary=min_salary,
        max_salary=max_salary,
        min_experience=min_experience,
        max_experience=max_experience,
        employment_type=employment_type,
        start_date=start_date,
        end_date=end_date,
        skip=skip,
        limit=limit
    )

@router.get('/company/{company_id}',response_model=List[SalaryResponse])
async def get_company_salary(
    company_id:int,
    position: str | None = None,
    skip: int = Query(0,ge=0),
    limit: int = Query(10,ge=1,le=100),
    salary_service: SalaryService = Depends(get_salary_service)
):
    return await salary_service.get_salary_by_company(company_id,position,skip,limit)

@router.get('/statistics')
async def get_salary_statistics(
    company_id:int | None = None,
    position: str | None = None,
    salary_service: SalaryService = Depends(get_salary_service)
):
    return await salary_service.get_salary_statistics(company_id,position)

@router.patch('/{salary_id}',response_model=SalaryResponse)
async def update_salary(
    salary_id:int,
    salary_data:SalaryUpdate,
    salary_service:SalaryService = Depends(get_salary_service),
    user: UserModel = Depends(get_current_user)
):
    return await salary_service.update_salary(salary_id,salary_data,user)

@router.delete('/{salary_id}')
async def delete_salary(
    salary_id:int,
    salary_service: SalaryService = Depends(get_salary_service),
    user: UserModel = Depends(get_current_user)
):
    deleted_salary = await salary_service.delete_salary(salary_id,user)
    if not deleted_salary:
        raise HTTPException(status_code=404,detail="Salary not found or not authorized")
    return {"message":"Salary deleted"}
