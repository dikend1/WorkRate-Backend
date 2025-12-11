from sqlalchemy import Column,String,Integer,DateTime,Text,Float,ForeignKey,Boolean,Date
from app.db.base import Base
from sqlalchemy.orm import relationship
from datetime import datetime
import enum


class ReviewStatus(str,enum.Enum):
    PENDING = "pending"
    VERIFIED = "verified"
    REJECTED = "rejected"


class ReviewModel(Base):
    __tablename__ = "reviews"

    id = Column(Integer,primary_key=True,index=True)
    company_id = Column(Integer,ForeignKey("companies.id"),nullable=False)
    user_id = Column(Integer,ForeignKey("users.id"),nullable=False)
    rating = Column(Float,nullable=False)
    title = Column(String(200),nullable=False)
    content = Column(Text,nullable=False)
    pros = Column(Text,nullable=True)
    cons = Column(Text,nullable=True)
    is_current_employee = Column(Boolean,default=True)
    employment_end_date = Column(Date,nullable=True)
    is_anonymous = Column(Boolean,default=False)
    recommendations = Column(String,nullable=True)
    work_location = Column(String,nullable=True)
    status = Column(String,default=ReviewStatus.PENDING.value,nullable=False)
    created_at = Column(DateTime,default=datetime.utcnow)
    updated_at = Column(DateTime,default=datetime.utcnow,onupdate=datetime.utcnow)
    
    # Relationships
    user = relationship("UserModel", back_populates="reviews")
    company = relationship("CompanyModel", back_populates="reviews")
    moderation_logs = relationship("ModerationLog", back_populates="review")
    