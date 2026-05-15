# importing all the necessary modules
from datetime import datetime
from pydantic import BaseModel, Field


class ChunkCreateSchema(BaseModel):
    repository_id: str
    file_path: str
    content: str
    chunk_index: int
    embedding: list[float]
    language: str | None = None
    start_line: int | None = None
    end_line: int | None = None


class ChunkResponseSchema(BaseModel):
    id: str
    repository_id: str
    file_path: str
    content: str
    chunk_index: int
    embedding: list[float]
    language: str | None = None
    start_line: int | None = None
    end_line: int | None = None
    created_at: datetime
