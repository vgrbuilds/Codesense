from fastapi import APIRouter
from src.schemas.repository import RepositoryIngestSchema
from src.services.ingestion_service import IngestionService


router = APIRouter(prefix="/repositories", tags=["repositories"])


@router.post("/ingest")
async def ingest_repository(
    payload: RepositoryIngestSchema,
):
    response = await IngestionService.ingest_repository(
        source_path=payload.source_path,
        repository_data=payload,
    )
    return response
