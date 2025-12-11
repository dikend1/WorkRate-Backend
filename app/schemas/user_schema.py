from pydantic import BaseModel, EmailStr



class UserBaseSchema(BaseModel):
    email: EmailStr
    username: str
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

class TokenSchema(BaseModel):
    access_token: str
    token_type: str = "bearer"



