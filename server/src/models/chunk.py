#importing necessary modules
from typing import Optional
from datetime import datetime
from pydantic import BaseModel, Field

# defining the chunk class
class ChunkModel(BaseModel):
    id: Optional[str] = None
    repository_id: str
    file_path: str
    content: str
    chunk_index: int
    embedding: list[float]
    language: Optional[str] = None
    start_line: Optional[int] = None
    end_line: Optional[int] = None
    created_at: datetime = Field(default_factory=datetime.utcnow)