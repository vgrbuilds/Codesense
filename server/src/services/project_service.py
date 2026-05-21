# importing all the necessary modules
from datetime import datetime
from bson import ObjectId
from src.db.mongo import MongoDB
from src.models.project import ProjectModel
from src.schemas.repository import RepositoryCreateSchema
from src.schemas.project import ProjectCreateSchema, ProjectResponseSchema
from src.services.ingestion_service import IngestionService
from src.services.policies import (
    CREDIT_COST_PER_PROJECT,
    DEFAULT_CREDITS,
    normalize_repository_url,
    should_reset_credits,
)


class ProjectService:
    #method to create a new project
    @staticmethod
    async def create_project(owner_id: str, project_data: ProjectCreateSchema):
        projects_collection = MongoDB.database["projects"]
        users_collection = MongoDB.database["users"]
        repositories_collection = MongoDB.database["repositories"]

        try:
            user_object_id = ObjectId(owner_id)
        except Exception:
            return {"success": False, "message": "Invalid owner ID format"}

        user = await users_collection.find_one({"_id": user_object_id})
        if not user:
            return {"success": False, "message": "User not found"}

        now = datetime.utcnow()
        user_credits = int(user.get("credits", DEFAULT_CREDITS))
        last_reset_at = user.get("credits_last_reset_at")

        update_user_fields: dict = {}
        if should_reset_credits(last_reset_at, now):
            user_credits = DEFAULT_CREDITS
            update_user_fields["credits"] = user_credits
            update_user_fields["credits_last_reset_at"] = now

        if user_credits < CREDIT_COST_PER_PROJECT:
            return {"success": False, "message": "Insufficient credits to create a project"}

        normalized_url = normalize_repository_url(project_data.repository_url)
        existing_repository = await repositories_collection.find_one({"url": normalized_url})
        repository_id: str | None = str(existing_repository["_id"]) if existing_repository else None

        if not existing_repository:
            ingestion_result = await IngestionService.ingest_repository(
                source_path="",
                repository_data=RepositoryCreateSchema(url=normalized_url),
            )
            if not ingestion_result.get("success"):
                return {
                    "success": False,
                    "message": ingestion_result.get("message", "Repository ingestion failed"),
                }
            repository_id = ingestion_result["repository_id"]

        new_project = ProjectModel(
            name=project_data.name,
            description=project_data.description,
            owner_id=owner_id,
            repository_url=normalized_url,
            repository_id=repository_id,
            created_at=datetime.utcnow(),
        )

        result = await projects_collection.insert_one(new_project.model_dump())
        update_user_fields["credits"] = user_credits - CREDIT_COST_PER_PROJECT
        await users_collection.update_one({"_id": user_object_id}, {"$set": update_user_fields})
        return {
            "success": True,
            "message": "Project created successfully",
            "project_id": str(result.inserted_id),
            "repository_id": repository_id,
            "credits_remaining": update_user_fields["credits"],
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
