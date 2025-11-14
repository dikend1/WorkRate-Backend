from pydantic import BaseModel, EmailStr



class UserBaseSchema(BaseModel):
    email: EmailStr
    username: str  

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



