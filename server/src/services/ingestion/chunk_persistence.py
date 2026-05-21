#importing all the necessary modules
from pathlib import Path
from typing import Any
from src.db.mongo import MongoDB
from src.models.chunk import ChunkModel
from src.services.ingestion.constants import BATCH_SIZE
from src.services.ingestion.file_helpers import detect_language, read_file_text, split_text_to_chunks, walk_text_files
from src.services.ingestion.llm_helpers import generate_embedding


#method to build chunk payloads from repository files
async def build_chunks(root: Path, repository_id: str) -> tuple[list[dict[str, Any]], int]:
    chunks: list[dict[str, Any]] = []
    files_scanned = 0

    for file_path in walk_text_files(root):
        files_scanned += 1
        content = read_file_text(file_path)
        if content is None or not content.strip():
            continue

        language = detect_language(file_path)
        for chunk_index, chunk_data in enumerate(split_text_to_chunks(content)):
            chunk = ChunkModel(
                repository_id=repository_id,
                file_path=str(file_path.relative_to(root)).replace("\\", "/"),
                content=chunk_data["content"],
                chunk_index=chunk_index,
                embedding=await generate_embedding(chunk_data["content"]),
                language=language,
                start_line=chunk_data["start_line"],
                end_line=chunk_data["end_line"],
            )
            chunks.append(chunk.model_dump())

    return chunks, files_scanned


#method to insert chunk documents in batches
async def insert_chunks_in_batches(chunks: list[dict[str, Any]]) -> None:
    for start in range(0, len(chunks), BATCH_SIZE):
        batch = chunks[start : start + BATCH_SIZE]
        await MongoDB.database["chunks"].insert_many(batch)
