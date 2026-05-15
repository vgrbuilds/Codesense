# importing all the necessary modules
from datetime import datetime
from bson import ObjectId
from src.db.mongo import MongoDB
from src.models.message import MessageModel
from src.schemas.message import MessageCreateSchema, MessageResponseSchema


class MessageService:
    @staticmethod
    async def create_message(user_id: str, message_data: MessageCreateSchema):
        messages_collection = MongoDB.database["messages"]

        new_message = MessageModel(
            conversation_id=message_data.conversation_id,
            user_id=user_id,
            role=message_data.role,
            content=message_data.content,
            references=message_data.references,
            created_at=datetime.utcnow(),
        )

        result = await messages_collection.insert_one(new_message.model_dump())
        return {
            "success": True,
            "message": "Message created successfully",
            "message_id": str(result.inserted_id),
        }

    @staticmethod
    async def get_message(message_id: str):
        messages_collection = MongoDB.database["messages"]

        try:
            message = await messages_collection.find_one({"_id": ObjectId(message_id)})
        except Exception:
            return {"success": False, "message": "Invalid message ID format"}

        if not message:
            return {"success": False, "message": "Message not found"}

        message["id"] = str(message.pop("_id"))
        return {"success": True, "data": MessageResponseSchema(**message).model_dump()}
