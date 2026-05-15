from fastapi import APIRouter, Depends
from src.core.security import get_current_user
from src.schemas.repository import RepositoryIngestSchema
from src.services.ingestion_service import IngestionService


router = APIRouter(prefix="/repositories", tags=["repositories"])


@router.post("/ingest")
async def ingest_repository(
    payload: RepositoryIngestSchema,
    current_user: dict = Depends(get_current_user),
):
    response = await IngestionService.ingest_repository(
        source_path=payload.source_path,
        repository_data=payload,
    )
    return response
