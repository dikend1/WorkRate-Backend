from datetime import datetime

from fastapi import HTTPException
from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.moderation_log_model import ModerationLog
from app.models.review_model import ReviewModel, ReviewStatus
from app.models.salary_model import SalaryModel


class AdminService:
    def __init__(self, db_session: AsyncSession):
        self.db = db_session

    async def get_dashboard(self) -> dict:
        total_reviews = await self._count_reviews()
        pending_reviews = await self._count_reviews(ReviewStatus.PENDING.value)
        verified_reviews = await self._count_reviews(ReviewStatus.VERIFIED.value)
        rejected_reviews = await self._count_reviews(ReviewStatus.REJECTED.value)

        latest_result = await self.db.execute(
            select(ReviewModel).order_by(ReviewModel.created_at.desc()).limit(10)
        )

        return {
            "reviews": {
                "total": total_reviews,
                "pending": pending_reviews,
                "verified": verified_reviews,
                "rejected": rejected_reviews,
            },
            "latest_reviews": latest_result.scalars().all()
        }

    async def list_reviews(self, status: str | None = None, company_id: int | None = None) -> list[ReviewModel]:
        query = select(ReviewModel).order_by(ReviewModel.created_at.desc())
        if status:
            query = query.where(ReviewModel.status == status)
        if company_id:
            query = query.where(ReviewModel.company_id == company_id)

        result = await self.db.execute(query)
        return result.scalars().all()

    async def moderate_review(
        self,
        review_id: int,
        status: ReviewStatus,
        moderator_decision: str,
        ai_score: float | None = None,
        flagged_words: dict | None = None
    ) -> ReviewModel:
        review = await self._get_review(review_id)
        review.status = status.value

        log = ModerationLog(
            review_id=review_id,
            ai_score=ai_score if ai_score is not None else 0.0,
            flagged_words=flagged_words,
            moderator_decision=moderator_decision,
            moderated_at=datetime.utcnow()
        )
        self.db.add(log)
        await self.db.commit()
        await self.db.refresh(review)
        return review

    async def scan_review(self, review_id: int) -> dict:
        review = await self._get_review(review_id)
        flagged = self._find_flagged_words(review.content)
        toxicity_markers = self._find_toxicity_markers(review.content)
        score = min(1.0, (len(flagged) * 0.2) + (len(toxicity_markers) * 0.1))
        return {
            "review_id": review.id,
            "ai_score": score,
            "flagged_words": {"words": flagged, "markers": toxicity_markers},
            "requires_attention": bool(flagged or toxicity_markers)
        }

    async def list_salaries(
        self,
        company_id: int | None = None,
        position: str | None = None,
        min_salary: float | None = None,
        max_salary: float | None = None,
        employment_type: str | None = None,
        start_date: datetime | None = None,
        end_date: datetime | None = None
    ) -> list[SalaryModel]:
        query = select(SalaryModel).order_by(SalaryModel.created_at.desc())
        if company_id:
            query = query.where(SalaryModel.company_id == company_id)
        if position:
            query = query.where(SalaryModel.position.ilike(f"%{position}%"))
        if min_salary is not None:
            query = query.where(SalaryModel.salary_amount >= min_salary)
        if max_salary is not None:
            query = query.where(SalaryModel.salary_amount <= max_salary)
        if employment_type:
            query = query.where(SalaryModel.employment_type == employment_type)
        if start_date:
            query = query.where(SalaryModel.created_at >= start_date)
        if end_date:
            query = query.where(SalaryModel.created_at <= end_date)

        result = await self.db.execute(query)
        return result.scalars().all()

    async def delete_salary(self, salary_id: int) -> bool:
        result = await self.db.execute(select(SalaryModel).where(SalaryModel.id == salary_id))
        salary = result.scalar_one_or_none()
        if not salary:
            return False

        await self.db.delete(salary)
        await self.db.commit()
        return True

    async def _count_reviews(self, status: str | None = None) -> int:
        query = select(func.count(ReviewModel.id))
        if status:
            query = query.where(ReviewModel.status == status)
        result = await self.db.execute(query)
        return result.scalar_one()

    async def _get_review(self, review_id: int) -> ReviewModel:
        result = await self.db.execute(select(ReviewModel).where(ReviewModel.id == review_id))
        review = result.scalar_one_or_none()
        if not review:
            raise HTTPException(status_code=404, detail="Review not found")
        return review

    def _find_flagged_words(self, text: str) -> list[str]:
        blocked_words = {"idiot", "stupid", "hate", "scam", "fraud"}
        lowered = text.lower()
        return sorted(word for word in blocked_words if word in lowered)

    def _find_toxicity_markers(self, text: str) -> list[str]:
        markers = {
            "personal_attack": ["manager is", "boss is", "coworker is"],
            "legal_accusation": ["illegal", "criminal", "stole"],
            "private_data": ["phone", "address", "passport", "ssn"],
        }
        lowered = text.lower()
        return [
            marker
            for marker, phrases in markers.items()
            if any(phrase in lowered for phrase in phrases)
        ]
