# import all the necessary modules
from fastapi import APIRouter
from src.schemas.repository import RepositoryCreateSchema
from src.services.repository_service import RepositoryService

# defining the router
router = APIRouter(prefix="/repositories", tags=["repositories"])

# endpoint to create a repository
@router.post("")
async def create_repository(repository_data: RepositoryCreateSchema):
    response = await RepositoryService.create_repository(repository_data)
    return response

# endpoint to get a repository by ID
@router.get("/{repository_id}")
async def get_repository(repository_id: str):
    response = await RepositoryService.get_repository(repository_id)
    return response
