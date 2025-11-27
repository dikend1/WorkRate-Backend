from sqlalchemy import Column, Integer, String, DateTime, Float, ForeignKey
from app.db.base import Base
from sqlalchemy.orm import relationship
from datetime import datetime

class SalaryModel(Base):
    __tablename__ = "salaries"

    id = Column(Integer, primary_key=True, index=True)
    company_id = Column(Integer, ForeignKey("companies.id"), nullable=False)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    position = Column(String, nullable=False)
    salary_amount = Column(Float, nullable=False)
    currency = Column(String(3), default="USD", nullable=False)  # USD, EUR, KZT
    experience_years = Column(Float, nullable=True)
    location = Column(String, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    
    # Relationships
    user = relationship("UserModel", back_populates="salaries")
    company = relationship("CompanyModel", back_populates="salaries")