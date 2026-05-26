from pydantic import BaseModel, ConfigDict, Field
from typing import Optional
from datetime import datetime


# defining the send message schema class
class SendMessageSchema(BaseModel):
    content: str


# defining the message response schema class
class MessageResponseSchema(BaseModel):
    id: str = Field(..., alias="_id")
    conversation_id: str
    role: str
    content: str
    created_at: datetime

    model_config = ConfigDict(populate_by_name=True)


# defining the conversation response schema class
class ConversationResponseSchema(BaseModel):
    id: str = Field(..., alias="_id")
    project_id: str
    user_id: str
    created_at: datetime
    messages: list[MessageResponseSchema] = []

    model_config = ConfigDict(populate_by_name=True)