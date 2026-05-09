from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from app.models.salary_model import SalaryModel
from app.schemas.salary_schema import SalaryCreate,SalaryUpdate
from datetime import datetime
from typing import List,Optional
import statistics
from fastapi import HTTPException

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
        return result.scalar_one_or_none()

    async def get_all_salaries(
        self,
        company_id: int | None = None,
        position: str | None = None,
        location: str | None = None,
        currency: str | None = None,
        min_salary: float | None = None,
        max_salary: float | None = None,
        min_experience: float | None = None,
        max_experience: float | None = None,
        employment_type: str | None = None,
        start_date: datetime | None = None,
        end_date: datetime | None = None,
        skip: int = 0,
        limit: int = 20
    ) -> List[SalaryModel]:
        query = select(SalaryModel)
        if company_id:
            query = query.where(SalaryModel.company_id == company_id)
        if position:
            query = query.where(SalaryModel.position.ilike(f"%{position}%"))
        if location:
            query = query.where(SalaryModel.location.ilike(f"%{location}%"))
        if currency:
            query = query.where(SalaryModel.currency == currency)
        if min_salary is not None:
            query = query.where(SalaryModel.salary_amount >= min_salary)
        if max_salary is not None:
            query = query.where(SalaryModel.salary_amount <= max_salary)
        if min_experience is not None:
            query = query.where(SalaryModel.experience_years >= min_experience)
        if max_experience is not None:
            query = query.where(SalaryModel.experience_years <= max_experience)
        if employment_type:
            query = query.where(SalaryModel.employment_type == employment_type)
        if start_date:
            query = query.where(SalaryModel.created_at >= start_date)
        if end_date:
            query = query.where(SalaryModel.created_at <= end_date)

        query = query.order_by(SalaryModel.created_at.desc()).offset(skip).limit(limit)
        result = await self.db.execute(query)
        return result.scalars().all()
    
    async def get_salary_by_company(self,company_id:int,position: Optional[str] = None, skip:int=0, limit:int=10)->List[SalaryModel]:
        query = select(SalaryModel).where(SalaryModel.company_id == company_id)
        if position:
            query = query.where(SalaryModel.position.ilike(f"%{position}%"))
        query = query.offset(skip).limit(limit)
        result = await self.db.execute(query)
        return result.scalars().all()
    
    async def update_salary(self,salary_id:int,salary_data:SalaryUpdate,user)->Optional[SalaryModel]:
        salary = await self.get_salary(salary_id)
        if not salary:
            raise HTTPException(status_code=404, detail="Salary not found")
        # Allow update for owner or admin.
        if user.role == 'admin':
            pass
        elif salary.user_id == user.id:
            pass  # owner can update
        else:
            raise HTTPException(status_code=404, detail="Salary not found")
        for field,value in salary_data.model_dump(exclude_unset=True).items():
            setattr(salary,field,value)

        await self.db.commit()
        await self.db.refresh(salary)
        return salary
    
    async def delete_salary(self,salary_id:int,user)->bool:
        salary = await self.get_salary(salary_id)
        if not salary:
            return False
        # Allow delete if user is admin or owner.
        if user.role == 'admin':
            pass
        elif salary.user_id == user.id:
            pass
        else:
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
        
        stats = {
            "count": len(salaries),
            "average": statistics.mean(salaries),
            "median": statistics.median(salaries),
            "min": min(salaries),
            "max": max(salaries)
        }
        
        if len(salaries) >= 2:
            try:
                quantiles = statistics.quantiles(salaries, n=4)
                stats["percentile_25"] = quantiles[0]
                stats["percentile_75"] = quantiles[2]
            except statistics.StatisticsError:
                stats["percentile_25"] = None
                stats["percentile_75"] = None
        else:
            stats["percentile_25"] = None
            stats["percentile_75"] = None
        
        return stats
