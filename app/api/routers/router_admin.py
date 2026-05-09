from datetime import datetime

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.roles import require_admin, require_admin_or_moderator
from app.db.session import get_db
from app.models.review_model import ReviewStatus
from app.schemas.admin_schema import (
    AdminDashboardSchema,
    ReviewModerationSchema,
    ReviewScanResponseSchema,
)
from app.schemas.review_schema import ReviewResponse
from app.schemas.salary_schema import SalaryResponse
from app.services.admin_service import AdminService


router = APIRouter(prefix="/admin", tags=["Admin"])


def get_admin_service(db: AsyncSession = Depends(get_db)):
    return AdminService(db)


@router.get("/dashboard", response_model=AdminDashboardSchema)
async def get_dashboard(
    _user=Depends(require_admin_or_moderator),
    admin_service: AdminService = Depends(get_admin_service)
):
    return await admin_service.get_dashboard()


@router.get("/reviews", response_model=list[ReviewResponse])
async def list_reviews(
    status: str | None = Query(None),
    company_id: int | None = Query(None),
    _user=Depends(require_admin_or_moderator),
    admin_service: AdminService = Depends(get_admin_service)
):
    return await admin_service.list_reviews(status=status, company_id=company_id)


@router.patch("/reviews/{review_id}/moderate", response_model=ReviewResponse)
async def moderate_review(
    review_id: int,
    moderation_data: ReviewModerationSchema,
    _user=Depends(require_admin_or_moderator),
    admin_service: AdminService = Depends(get_admin_service)
):
    return await admin_service.moderate_review(
        review_id=review_id,
        status=ReviewStatus(moderation_data.status),
        moderator_decision=moderation_data.moderator_decision,
        ai_score=moderation_data.ai_score,
        flagged_words=moderation_data.flagged_words
    )


@router.post("/reviews/{review_id}/scan", response_model=ReviewScanResponseSchema)
async def scan_review(
    review_id: int,
    _user=Depends(require_admin_or_moderator),
    admin_service: AdminService = Depends(get_admin_service)
):
    return await admin_service.scan_review(review_id)


@router.get("/salaries", response_model=list[SalaryResponse])
async def list_salaries(
    company_id: int | None = Query(None),
    position: str | None = Query(None),
    min_salary: float | None = Query(None, ge=0),
    max_salary: float | None = Query(None, ge=0),
    employment_type: str | None = Query(None),
    start_date: datetime | None = Query(None),
    end_date: datetime | None = Query(None),
    _user=Depends(require_admin_or_moderator),
    admin_service: AdminService = Depends(get_admin_service)
):
    return await admin_service.list_salaries(
        company_id=company_id,
        position=position,
        min_salary=min_salary,
        max_salary=max_salary,
        employment_type=employment_type,
        start_date=start_date,
        end_date=end_date
    )


@router.delete("/salaries/{salary_id}")
async def delete_salary(
    salary_id: int,
    _user=Depends(require_admin),
    admin_service: AdminService = Depends(get_admin_service)
):
    deleted = await admin_service.delete_salary(salary_id)
    if not deleted:
        raise HTTPException(status_code=404, detail="Salary not found")
    return {"message": "Salary deleted"}
