from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.ext.asyncio import AsyncSession
from app.db.session import get_db
from app.models.review_model import ReviewModel  
from app.schemas.review_schema import ReviewCreate, ReviewResponse, ReviewUpdate  
from app.services.review_service import ReviewService 
from app.services.auth_service import AuthService
from typing import List

router = APIRouter(prefix="/reviews", tags=["Reviews"])

def get_review_service(db: AsyncSession = Depends(get_db)):
    return ReviewService(db)

def get_auth_service(db: AsyncSession = Depends(get_db)):
    return AuthService(db)

@router.post("/", response_model=ReviewResponse)
async def create_review(
    review: ReviewCreate,
    review_service: ReviewService = Depends(get_review_service),
    auth_service: AuthService = Depends(get_auth_service),
    token: str = Query(...)
):
    user = await auth_service.get_current_user(token)
    return await review_service.create_review(review, user.id)

@router.get("/", response_model=List[ReviewResponse])
async def get_all_reviews(
    status: str = Query(None),
    skip: int = Query(0, ge=0),
    limit: int = Query(10, ge=1, le=100),
    review_service: ReviewService = Depends(get_review_service)
):
    return await review_service.get_all_reviews(status, skip, limit)

@router.get("/{review_id}", response_model=ReviewResponse)
async def get_review(
    review_id: int,
    review_service: ReviewService = Depends(get_review_service)
):
    review = await review_service.get_review(review_id)
    if not review:
        raise HTTPException(status_code=404, detail="Review not found")
    return review

@router.get("/company/{company_id}", response_model=List[ReviewResponse])
async def get_company_reviews(
    company_id: int,
    skip: int = Query(0, ge=0),
    limit: int = Query(10, ge=1, le=100),
    review_service: ReviewService = Depends(get_review_service)
):
    return await review_service.get_reviews_by_company(company_id, skip, limit)

@router.patch("/{review_id}", response_model=ReviewResponse)
async def update_review(
    review_id: int,
    review_data: ReviewUpdate,
    review_service: ReviewService = Depends(get_review_service),
    auth_service: AuthService = Depends(get_auth_service),
    token: str = Query(...)
):
    user = await auth_service.get_current_user(token)
    return await review_service.update_review(review_id, review_data, user)

@router.delete("/{review_id}")
async def delete_review(
    review_id: int,
    review_service: ReviewService = Depends(get_review_service),
    auth_service: AuthService = Depends(get_auth_service),
    token: str = Query(...)
):
    user = await auth_service.get_current_user(token)
    deleted = await review_service.delete_review(review_id, user)
    if not deleted:
        raise HTTPException(status_code=404, detail="Review not found or not authorized")
    return {"message": "Review deleted"}