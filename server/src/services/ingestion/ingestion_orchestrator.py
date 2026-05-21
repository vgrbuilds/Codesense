#importing all the necessary modules
from typing import Any
from src.schemas.repository import RepositoryCreateSchema
from src.services.ingestion.repository_ingestion_pipeline import ingest_repository_pipeline


# defining ingestion workflow service
class IngestionService:
    #method to ingest the repository and create chunks
    @staticmethod
    async def ingest_repository(
        source_path: str,
        repository_data: RepositoryCreateSchema,
    ) -> dict[str, Any]:
        return await ingest_repository_pipeline(source_path, repository_data)
