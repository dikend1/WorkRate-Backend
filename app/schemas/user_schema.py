from pydantic import BaseModel, EmailStr
from app.schemas.review_schema import ReviewResponse
from app.schemas.salary_schema import SalaryResponse



class UserBaseSchema(BaseModel):
    email: EmailStr
    username: str | None = None
    first_name: str | None = None
    last_name: str | None = None
    profile_picture: str | None = None
    current_position: str | None = None
    current_company_id: int | None = None  

class UserCreateSchema(UserBaseSchema):
    password: str

class UserResponseSchema(UserBaseSchema):
    id: int
    is_active: bool
    is_verified: bool

    model_config = {"from_attributes": True}

class UserUpdateSchema(BaseModel):
    email: EmailStr | None = None
    username: str | None = None
    first_name: str | None = None
    last_name: str | None = None
    profile_picture: str | None = None
    current_position: str | None = None
    current_company_id: int | None = None

class PasswordChangeSchema(BaseModel):
    current_password: str
    new_password: str

class EmailTokenSchema(BaseModel):
    token: str

class PasswordResetRequestSchema(BaseModel):
    email: EmailStr

class PasswordResetSchema(BaseModel):
    token: str
    new_password: str

class UserContributionsSchema(BaseModel):
    reviews: list[ReviewResponse]
    salaries: list[SalaryResponse]

class TokenSchema(BaseModel):
    access_token: str
    refresh_token: str | None = None
    token_type: str = "bearer"
