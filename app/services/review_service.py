from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select,update
from app.models.review_model import ReviewModel,ReviewStatus
from app.schemas.review_schema import ReviewCreate,ReviewResponse,ReviewUpdate
from typing import List,Optional

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
        reslut = await self.db.execute(query)
        return reslut.scalar_one_or_none
    
    async def get_reviews_by_company(self, company_id: int, status: str | None = None, skip: int = 0, limit: int = 10) -> List[ReviewModel]:
        query = select(ReviewModel).where(ReviewModel.company_id == company_id)
        if status:
            query = query.where(ReviewModel.status == status)
        query = query.offset(skip).limit(limit)
        result = await self.db.execute(query)
        return result.scalars().all()
    
    async def update_review(self,review_id:int,review_data:ReviewUpdate,user_id:int)->ReviewModel:
        review = await self.get_review(review_id)
        if not review or review.user_id != user_id:
            return None
        for field,value in review_data.model_dump(exclude_unset=True).items():
            setattr(review,field,value)
        
        await self.db.commit()
        await self.db.refresh(review)
        return review
    
    async def delete_review(self,review_id:int,user_id:int)->bool:
        review = await self.get_review(review_id)
        if not review or review.user_id != user_id:
            return False
        await self.db.delete(review)
        await self.db.commit()
        return True
        
    async def moderate_review(self,review_id: int,status: ReviewStatus) ->Optional[ReviewModel]:
        review = await self.get_review(review_id)
        if not review:
            return None
        review.status = status.value
        await self.db.commit()
        await self.db.refresh(review)
        return review