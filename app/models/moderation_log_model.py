from sqlalchemy import Column, Integer, Float, Text, DateTime, ForeignKey, JSON
from sqlalchemy.orm import relationship
from app.db.base import Base


class ModerationLog(Base):
    __tablename__ = "moderation_logs"

    id = Column(Integer, primary_key=True, index=True)
    review_id = Column(Integer, ForeignKey("reviews.id"), nullable=False)
    ai_score = Column(Float, nullable=False)
    flagged_words = Column(JSON, nullable=True)
    moderator_decision = Column(Text, nullable=False)
    moderated_at = Column(DateTime, nullable=False)

    # Relationships
    review = relationship("Review", back_populates="moderation_logs")