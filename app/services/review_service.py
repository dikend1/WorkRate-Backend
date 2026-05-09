from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from app.models.company_model import CompanyModel
from app.models.review_model import ReviewModel,ReviewStatus
from app.schemas.review_schema import ReviewCreate,ReviewUpdate
from datetime import datetime
from typing import List
from fastapi import HTTPException

class ReviewService:
    def __init__(self,db_session:AsyncSession):
        self.db = db_session
    

    async def create_review(self,review_data:ReviewCreate,user_id: int) -> ReviewModel:
        # Check if company exists
        company_query = select(CompanyModel).where(CompanyModel.id == review_data.company_id)
        company_result = await self.db.execute(company_query)
        company = company_result.scalar_one_or_none()
        if not company:
            raise HTTPException(status_code=404, detail=f"Company with id {review_data.company_id} not found")
        
        review = ReviewModel(
            **review_data.model_dump(),
            user_id = user_id,
            status = ReviewStatus.PENDING.value
            )
        self.db.add(review)
        await self.db.commit()
        await self.db.refresh(review)
        return review
    
    async def get_review(self,review_id:int)->ReviewModel:
        query = select(ReviewModel).where(ReviewModel.id == review_id)
        result = await self.db.execute(query)
        return result.scalar_one_or_none()
    
    async def get_reviews_by_company(self, company_id: int, skip: int = 0, limit: int = 10) -> List[ReviewModel]:
        query = select(ReviewModel).where(ReviewModel.company_id == company_id)
        query = query.order_by(ReviewModel.created_at.desc()).offset(skip).limit(limit)
        result = await self.db.execute(query)
        return result.scalars().all()
    
    async def update_review(self,review_id:int,review_data:ReviewUpdate,user)->ReviewModel:
        review = await self.get_review(review_id)
        if not review:
            raise HTTPException(status_code=404, detail="Review not found")
        # Allow update for owner or admin.
        if user.role == 'admin':
            pass
        elif review.user_id == user.id:
            pass
        else:
            raise HTTPException(status_code=404, detail="Review not found")
        for field,value in review_data.model_dump(exclude_unset=True).items():
            setattr(review,field,value)
        
        await self.db.commit()
        await self.db.refresh(review)
        return review
    
    async def delete_review(self,review_id:int,user)->bool:
        review = await self.get_review(review_id)
        if not review:
            return False
        # Allow delete for owner or admin.
        if user.role == 'admin':
            pass
        elif review.user_id == user.id:
            pass
        else:
            return False
        await self.db.delete(review)
        await self.db.commit()
        return True

    async def set_attachment(self, review_id: int, attachment_url: str, user) -> ReviewModel:
        review = await self.get_review(review_id)
        if not review:
            raise HTTPException(status_code=404, detail="Review not found")
        if user.role != "admin" and review.user_id != user.id:
            raise HTTPException(status_code=404, detail="Review not found")

        review.attachment_url = attachment_url
        await self.db.commit()
        await self.db.refresh(review)
        return review
        
    async def get_all_reviews(
        self,
        status: str | None = None,
        company_id: int | None = None,
        min_rating: float | None = None,
        max_rating: float | None = None,
        is_current_employee: bool | None = None,
        start_date: datetime | None = None,
        end_date: datetime | None = None,
        skip: int = 0,
        limit: int = 10
    ) -> List[ReviewModel]:
        query = select(ReviewModel)
        if status:
            query = query.where(ReviewModel.status == status)
        if company_id:
            query = query.where(ReviewModel.company_id == company_id)
        if min_rating is not None:
            query = query.where(ReviewModel.rating >= min_rating)
        if max_rating is not None:
            query = query.where(ReviewModel.rating <= max_rating)
        if is_current_employee is not None:
            query = query.where(ReviewModel.is_current_employee == is_current_employee)
        if start_date:
            query = query.where(ReviewModel.created_at >= start_date)
        if end_date:
            query = query.where(ReviewModel.created_at <= end_date)
        query = query.order_by(ReviewModel.created_at.desc()).offset(skip).limit(limit)
        result = await self.db.execute(query)
        return result.scalars().all()
