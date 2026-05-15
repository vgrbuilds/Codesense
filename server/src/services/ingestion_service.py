#importing all the necessary modules
import asyncio
import os
from datetime import datetime
from pathlib import Path
from typing import Any

import google.generativeai as genai

from src.core.config import config
from src.db.mongo import MongoDB
from src.models.chunk import ChunkModel
from src.models.repository import RepositoryModel
from src.schemas.repository import RepositoryCreateSchema


class IngestionService:
    ALLOWED_EXTENSIONS = {
        ".py", ".js", ".ts", ".tsx", ".jsx", ".md", ".txt",
        ".json", ".yaml", ".yml", ".toml", ".ini", ".cfg", ".sh",
        ".java", ".c", ".cpp", ".h", ".cs", ".go", ".rb", ".php",
        ".rs",
    }
    IGNORE_DIRS = {"node_modules", ".git", "__pycache__", ".venv", "venv"}
    MAX_LINES_PER_CHUNK = 200
    CHUNK_OVERLAP = 20
    BATCH_SIZE = 500

    @staticmethod
    async def ingest_repository(
        source_path: str,
        repository_data: RepositoryCreateSchema,
    ) -> dict[str, Any]:
        root = Path(source_path)
        if not root.exists() or not root.is_dir():
            return {"success": False, "message": f"Repository path not found: {source_path}"}

        repository_doc = RepositoryModel(
            url=repository_data.url,
            assets=repository_data.assets,
            summary=repository_data.summary,
            documentation=repository_data.documentation,
        )

        repository_result = await MongoDB.database["repositories"].insert_one(repository_doc.model_dump())
        repository_id = str(repository_result.inserted_id)

        chunks: list[dict[str, Any]] = []
        files_scanned = 0

        for file_path in IngestionService._walk_text_files(root):
            files_scanned += 1
            content = IngestionService._read_file_text(file_path)
            if content is None or not content.strip():
                continue

            language = IngestionService._detect_language(file_path)
            for chunk_index, chunk_data in enumerate(IngestionService._split_text_to_chunks(content)):
                chunk = ChunkModel(
                    repository_id=repository_id,
                    file_path=str(file_path.relative_to(root)).replace("\\", "/"),
                    content=chunk_data["content"],
                    chunk_index=chunk_index,
                    embedding=await IngestionService.generate_embedding(chunk_data["content"]),
                    language=language,
                    start_line=chunk_data["start_line"],
                    end_line=chunk_data["end_line"],
                )
                chunks.append(chunk.model_dump())

        if not chunks:
            await MongoDB.database["repositories"].delete_one({"_id": repository_result.inserted_id})
            return {
                "success": False,
                "message": "No supported text files were found in the repository path.",
                "files_scanned": files_scanned,
            }

        await IngestionService._insert_chunks_in_batches(chunks)

        return {
            "success": True,
            "repository_id": repository_id,
            "files_scanned": files_scanned,
            "chunks_created": len(chunks),
        }

    @staticmethod
    async def generate_embedding(text: str) -> list[float]:
        """Generate an embedding vector for a chunk using Gemini."""
        if not config.gemini_key:
            raise RuntimeError("GEMINI_KEY is not configured in the environment")

        if not text:
            return []

        genai.configure(api_key=config.gemini_key)

        def create_embedding() -> list[float]:
            response = genai.embeddings.create(
                model="gemini-embedding-alpha-001",
                input=text,
            )
            return response["data"][0]["embedding"]

        return await asyncio.to_thread(create_embedding)

    @staticmethod
    async def _insert_chunks_in_batches(chunks: list[dict[str, Any]]) -> None:
        for start in range(0, len(chunks), IngestionService.BATCH_SIZE):
            batch = chunks[start : start + IngestionService.BATCH_SIZE]
            await MongoDB.database["chunks"].insert_many(batch)

    @staticmethod
    def _walk_text_files(root: Path):
        for dirpath, dirnames, filenames in os.walk(root):
            dirnames[:] = [d for d in dirnames if d not in IngestionService.IGNORE_DIRS]
            for filename in filenames:
                path = Path(dirpath) / filename
                if path.suffix.lower() in IngestionService.ALLOWED_EXTENSIONS:
                    yield path

    @staticmethod
    def _read_file_text(file_path: Path) -> str | None:
        try:
            return file_path.read_text(encoding="utf-8", errors="ignore")
        except Exception:
            return None

    @staticmethod
    def _split_text_to_chunks(text: str) -> list[dict[str, Any]]:
        lines = text.splitlines()
        if not lines:
            return []

        chunks: list[dict[str, Any]] = []
        step = max(1, IngestionService.MAX_LINES_PER_CHUNK - IngestionService.CHUNK_OVERLAP)
        start_line = 0

        while start_line < len(lines):
            end_line = min(start_line + IngestionService.MAX_LINES_PER_CHUNK, len(lines))
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

    @staticmethod
    def _detect_language(file_path: Path) -> str | None:
        extension_map = {
            ".py": "python",
            ".js": "javascript",
            ".ts": "typescript",
            ".tsx": "typescript",
            ".jsx": "javascript",
            ".md": "markdown",
            ".java": "java",
            ".c": "c",
            ".cpp": "cpp",
            ".h": "c",
            ".cs": "csharp",
            ".go": "go",
            ".rb": "ruby",
            ".php": "php",
            ".rs": "rust",
            ".sh": "bash",
            ".json": "json",
            ".yaml": "yaml",
            ".yml": "yaml",
            ".toml": "toml",
            ".ini": "ini",
            ".cfg": "ini",
            ".txt": "text",
        }
        return extension_map.get(file_path.suffix.lower())
