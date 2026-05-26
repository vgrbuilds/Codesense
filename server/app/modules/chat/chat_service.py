from datetime import datetime
from bson import ObjectId
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_mongodb import MongoDBAtlasVectorSearch
from langchain_google_genai import GoogleGenerativeAIEmbeddings
from app.modules.chat.chat_model import Conversation, Message
from app.modules.chat.chat_schema import ConversationResponseSchema, MessageResponseSchema
from app.core.config import settings


# defining the chat service class
class ChatService:

    def __init__(self, db):
        self.conversations = db["conversations"]
        self.messages = db["messages"]
        self.chunks = db["chunks"]
        self.llm = ChatGoogleGenerativeAI(
            model=settings.GEMINI_MODEL,
            google_api_key=settings.GEMINI_API_KEY
        )
        self.embeddings = GoogleGenerativeAIEmbeddings(
            model="models/text-embedding-004",
            google_api_key=settings.GEMINI_API_KEY
        )

    def _serialize_message(self, message: dict) -> MessageResponseSchema:
        message["_id"] = str(message["_id"])
        return MessageResponseSchema(**message)

    def _serialize_conversation(self, conversation: dict, messages: list) -> ConversationResponseSchema:
        conversation["_id"] = str(conversation["_id"])
        return ConversationResponseSchema(
            **conversation,
            messages=messages
        )

    # service to create a conversation
    async def create_conversation(self, project_id: str, user_id: str) -> str:
        conversation = Conversation(
            project_id=project_id,
            user_id=user_id,
            created_at=datetime.utcnow(),
        )

        result = await self.conversations.insert_one(
            conversation.model_dump(by_alias=True, exclude={"id"})
        )

        return str(result.inserted_id)

    # service to get conversation with messages by project id
    async def get_conversation(self, project_id: str) -> ConversationResponseSchema:
        conversation = await self.conversations.find_one({"project_id": project_id})
        if not conversation:
            raise ValueError(f"Conversation for project {project_id} not found")

        conversation_id = str(conversation["_id"])

        # fetch all messages in order
        messages = []
        async for message in self.messages.find(
            {"conversation_id": conversation_id}
        ).sort("created_at", 1):
            messages.append(self._serialize_message(message))

        return self._serialize_conversation(conversation, messages)

    # service to send a message and get a response
    async def send_message(self, conversation_id: str, repo_id: str, content: str) -> MessageResponseSchema:
        # 1 - save user message
        user_message = Message(
            conversation_id=conversation_id,
            role="user",
            content=content,
            created_at=datetime.utcnow(),
        )
        await self.messages.insert_one(
            user_message.model_dump(by_alias=True, exclude={"id"})
        )

        # 2 - fetch conversation history for context
        history = []
        async for message in self.messages.find(
            {"conversation_id": conversation_id}
        ).sort("created_at", 1):
            history.append(f"{message['role']}: {message['content']}")
        history_text = "\n".join(history)

        # 3 - query vector store filtered by repo_id
        vector_store = MongoDBAtlasVectorSearch(
            collection=self.chunks,
            embedding=self.embeddings,
            index_name="vector_index",
        )
        relevant_chunks = vector_store.similarity_search(
            content,
            k=5,
            pre_filter={"repo_id": {"$eq": repo_id}},
        )
        context = "\n\n".join([c.page_content for c in relevant_chunks])

        # 4 - build prompt with context + history
        prompt = f"""
You are an expert code assistant. Answer the user's question based on the codebase context provided.

Codebase context:
{context}

Conversation history:
{history_text}

User: {content}

Answer clearly and concisely. If the answer is not in the context, say so.
"""

        # 5 - get response from gemini
        response = self.llm.invoke(prompt)

        # 6 - save assistant message
        assistant_message = Message(
            conversation_id=conversation_id,
            role="assistant",
            content=response.content,
            created_at=datetime.utcnow(),
        )
        result = await self.messages.insert_one(
            assistant_message.model_dump(by_alias=True, exclude={"id"})
        )

        stored = await self.messages.find_one({"_id": result.inserted_id})
        return self._serialize_message(stored)