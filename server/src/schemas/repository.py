# importing all the necessary modules
from datetime import datetime
from typing import Any
from pydantic import BaseModel, Field


class RepositoryCreateSchema(BaseModel):
    url: str
    assets: list[Any] = Field(default_factory=list)
    summary: str | None = None
    documentation: list[Any] = Field(default_factory=list)
    design: str | None = None


class RepositoryIngestSchema(BaseModel):
    source_path: str = ""
    url: str
    assets: list[Any] = Field(default_factory=list)
    summary: str | None = None
    documentation: list[Any] = Field(default_factory=list)
    design: str | None = None


class RepositoryResponseSchema(BaseModel):
    id: str
    url: str | None = None
    assets: list[Any]
    summary: str | None = None
    documentation: list[Any]
    design: str | None = None
    created_at: datetime
