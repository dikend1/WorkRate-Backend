from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from app.models.company_model import CompanyModel
from app.models.review_model import ReviewModel
from app.models.salary_model import SalaryModel
from app.schemas.company_schema import CompanyUpdate,CompanyResponse,CompanyCreate
import statistics
from datetime import datetime

class CompanyService:
    def __init__(self,db_session:AsyncSession):
        self.db = db_session
    
    async def create_company(self,company_data: CompanyCreate) -> CompanyModel:
        company = CompanyModel(**company_data.model_dump())
        self.db.add(company)
        await self.db.commit()
        await self.db.refresh(company)
        return company
    
    async def get_company(self,company_id:int)->CompanyModel:
        query = select(CompanyModel).where(CompanyModel.id == company_id)
        result = await self.db.execute(query)
        return result.scalar_one_or_none()

    async def get_all_companies(
        self,
        location: str | None = None,
        industry: str | None = None,
        min_rating: float | None = None,
        name: str | None = None,
        start_date: datetime | None = None,
        end_date: datetime | None = None,
    ) -> list[CompanyModel]:
        query = select(CompanyModel)
        if location:
            query = query.where(CompanyModel.location.ilike(f"%{location}%"))
        if industry:
            query = query.where(CompanyModel.industry.ilike(f"%{industry}%"))
        if min_rating is not None:
            query = query.where(CompanyModel.rating >= min_rating)
        if name:
            query = query.where(CompanyModel.name.ilike(f"%{name}%"))
        if start_date:
            query = query.where(CompanyModel.created_at >= start_date)
        if end_date:
            query = query.where(CompanyModel.created_at <= end_date)
        query = query.order_by(CompanyModel.rating.desc(), CompanyModel.name.asc())
        result = await self.db.execute(query)
        return result.scalars().all()

    async def get_company_page(self, company_id: int) -> dict | None:
        company = await self.get_company(company_id)
        if not company:
            return None

        reviews_result = await self.db.execute(
            select(ReviewModel)
            .where(ReviewModel.company_id == company_id)
            .order_by(ReviewModel.created_at.desc())
            .limit(10)
        )
        salaries_result = await self.db.execute(
            select(SalaryModel.salary_amount).where(SalaryModel.company_id == company_id)
        )
        salaries = salaries_result.scalars().all()
        salary_statistics = {"count": 0}
        if salaries:
            salary_statistics = {
                "count": len(salaries),
                "average": statistics.mean(salaries),
                "median": statistics.median(salaries),
                "min": min(salaries),
                "max": max(salaries),
            }

        return {
            "company": company,
            "reviews": reviews_result.scalars().all(),
            "salary_statistics": salary_statistics
        }

    async def update_company(self,company_id:int,company_data:CompanyUpdate)->CompanyModel:
        company = await self.get_company(company_id)
        if not company:
            return None
        for field,value in company_data.model_dump(exclude_unset=True).items():
            setattr(company,field,value)
        await self.db.commit()
        await self.db.refresh(company)
        return company
    
    async def delete_company(self,company_id:int)->bool:
        company = await self.get_company(company_id)
        if not company:
            return False
        await self.db.delete(company)
        await self.db.commit()
        return True
