from fastapi import APIRouter, HTTPException
from app.modules.repository.repository_schema import (
    CreateRepositorySchema,
    RepositoryResponseSchema,
)
from app.modules.repository.repository_service import RepositoryService
from app.core.db_connect import mongodb

router = APIRouter(prefix="/repository", tags=["repository"], include_in_schema=False)

# Public HTTP routes from this router are intentionally disabled.
# Project creation must be the only entry point that creates/links repositories.




# defining the repository API class
class RepositoryAPI:

    def __init__(self):
        self.service = RepositoryService(mongodb.get_database())

    # api to create a repository
    async def create_repository(self, data: CreateRepositorySchema) -> RepositoryResponseSchema:
        try:
            return await self.service.create_repository(data.github_link)
        except Exception as e:
            raise HTTPException(status_code=500, detail=str(e))

    # api to get a repository by id
    async def get_repository(self, repo_id: str) -> RepositoryResponseSchema:
        try:
            return await self.service.get_repository(repo_id)
        except ValueError as e:
            raise HTTPException(status_code=404, detail=str(e))


# ── routes ────────────────────────────────────────────────
repository_api = RepositoryAPI()


@router.post("/", response_model=RepositoryResponseSchema)
async def create_repository(data: CreateRepositorySchema):
    return await repository_api.create_repository(data)


@router.get("/{repo_id}", response_model=RepositoryResponseSchema)
async def get_repository(repo_id: str):
    return await repository_api.get_repository(repo_id)