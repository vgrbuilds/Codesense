from pydantic import BaseModel, Field, ConfigDict
from typing import Optional
from datetime import datetime


# defining the create repository schema class
class CreateRepositorySchema(BaseModel):
    github_link: str


# defining the repository response schema class
class RepositoryResponseSchema(BaseModel):
    id: str = Field(..., alias="_id")
    github_link: str
    description: Optional[str] = None
    technologies: Optional[list[str]] = None
    summary: Optional[str] = None
    workflow_diagram: Optional[str] = None
    architecture_diagram: Optional[str] = None
    er_diagram: Optional[str] = None
    setup_guide: Optional[str] = None 
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(populate_by_name=True)