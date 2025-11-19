from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select,Update
from app.models.salary_model import SalaryModel
from app.schemas.salary_schema import SalaryResponse,SalaryCreate,SalaryUpdate
from typing import List,Optional
import statistics

class SalaryService:
    def __init__(self,db_session:AsyncSession):
        self.db = db_session

    
    async def create_salary(self,salary_data:SalaryCreate,user_id:int)->SalaryModel:
        salary = SalaryModel(**salary_data.model_dump(),user_id=user_id)
        self.db.add(salary)
        await self.db.commit()
        await self.db.refresh(salary)
        return salary
    
    async def get_salary(self,salary_id:int) -> Optional[SalaryModel]:
        query = select(SalaryModel).where(SalaryModel.id == salary_id)
        result = await self.db.execute(query)
        return result.scalar_one_or_none
    
    async def get_salary_by_company(self,company_id:int,position: Optional[str] = None, skip:int=0, limit:int=10)->List[SalaryModel]:
        query = select(SalaryModel).where(SalaryModel.company_id == company_id)
        if position:
            query = query.where(SalaryModel.position.ilike(f"%{position}%"))
        query = query.offset(skip).limit(limit)
        result = await self.db.execute(query)
        return result.scalars().all()
    
    async def update_salary(self,salary_id:int,salary_data:SalaryUpdate,user_id:int)->Optional[SalaryModel]:
        salary = await self.get_salary(salary_id)
        if not salary or salary.user_id != user_id:
            return None
        for field,value in salary_data.model_dump(exclude_unset=True).items():
            setattr(salary,field,value)

        await self.db.commit()
        await self.db.refresh(salary)
        return salary
    
    async def delete_salary(self,salary_id:int,user_id:int)->bool:
        salary = await self.get_salary(salary_id)
        if not salary or salary.user_id != user_id:
            return False
        await self.db.delete(salary)
        await self.db.commit()
        return True
    
    async def get_salary_statistics(self,company_id:Optional[int] = None,position: Optional[str] = None)->dict:
        query = select(SalaryModel.salary_amount)
        if company_id:
            query = query.where(SalaryModel.company_id == company_id)
        if position:
            query = query.where(SalaryModel.position.ilike(f"%{position}%"))

        result = await self.db.execute(query)
        salaries = result.scalars().all()

        if not salaries:
            return {"error": "No salary data found"}
        return {
            "count": len(salaries),
            "average": statistics.mean(salaries),
            "median": statistics.median(salaries),
            "min": min(salaries),
            "max": max(salaries),
            "percentile_25": statistics.quantiles(salaries, n=4)[0],
            "percentile_75": statistics.quantiles(salaries, n=4)[2]
        }
