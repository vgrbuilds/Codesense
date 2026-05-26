from fastapi import APIRouter, HTTPException
from app.modules.chat.chat_schema import (
    SendMessageSchema,
    MessageResponseSchema,
    ConversationResponseSchema,
)
from app.modules.chat.chat_service import ChatService
from app.core.db_connect import mongodb

router = APIRouter(prefix="/chat", tags=["chat"])


# defining the chat API class
class ChatAPI:

    def __init__(self):
        self.service = ChatService(mongodb.get_database())

    # api to get conversation by project id
    async def get_conversation(self, project_id: str) -> ConversationResponseSchema:
        try:
            return await self.service.get_conversation(project_id)
        except ValueError as e:
            raise HTTPException(status_code=404, detail=str(e))

    # api to send a message
    async def send_message(self, conversation_id: str, repo_id: str, data: SendMessageSchema) -> MessageResponseSchema:
        try:
            return await self.service.send_message(conversation_id, repo_id, data.content)
        except Exception as e:
            raise HTTPException(status_code=500, detail=str(e))


# ── routes ────────────────────────────────────────────────
chat_api = ChatAPI()


@router.get("/{project_id}", response_model=ConversationResponseSchema)
async def get_conversation(project_id: str):
    return await chat_api.get_conversation(project_id)


@router.post("/{conversation_id}/message", response_model=MessageResponseSchema)
async def send_message(conversation_id: str, repo_id: str, data: SendMessageSchema):
    return await chat_api.send_message(conversation_id, repo_id, data)