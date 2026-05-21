# import all the necessary modules
from fastapi import APIRouter, Depends
from src.schemas.message import MessageCreateSchema, MessageQuerySchema
from src.services.message_service import MessageService
from src.core.security import get_current_user

# defining the router
router = APIRouter(prefix="/messages", tags=["messages"])

# endpoint to create a message
@router.post("")
async def create_message(
    message_data: MessageCreateSchema,
    current_user: dict = Depends(get_current_user),
):
    response = await MessageService.create_message(current_user["id"], message_data)
    return response


# endpoint to query repository with rag
@router.post("/query")
async def query_repository(
    query_data: MessageQuerySchema,
    current_user: dict = Depends(get_current_user),
):
    response = await MessageService.query_repository(current_user["id"], query_data)
    return response
