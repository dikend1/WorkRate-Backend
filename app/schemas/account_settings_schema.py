from pydantic import BaseModel
from datetime import datetime
from typing import Any

class AccountSettingsBase(BaseModel):
    email_notifications: bool = True
    profile_visibility: str = "public"  # public, private, anonymous
    data_sharing: bool = False
    two_factor_enabled: bool = False

class AccountSettingsCreate(AccountSettingsBase):
    pass

class AccountSettingsUpdate(BaseModel):
    email_notifications: bool | None = None
    profile_visibility: str | None = None
    data_sharing: bool | None = None
    two_factor_enabled: bool | None = None

class AccountSettingsResponse(AccountSettingsBase):
    id: int
    user_id: int

    model_config = {"from_attributes": True}