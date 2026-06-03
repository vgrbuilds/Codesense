from datetime import datetime
from bson import ObjectId
from app.modules.project.project_model import Project
from app.modules.project.project_schema import ProjectResponseSchema
from app.modules.repository.repository_service import RepositoryService
from app.modules.chat.chat_service import ChatService


# defining the project service class
class ProjectService:

    def __init__(self, db):
        self.collection = db["projects"]
        self.repo_service = RepositoryService(db)
        self.chat_service = ChatService(db)

    def _serialize(self, project: dict) -> ProjectResponseSchema:
        project["_id"] = str(project["_id"])
        return ProjectResponseSchema(**project)

    # service to create a project
    async def create_project(self, name: str, github_link: str, user_id: str) -> ProjectResponseSchema:
        # check if repo exists or create it
        repo = await self.repo_service.create_repository(github_link)

        # build project entity
        project = Project(
            name=name,
            user_id=user_id,
            repo_id=repo.id,
            created_at=datetime.utcnow(),
            updated_at=datetime.utcnow(),
        )

        # store
        result = await self.collection.insert_one(
            project.model_dump(by_alias=True, exclude={"id"})
        )
        
        project_id_str = str(result.inserted_id)

        # create conversation
        conversation_id = await self.chat_service.create_conversation(project_id_str, user_id)

        # update project with conversation_id
        await self.collection.update_one(
            {"_id": result.inserted_id},
            {"$set": {"conversation_id": conversation_id, "updated_at": datetime.utcnow()}}
        )

        stored = await self.collection.find_one({"_id": result.inserted_id})
        return self._serialize(stored)

    # service to get a project by id
    async def get_project(self, project_id: str) -> ProjectResponseSchema:
        project = await self.collection.find_one({"_id": ObjectId(project_id)})
        if not project:
            raise ValueError(f"Project {project_id} not found")
        return self._serialize(project)

    # service to get all projects for a user
    async def get_user_projects(self, user_id: str) -> list[ProjectResponseSchema]:
        projects = []
        async for project in self.collection.find({"user_id": user_id}):
            projects.append(self._serialize(project))
        return projects