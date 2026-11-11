
from pydantic import BaseModel, ConfigDict, EmailStr, Field


# Dữ liệu khi đăng ký
class UserRegister(BaseModel):

    full_name: str = Field(
        min_length=2,
        max_length=100
    )

    email: EmailStr

    password: str = Field(
        min_length=8,
        max_length=128
    )


# Dữ liệu trả về cho client
class UserResponse(BaseModel):

    model_config = ConfigDict(from_attributes=True)

    id: int
    full_name: str
    email: EmailStr
    role: str
    is_active: bool


# Dữ liệu trả về khi đăng nhập
class Token(BaseModel):

    access_token: str
    token_type: str
