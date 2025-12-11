from sqlalchemy import Column, Integer, Boolean, String, ForeignKey
from sqlalchemy.orm import relationship
from app.db.base import Base


class AccountSettings(Base):
    __tablename__ = "account_settings"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False, unique=True)
    email_notifications = Column(Boolean, default=True)
    profile_visibility = Column(String(20), default="public")  # public, private, anonymous
    data_sharing = Column(Boolean, default=False)
    two_factor_enabled = Column(Boolean, default=False)

    # Relationships
    user = relationship("User", back_populates="account_settings")