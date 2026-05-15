# importing all the necessary modules
from datetime import datetime
from pydantic import BaseModel, Field


class ProjectCreateSchema(BaseModel):
    name: str = Field(min_length=3, max_length=50)
    description: str | None = None
    repository_url: str


class ProjectResponseSchema(BaseModel):
    id: str
    name: str
    description: str | None = None
    owner_id: str
    repository_url: str
    created_at: datetime
