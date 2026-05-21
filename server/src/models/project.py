#importing all the necessary modules
from typing import Optional
from datetime import datetime
from pydantic import BaseModel , Field


#defining the project class
class ProjectModel(BaseModel):
    id: Optional[str] = None
    name: str = Field(min_length=3, max_length=50)
    description: Optional[str] = None
    owner_id: str
    repository_url: str
    repository_id: Optional[str] = None
    created_at: datetime = Field(default_factory=datetime.utcnow)
