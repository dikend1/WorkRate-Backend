from fastapi import APIRouter,Depends,HTTPException,Query
from sqlalchemy.ext.asyncio import AsyncSession
from app.db.session import get_db
from app.models.salary_model import SalaryModel
from app.schemas.salary_schema import SalaryCreate,SalaryResponse,SalaryUpdate
from app.services.salary_service import SalaryService
from app.services.auth_service import AuthService
from typing import List

router = APIRouter(prefix="/salaries",tags=["Salaries"])


def get_salary_service(db:AsyncSession = Depends(get_db)):
    return SalaryService(db)

def get_auth_service(db:AsyncSession = Depends(get_db)):
    return AuthService(db)

@router.post('/',response_model=SalaryResponse)
async def create_salary(
    salary:SalaryCreate,
    salary_service:SalaryService = Depends(get_salary_service),
    auth_service: AuthService = Depends(get_auth_service),
    token: str = Query(...)
):
    # Логируем входящие данные для отладки
    print(f"Создание salary: {salary.model_dump()}")
    user = await auth_service.get_current_user(token)
    return await salary_service.create_salary(salary,user.id)

@router.get('/company/{company_id}',response_model=List[SalaryResponse])
async def get_company_salary(
    company_id:int,
    position: str | None = None,
    skip: int = Query(0,ge=0),
    limit: int = Query(10,ge=1,le=100),
    salary_service: SalaryService = Depends(get_salary_service)
):
    return await salary_service.get_salary_by_company(company_id,position,skip,limit)

@router.patch('/{salary_id}',response_model=SalaryResponse)
async def update_salary(
    salary_id:int,
    salary_data:SalaryUpdate,
    salary_service:SalaryService = Depends(get_salary_service),
    auth_service:AuthService = Depends(get_auth_service),
    token: str = Query(...)
):
    user = await auth_service.get_current_user(token)
    return await salary_service.update_salary(salary_id,salary_data,user)

@router.delete('/{salary_id}')
async def delete_salary(
    salary_id:int,
    salary_service: SalaryService = Depends(get_salary_service),
    auth_service: AuthService = Depends(get_auth_service),
    token: str = Query(...)
):
    user = await auth_service.get_current_user(token)
    deleted_salary = await salary_service.delete_salary(salary_id,user)
    if not deleted_salary:
        raise HTTPException(status_code=404,detail="Salary not found or not authorized")
    return {"message":"Salary deleted"}


@router.get('/statistics')
async def get_salary_statistics(
    company_id:int | None = None,
    position: str | None = None,
    salary_service: SalaryService = Depends(get_salary_service)
):
    return await salary_service.get_salary_statistics(company_id,position)
