from pydantic import BaseModel, ConfigDict, Field
from typing import Optional
from datetime import datetime


# defining the repository model class
class Repository(BaseModel):
    id: Optional[str] = Field(None, alias="_id")
    github_link: str
    description: Optional[str] = None
    technologies: Optional[list[str]] = None
    summary: Optional[str] = None
    workflow_diagram: Optional[str] = None
    architecture_diagram: Optional[str] = None
    er_diagram: Optional[str] = None
    setup_guide: Optional[str] = None
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)

    model_config = ConfigDict(populate_by_name=True)