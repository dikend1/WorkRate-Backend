from datetime import datetime

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from app.models.review_model import ReviewModel
from app.models.company_model import CompanyModel
from app.models.salary_model import SalaryModel


class SearchService:
    def __init__(self,db_session:AsyncSession):
        self.db = db_session

    async def search_companies(self, name: str = None, industry: str = None, location: str = None,
                               min_rating: float = None, max_rating: float = None,
                               founded_year: int = None,
                               sort_by: str = None) -> list[CompanyModel]:
        query = select(CompanyModel)

        if name:
            query = query.where(CompanyModel.name.ilike(f"%{name}%"))
        if industry:
            query = query.where(CompanyModel.industry.ilike(f"%{industry}%"))
        if location:
            query = query.where(CompanyModel.location.ilike(f"%{location}%"))
        if min_rating is not None:
            query = query.where(CompanyModel.rating >= min_rating)
        if max_rating is not None:
            query = query.where(CompanyModel.rating <= max_rating)
        if founded_year:
            query = query.where(CompanyModel.founded_year == founded_year)

        if sort_by == "rating":
            query = query.order_by(CompanyModel.rating.desc())
        elif sort_by == "name":
            query = query.order_by(CompanyModel.name.asc())
        elif sort_by == "created_at":
            query = query.order_by(CompanyModel.created_at.desc())

        result = await self.db.execute(query)
        return result.scalars().all()
    
    async def search_reviews(self, text: str = None, title: str = None,
                             min_rating: int = None, max_rating: int = None,
                             start_date: datetime = None, end_date: datetime = None,
                             status: str = None, is_current_employee: bool = None) -> list[ReviewModel]:
        query = select(ReviewModel)

        if text:
            query = query.where(ReviewModel.content.ilike(f"%{text}%"))
        if title:
            query = query.where(ReviewModel.title.ilike(f"%{title}%"))
        if min_rating is not None:
            query = query.where(ReviewModel.rating >= min_rating)
        if max_rating is not None:
            query = query.where(ReviewModel.rating <= max_rating)
        if start_date:
            query = query.where(ReviewModel.created_at >= start_date)
        if end_date:
            query = query.where(ReviewModel.created_at <= end_date)
        if status:
            query = query.where(ReviewModel.status == status)
        if is_current_employee is not None:
            query = query.where(ReviewModel.is_current_employee == is_current_employee)

        result = await self.db.execute(query)
        return result.scalars().all()
    
    async def search_salaries(self, min_salary: float = None, max_salary: float = None,
                              position: str = None, company_id: int = None,
                              location: str = None, currency: str = None,
                              employment_type: str = None,
                              start_date: datetime = None, end_date: datetime = None) -> list[SalaryModel]:
        query = select(SalaryModel)

        if min_salary is not None:
            query = query.where(SalaryModel.salary_amount >= min_salary)
        if max_salary is not None:
            query = query.where(SalaryModel.salary_amount <= max_salary)
        if position:
            query = query.where(SalaryModel.position.ilike(f"%{position}%"))
        if company_id:
            query = query.where(SalaryModel.company_id == company_id)
        if location:
            query = query.where(SalaryModel.location.ilike(f"%{location}%"))
        if currency:
            query = query.where(SalaryModel.currency == currency)
        if employment_type:
            query = query.where(SalaryModel.employment_type == employment_type)
        if start_date:
            query = query.where(SalaryModel.created_at >= start_date)
        if end_date:
            query = query.where(SalaryModel.created_at <= end_date)
        result = await self.db.execute(query)
        return result.scalars().all()   
    

    

    
