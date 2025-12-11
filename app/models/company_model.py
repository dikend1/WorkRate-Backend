from sqlalchemy import Column, Integer, String, Text, DateTime, Float,Boolean
from app.db.base import Base
from sqlalchemy.orm import relationship
from datetime import datetime

class CompanyModel(Base):
    __tablename__ = "companies"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, unique=True, index=True, nullable=False)
    description = Column(Text, nullable=True)
    website = Column(String, nullable=True)
    industry = Column(String, nullable=True)
    location = Column(String, nullable=True)
    logo_url = Column(String, nullable=True)
    rating = Column(Float, default=0.0)
    founded_year = Column(Integer,nullable=True)
    tax_contributions = Column(Float,default=None)
    stock_price = Column(Float,nullable=True)
    is_public = Column(Boolean, default=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    reviews = relationship("ReviewModel", back_populates="company")
    salaries = relationship("SalaryModel", back_populates="company")
    
