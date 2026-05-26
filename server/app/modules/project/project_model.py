from pydantic import BaseModel, ConfigDict, Field
from typing import Optional
from datetime import datetime


# defining the project model class
class Project(BaseModel):
    id: Optional[str] = Field(None, alias="_id")
    name: str
    user_id: str
    repo_id: str
    conversation_id: Optional[str] = None
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)

    model_config = ConfigDict(populate_by_name=True)