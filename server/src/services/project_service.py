# importing all the necessary modules
from datetime import datetime
from bson import ObjectId
from src.db.mongo import MongoDB
from src.models.project import ProjectModel
from src.schemas.project import ProjectCreateSchema, ProjectResponseSchema


class ProjectService:
    #method to create a new project
    @staticmethod
    async def create_project(owner_id: str, project_data: ProjectCreateSchema):
        projects_collection = MongoDB.database["projects"]

        new_project = ProjectModel(
            name=project_data.name,
            description=project_data.description,
            owner_id=owner_id,
            repository_url=project_data.repository_url,
            created_at=datetime.utcnow(),
        )

        result = await projects_collection.insert_one(new_project.model_dump())
        return {
            "success": True,
            "message": "Project created successfully",
            "project_id": str(result.inserted_id),
        }
    #method to get a specific project by its ID
    @staticmethod
    async def get_project(project_id: str):
        projects_collection = MongoDB.database["projects"]

        try:
            project = await projects_collection.find_one({"_id": ObjectId(project_id)})
        except Exception:
            return {"success": False, "message": "Invalid project ID format"}

        if not project:
            return {"success": False, "message": "Project not found"}

        project["id"] = str(project.pop("_id"))
        return {"success": True, "data": ProjectResponseSchema(**project).model_dump()}
    #method to list projects by their owner ID
    @staticmethod
    async def list_projects(owner_id: str):
        projects_collection = MongoDB.database["projects"]
        cursor = projects_collection.find({"owner_id": owner_id})
        projects = []

        async for project in cursor:
            project["id"] = str(project.pop("_id"))
            projects.append(ProjectResponseSchema(**project).model_dump())

        return {"success": True, "data": projects}
    #method to delete a project by its ID and the current user
    @staticmethod
    async def delete_project(project_id: str, current_user: dict):
        projects_collection = MongoDB.database["projects"]

        try:
            project = await projects_collection.find_one({"_id": ObjectId(project_id)})
        except Exception:
            return {"success": False, "message": "Invalid project ID format"}

        if not project:
            return {"success": False, "message": "Project not found"}

        if project["owner_id"] != current_user["id"]:
            return {"success": False, "message": "Not authorized to delete this project"}

        result = await projects_collection.delete_one({"_id": ObjectId(project_id)})
        if result.deleted_count > 0:
            return {"success": True, "message": "Project deleted successfully"}
        return {"success": False, "message": "Project not found"}
