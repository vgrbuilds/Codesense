#importing all the necessary modules
from typing import Optional , Literal
from datetime import datetime
from pydantic import BaseModel, Field

#defining the conversation class
class ConversationModel(BaseModel):
    id: Optional[str] = None
    project_id: str
    title: str
    user_id: str
    created_at: datetime = Field(default_factory=datetime.utcnow)
