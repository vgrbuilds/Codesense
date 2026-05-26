from datetime import datetime
from bson import ObjectId
from app.modules.ingestion.pipeline import IngestionPipeline
from app.modules.analysis.analyzer import RepoAnalyzer
from app.modules.repository.repository_model import Repository
from app.modules.repository.repository_schema import RepositoryResponseSchema


# defining the repository service class
class RepositoryService:

    def __init__(self, db):
        self.collection = db["repositories"]
        self.chunks_collection = db["chunks"]
        self.ingestion = IngestionPipeline()
        self.analyzer = RepoAnalyzer()

    def _serialize(self, repo: dict) -> RepositoryResponseSchema:
        repo["_id"] = str(repo["_id"])
        return RepositoryResponseSchema(**repo)

    # service to create a repository
    async def create_repository(self, github_link: str) -> RepositoryResponseSchema:
        # check if already exists
        existing = await self.collection.find_one({"github_link": github_link})
        if existing:
            return self._serialize(existing)

        # ingest
        ingestion_result = self.ingestion.run(github_link, self.chunks_collection)

        # analyze
        analysis = self.analyzer.analyze(ingestion_result["chunks"])

        # build entity
        repo = Repository(
            github_link=github_link,
            description=analysis["description"],
            summary=analysis["summary"],
            technologies=analysis["technologies"],
            workflow_diagram=analysis["workflow_diagram"],
            architecture_diagram=analysis["architecture_diagram"],
            er_diagram=analysis["er_diagram"],
            setup_guide=analysis.get("setup_guide"),
            created_at=datetime.utcnow(),
            updated_at=datetime.utcnow(),
        )

        # store
        result = await self.collection.insert_one(
            repo.model_dump(by_alias=True, exclude={"id"})
        )

        stored = await self.collection.find_one({"_id": result.inserted_id})
        return self._serialize(stored)

    # service to get a repository by id
    async def get_repository(self, repo_id: str) -> RepositoryResponseSchema:
        repo = await self.collection.find_one({"_id": ObjectId(repo_id)})
        if not repo:
            raise ValueError(f"Repository {repo_id} not found")
        return self._serialize(repo)