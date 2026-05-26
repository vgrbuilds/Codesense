#importing all the required modules
from pydantic import BaseModel, ConfigDict, EmailStr, Field
from typing import Optional
from datetime import datetime

# defining the user model class
class User(BaseModel):
    id: Optional[str] = Field(None, alias="_id")
    name: str
    email: EmailStr
    hashed_password: str
    profile_picture: Optional[str] = None
    credits: int 
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)
    last_credit_update: Optional[datetime] = None
    model_config = ConfigDict(populate_by_name=True)


