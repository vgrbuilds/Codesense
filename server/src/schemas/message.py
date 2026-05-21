# importing all the necessary modules
from datetime import datetime
from typing import Any
from pydantic import BaseModel, Field


class MessageCreateSchema(BaseModel):
    conversation_id: str
    role: str
    content: str
    references: list[Any] = Field(default_factory=list)


class MessageResponseSchema(BaseModel):
    id: str
    conversation_id: str
    user_id: str
    role: str
    content: str
    references: list[Any]
    created_at: datetime


class MessageQuerySchema(BaseModel):
    conversation_id: str
    repository_id: str
    question: str
    top_k: int = 5
