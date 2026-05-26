from pydantic import BaseModel, ConfigDict, Field
from typing import Optional
from datetime import datetime


# defining the create project schema class
class CreateProjectSchema(BaseModel):
    name: str
    github_link: str


# defining the project response schema class
class ProjectResponseSchema(BaseModel):
    id: str = Field(..., alias="_id")
    name: str
    user_id: str
    repo_id: str
    conversation_id: Optional[str] = None
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(populate_by_name=True)


# defining the project delete response schema class
class ProjectDeleteResponseSchema(BaseModel):
    message: str