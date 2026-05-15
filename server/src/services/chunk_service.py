#importing all the necessary modules
from bson import ObjectId
from datetime import datetime
from src.db.mongo import MongoDB
from src.models.chunk import ChunkModel
from src.schemas.chunk import ChunkCreateSchema,ChunkResponseSchema

# defining the chunk service class
class ChunkService:
    #method to create chunk
    @staticmethod
    async def create_chunk(chunk_data: ChunkCreateSchema):
        chunks_collection = MongoDB.database["chunks"]

        new_chunk = ChunkModel(
            **chunk_data.model_dump(),
            created_at=datetime.utcnow()
        )

        result = await chunks_collection.insert_one(
            new_chunk.model_dump()
        )

        return {
            "success": True,
            "message": "Chunk created successfully",
            "chunk_id": str(result.inserted_id),
        }
    
    #method to retrieve a chunk
    @staticmethod
    async def get_chunk(chunk_id: str):
        chunks_collection = MongoDB.database["chunks"]

        try:
            chunk = await chunks_collection.find_one({
                "_id": ObjectId(chunk_id)
            })
        except Exception:
            return {
                "success": False,
                "message": "Invalid chunk ID format"
            }
        if not chunk:
            return {"success": False,"message": "Chunk not found"}
        chunk["id"] = str(chunk.pop("_id"))
        return {"success": True,"data": ChunkResponseSchema(**chunk).model_dump()}
    
    #method to get the list of chunks by repo id 
    @staticmethod
    async def list_chunks_by_repository(repository_id: str):
        chunks_collection = MongoDB.database["chunks"]
        cursor = chunks_collection.find({"repository_id": repository_id})
        chunks = []
        async for chunk in cursor:
            chunk["id"] = str(chunk.pop("_id"))
            chunks.append(ChunkResponseSchema(**chunk).model_dump())
        return {"success": True,"data": chunks}