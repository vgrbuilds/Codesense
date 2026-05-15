#importing all the necessary modules
from typing import Optional , Literal
from datetime import datetime
from pydantic import BaseModel, Field


#defining the message class
class MessageModel(BaseModel):
    id: Optional[str] = None
    conversation_id: str
    user_id: str
    role: Literal["user", "assistant" , "system"]
    content: str
    references: list = Field(default_factory=list)
    created_at: datetime = Field(default_factory=datetime.utcnow)
  

