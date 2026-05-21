#importing all the necessary modules
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any
from src.models.repository import RepositoryModel


#defining ingestion runtime context
@dataclass
class IngestionContext:
    repo_local_path: str | None = None
    readme_text: str = ""
    file_list: list[str] = field(default_factory=list)
    root: Path | None = None
    repository_doc: RepositoryModel | None = None
    repository_inserted_id: Any = None
    repository_id: str = ""
    chunks: list[dict[str, Any]] = field(default_factory=list)
    files_scanned: int = 0
    uploaded_assets: list[dict[str, Any]] = field(default_factory=list)
    uploaded_documents: list[dict[str, Any]] = field(default_factory=list)
