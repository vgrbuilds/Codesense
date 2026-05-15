# import all the necessary modules
from fastapi import APIRouter, Depends, Path
from src.schemas.project import ProjectCreateSchema
from src.services.project_service import ProjectService
from src.core.security import get_current_user

# defining the router
router = APIRouter(prefix="/projects", tags=["projects"])

# endpoint to create a project
@router.post("")
async def create_project(
    project_data: ProjectCreateSchema,
    current_user: dict = Depends(get_current_user),
):
    response = await ProjectService.create_project(current_user["id"], project_data)
    return response

# endpoint to list current user's projects
@router.get("")
async def list_projects(current_user: dict = Depends(get_current_user)):
    response = await ProjectService.list_projects(current_user["id"])
    return response

# endpoint to get a specific project
@router.get("/{project_id}")
async def get_project(
    project_id: str = Path(..., description="The ID of the project to retrieve"),
    current_user: dict = Depends(get_current_user),
):
    response = await ProjectService.get_project(project_id)
    if not response.get("success"):
        return response

    if response["data"]["owner_id"] != current_user["id"]:
        return {"success": False, "message": "Not authorized to access this project"}

    return response

# endpoint to delete a project
@router.delete("/{project_id}")
async def delete_project(
    project_id: str = Path(...),
    current_user: dict = Depends(get_current_user),
):
    response = await ProjectService.delete_project(project_id, current_user)
    return response
