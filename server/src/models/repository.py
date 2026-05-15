#importing all the necessary modules
from typing import Optional , Literal
from datetime import datetime
from pydantic import BaseModel, Field

#defining the repository class
class RepositoryModel(BaseModel):
    id: Optional[str] = None
    url: str
    assets: list = Field(default_factory=list)
    summary: str | None = None
    documentation: list = Field(default_factory=list)#url for cloudinary files stored as documents
    created_at: datetime = Field(default_factory=datetime.utcnow)
