#importing all the necessary modules
import os
from pathlib import Path
from typing import Any
from src.services.ingestion.constants import (
    ALLOWED_EXTENSIONS,
    CHUNK_OVERLAP,
    DOCUMENT_EXTENSIONS,
    EXTENSION_LANGUAGE_MAP,
    IMAGE_EXTENSIONS,
    IGNORE_DIRS,
    MAX_LINES_PER_CHUNK,
)


#method to walk all supported text files
def walk_text_files(root: Path):
    for dirpath, dirnames, filenames in os.walk(root):
        dirnames[:] = [d for d in dirnames if d not in IGNORE_DIRS]
        for filename in filenames:
            path = Path(dirpath) / filename
            if path.suffix.lower() in ALLOWED_EXTENSIONS:
                yield path


#method to read file content safely
def read_file_text(file_path: Path) -> str | None:
    try:
        return file_path.read_text(encoding="utf-8", errors="ignore")
    except Exception:
        return None


#method to split text content into overlapping line chunks
def split_text_to_chunks(text: str) -> list[dict[str, Any]]:
    lines = text.splitlines()
    if not lines:
        return []

    chunks: list[dict[str, Any]] = []
    step = max(1, MAX_LINES_PER_CHUNK - CHUNK_OVERLAP)
    start_line = 0

    while start_line < len(lines):
        end_line = min(start_line + MAX_LINES_PER_CHUNK, len(lines))
        chunk_lines = lines[start_line:end_line]
        chunks.append(
            {
                "content": "\n".join(chunk_lines),
                "start_line": start_line + 1,
                "end_line": end_line,
            }
        )
        if end_line == len(lines):
            break
        start_line += step

    return chunks


#method to map file extension to programming language
def detect_language(file_path: Path) -> str | None:
    return EXTENSION_LANGUAGE_MAP.get(file_path.suffix.lower())


#method to check if a file is image
def is_image_file(file_path: Path) -> bool:
    return file_path.suffix.lower() in IMAGE_EXTENSIONS


#method to check if a file is document
def is_document_file(file_path: Path) -> bool:
    return file_path.suffix.lower() in DOCUMENT_EXTENSIONS
