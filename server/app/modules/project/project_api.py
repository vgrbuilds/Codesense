from fastapi import APIRouter, HTTPException
from app.modules.project.project_schema import (
    CreateProjectSchema,
    ProjectResponseSchema,
)
from app.modules.project.project_service import ProjectService
from app.core.db_connect import mongodb

router = APIRouter(prefix="/project", tags=["project"])


# defining the project API class
class ProjectAPI:

    def __init__(self):
        self.service = ProjectService(mongodb.get_database())

    # api to create a project
    async def create_project(self, data: CreateProjectSchema, user_id: str) -> ProjectResponseSchema:
        try:
            return await self.service.create_project(data.name, data.github_link, user_id)
        except Exception as e:
            raise HTTPException(status_code=500, detail=str(e))

    # api to get a project by id
    async def get_project(self, project_id: str) -> ProjectResponseSchema:
        try:
            return await self.service.get_project(project_id)
        except ValueError as e:
            raise HTTPException(status_code=404, detail=str(e))


# ── routes ────────────────────────────────────────────────
project_api = ProjectAPI()


@router.post("/", response_model=ProjectResponseSchema)
async def create_project(data: CreateProjectSchema, user_id: str):
    return await project_api.create_project(data, user_id)


@router.get("/{project_id}", response_model=ProjectResponseSchema)
async def get_project(project_id: str):
    return await project_api.get_project(project_id)