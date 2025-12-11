from sqlalchemy import Column, Integer, String,Boolean,DateTime
from app.db.base import Base
from sqlalchemy.orm import relationship
from datetime import datetime
from enum import Enum


class UserRole(str, Enum):
    USER = "user"
    MODERATOR = "moderator"
    ADMIN = "admin"


class UserModel(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    first_name = Column(String,nullable=True)
    last_name = Column(String,nullable=True)
    profile_picture= Column(String,nullable=True)
    current_position = Column(String,nullable=True)
    current_company_id = Column(Integer,nullable=True)
    username = Column(String, unique=True, index=True, nullable=False)
    email = Column(String, unique=True, index=True, nullable=False)
    hashed_password = Column(String, nullable=True)  # Для OAuth пользователей пароль может быть null
    is_active = Column(Boolean, default=True)
    is_verified = Column(Boolean, default=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    google_id = Column(String, unique=True, nullable=True)  # Для OAuth Google

    role = Column(String, default=UserRole.USER.value, nullable=False)
    reviews = relationship("ReviewModel", back_populates="user")
    salaries = relationship("SalaryModel", back_populates="user")