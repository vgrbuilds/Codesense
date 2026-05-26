from pydantic import BaseModel, ConfigDict, Field
from typing import Optional
from datetime import datetime


# defining the message model class
class Message(BaseModel):
    id: Optional[str] = Field(None, alias="_id")
    conversation_id: str
    role: str                    # "user" or "assistant"
    content: str
    created_at: datetime = Field(default_factory=datetime.utcnow)

    model_config = ConfigDict(populate_by_name=True)


# defining the conversation model class
class Conversation(BaseModel):
    id: Optional[str] = Field(None, alias="_id")
    project_id: str
    user_id: str
    created_at: datetime = Field(default_factory=datetime.utcnow)

    model_config = ConfigDict(populate_by_name=True)