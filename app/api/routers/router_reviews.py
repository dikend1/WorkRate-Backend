from datetime import datetime
from pathlib import Path
from uuid import uuid4

from fastapi import APIRouter, Depends, File, HTTPException, Query, UploadFile
from sqlalchemy.ext.asyncio import AsyncSession
from app.db.session import get_db
from app.schemas.review_schema import ReviewCreate, ReviewResponse, ReviewUpdate  
from app.services.review_service import ReviewService 
from app.core.dependencies import get_current_user
from app.models.user_model import UserModel
from typing import List

router = APIRouter(prefix="/reviews", tags=["Reviews"])

def get_review_service(db: AsyncSession = Depends(get_db)):
    return ReviewService(db)

@router.post("/", response_model=ReviewResponse)
async def create_review(
    review: ReviewCreate,
    review_service: ReviewService = Depends(get_review_service),
    user: UserModel = Depends(get_current_user)
):
    return await review_service.create_review(review, user.id)

@router.get("/", response_model=List[ReviewResponse])
async def get_all_reviews(
    status: str = Query(None),
    company_id: int | None = Query(None),
    min_rating: float | None = Query(None, ge=0),
    max_rating: float | None = Query(None, ge=0),
    is_current_employee: bool | None = Query(None),
    start_date: datetime | None = Query(None),
    end_date: datetime | None = Query(None),
    skip: int = Query(0, ge=0),
    limit: int = Query(10, ge=1, le=100),
    review_service: ReviewService = Depends(get_review_service)
):
    return await review_service.get_all_reviews(
        status=status,
        company_id=company_id,
        min_rating=min_rating,
        max_rating=max_rating,
        is_current_employee=is_current_employee,
        start_date=start_date,
        end_date=end_date,
        skip=skip,
        limit=limit
    )

@router.get("/company/{company_id}", response_model=List[ReviewResponse])
async def get_company_reviews(
    company_id: int,
    skip: int = Query(0, ge=0),
    limit: int = Query(10, ge=1, le=100),
    review_service: ReviewService = Depends(get_review_service)
):
    return await review_service.get_reviews_by_company(company_id, skip, limit)

@router.get("/{review_id}", response_model=ReviewResponse)
async def get_review(
    review_id: int,
    review_service: ReviewService = Depends(get_review_service)
):
    review = await review_service.get_review(review_id)
    if not review:
        raise HTTPException(status_code=404, detail="Review not found")
    return review

@router.patch("/{review_id}", response_model=ReviewResponse)
async def update_review(
    review_id: int,
    review_data: ReviewUpdate,
    review_service: ReviewService = Depends(get_review_service),
    user: UserModel = Depends(get_current_user)
):
    return await review_service.update_review(review_id, review_data, user)

@router.post("/{review_id}/attachment", response_model=ReviewResponse)
async def upload_review_attachment(
    review_id: int,
    file: UploadFile = File(...),
    review_service: ReviewService = Depends(get_review_service),
    user: UserModel = Depends(get_current_user)
):
    upload_dir = Path("uploads/reviews")
    upload_dir.mkdir(parents=True, exist_ok=True)
    suffix = Path(file.filename or "").suffix
    filename = f"{review_id}_{uuid4().hex}{suffix}"
    file_path = upload_dir / filename
    file_path.write_bytes(await file.read())
    return await review_service.set_attachment(review_id, f"/uploads/reviews/{filename}", user)

@router.delete("/{review_id}")
async def delete_review(
    review_id: int,
    review_service: ReviewService = Depends(get_review_service),
    user: UserModel = Depends(get_current_user)
):
    deleted = await review_service.delete_review(review_id, user)
    if not deleted:
        raise HTTPException(status_code=404, detail="Review not found or not authorized")
    return {"message": "Review deleted"}
