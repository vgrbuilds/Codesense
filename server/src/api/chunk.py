# import all the necessary modules
from fastapi import APIRouter, Path
from src.schemas.chunk import ChunkCreateSchema
from src.services.chunk_service import ChunkService

# defining the router
router = APIRouter(prefix="/chunks", tags=["chunks"])

# endpoint to create a chunk
@router.post("")
async def create_chunk(chunk_data: ChunkCreateSchema):
    response = await ChunkService.create_chunk(chunk_data)
    return response

# endpoint to get a chunk by ID
@router.get("/{chunk_id}")
async def get_chunk(chunk_id: str = Path(..., description="The ID of the chunk to retrieve")):
    response = await ChunkService.get_chunk(chunk_id)
    return response

# endpoint to list chunks for a repository
@router.get("/repository/{repository_id}")
async def list_chunks(repository_id: str = Path(..., description="The repository ID to list chunks for")):
    response = await ChunkService.list_chunks_by_repository(repository_id)
    return response
