#imporing all the necessary modules
from typing import Optional
from datetime import datetime
from pydantic import BaseModel, EmailStr , Field


#defining the  user class
class UserModel(BaseModel):
    id: Optional[str] = None
    email: EmailStr
    username: str = Field(min_length=3, max_length=20)
    hashed_password: str
    avatar: Optional[str] = None
    credits: int = 10
    credits_last_reset_at: datetime = Field(default_factory=datetime.utcnow)
    created_at: datetime = Field(default_factory=datetime.utcnow)




