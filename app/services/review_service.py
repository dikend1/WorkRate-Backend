from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select,update
from app.models.review_model import ReviewModel,ReviewStatus
from app.models.company_model import CompanyModel
from app.schemas.review_schema import ReviewCreate,ReviewResponse,ReviewUpdate
from typing import List,Optional
from fastapi import HTTPException

class ReviewService:
    def __init__(self,db_session:AsyncSession):
        self.db = db_session
    

    async def create_review(self,review_data:ReviewCreate,user_id: int) -> ReviewModel:
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
    
    async def get_reviews_by_company(self, company_id: int, status: str | None = None, skip: int = 0, limit: int = 10) -> List[ReviewModel]:
        query = select(ReviewModel).where(ReviewModel.company_id == company_id)
        if status:
            query = query.where(ReviewModel.status == status)
        query = query.offset(skip).limit(limit)
        result = await self.db.execute(query)
        return result.scalars().all()
    
    async def update_review(self,review_id:int,review_data:ReviewUpdate,user)->ReviewModel:
        review = await self.get_review(review_id)
        if not review:
            raise HTTPException(status_code=404, detail="Review not found")
        # Allow update for owner, admin, or company owner
        if user.role == 'admin':
            pass
        elif review.user_id == user.id:
            pass
        else:
            company_query = select(CompanyModel).where(CompanyModel.id == review.company_id)
            company_result = await self.db.execute(company_query)
            company = company_result.scalar_one_or_none()
            if not company or company.user_id != user.id:
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
        # Allow delete for owner, admin, or company owner
        if user.role == 'admin':
            pass
        elif review.user_id == user.id:
            pass
        else:
            company_query = select(CompanyModel).where(CompanyModel.id == review.company_id)
            company_result = await self.db.execute(company_query)
            company = company_result.scalar_one_or_none()
            if not company or company.user_id != user.id:
                return False
        await self.db.delete(review)
        await self.db.commit()
        return True
        
    async def moderate_review(self,review_id: int,status: ReviewStatus) ->ReviewModel:
        review = await self.get_review(review_id)
        if not review:
            raise HTTPException(status_code=404, detail="Review not found")
        review.status = status.value
        await self.db.commit()
        await self.db.refresh(review)
        return review
    
    async def get_all_reviews(self, status: str | None = None) -> List[ReviewModel]:
        query = select(ReviewModel)
        if status:
            query = query.where(ReviewModel.status == status)
        result = await self.db.execute(query)
        return result.scalars().all()