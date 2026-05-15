# importing all the necessary modules
from datetime import datetime
from bson import ObjectId
from src.db.mongo import MongoDB
from src.models.repository import RepositoryModel
from src.schemas.repository import RepositoryCreateSchema, RepositoryResponseSchema


class RepositoryService:
    @staticmethod
    async def create_repository(repository_data: RepositoryCreateSchema):
        repositories_collection = MongoDB.database["repositories"]

        new_repository = RepositoryModel(
            url=repository_data.url,
            assets=repository_data.assets,
            summary=repository_data.summary,
            documentation=repository_data.documentation,
            created_at=datetime.utcnow(),
        )

        result = await repositories_collection.insert_one(new_repository.model_dump())
        return {
            "success": True,
            "message": "Repository created successfully",
            "repository_id": str(result.inserted_id),
        }

    @staticmethod
    async def get_repository(repository_id: str):
        repositories_collection = MongoDB.database["repositories"]

        try:
            repository = await repositories_collection.find_one({"_id": ObjectId(repository_id)})
        except Exception:
            return {"success": False, "message": "Invalid repository ID format"}

        if not repository:
            return {"success": False, "message": "Repository not found"}

        repository["id"] = str(repository.pop("_id"))
        return {"success": True, "data": RepositoryResponseSchema(**repository).model_dump()}
