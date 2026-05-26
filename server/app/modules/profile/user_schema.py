# importing all the required modules
from pydantic import BaseModel,EmailStr,Field,ConfigDict
from typing import Optional
from datetime import datetime


# defining the user schema class
class UserSchema(BaseModel):
    name: str
    email: EmailStr
    password: str
    profile_picture: Optional[str] = None


# defining the auth schema class
class AuthSchema(BaseModel):
    email: EmailStr
    password: str


# defining the update user schema class
class UpdateUserSchema(BaseModel):
    name: Optional[str] = None
    email: Optional[EmailStr] = None
    password: Optional[str] = None
    profile_picture: Optional[str] = None


# defining the update credits schema class
class UpdateCreditsSchema(BaseModel):
    credits: int


# defining the user response schema class
class UserResponseSchema(BaseModel):
    id: str = Field(..., alias="_id")
    name: str
    email: EmailStr
    profile_picture: Optional[str] = None
    credits: int
    created_at: datetime
    updated_at: datetime
    credits_last_reset: Optional[datetime] = None
    model_config = ConfigDict(populate_by_name=True)


# defining the auth response schema class
class AuthResponseSchema(BaseModel):
    access_token: str
    token_type: str = "bearer"


# defining the user delete response schema class
class UserDeleteResponseSchema(BaseModel):
    message: str