# importing all the necessary modules
from pydantic import BaseModel, EmailStr, Field

# schema for user registration
class UserRegisterSchema(BaseModel):
    email: EmailStr
    username: str = Field(min_length=3, max_length=20)
    password: str = Field(min_length=6)

# schema for user login
class UserLoginSchema(BaseModel):
    email: EmailStr
    password: str

# schema for sending user data to frontend
class UserResponseSchema(BaseModel):
    id: str
    email: EmailStr
    username: str
    avatar: str | None = None
    credits: int

# schema for updating the user details
class UserUpdateSchema(BaseModel):
    username: str | None = Field(default=None, min_length=3, max_length=20)
    email: EmailStr | None = None
    new_password: str | None = Field(default=None, min_length=6)
    avatar: str | None = None
