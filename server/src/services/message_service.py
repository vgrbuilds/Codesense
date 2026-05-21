# importing all the necessary modules
import math
from datetime import datetime
from bson import ObjectId
from langchain_core.output_parsers import StrOutputParser
from langchain_core.prompts import PromptTemplate
from langchain_google_genai import ChatGoogleGenerativeAI
from src.core.config import config
from src.db.mongo import MongoDB
from src.models.message import MessageModel
from src.schemas.message import MessageCreateSchema, MessageQuerySchema, MessageResponseSchema


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

    #method to perform rag query on repository chunks
    @staticmethod
    async def query_repository(user_id: str, query_data: MessageQuerySchema):
        repositories_collection = MongoDB.database["repositories"]
        messages_collection = MongoDB.database["messages"]

        try:
            repository = await repositories_collection.find_one({"_id": ObjectId(query_data.repository_id)})
        except Exception:
            return {"success": False, "message": "Invalid repository ID format"}

        if not repository:
            return {"success": False, "message": "Repository not found"}

        if not config.gemini_key:
            return {"success": False, "message": "GEMINI_KEY is not configured in the environment"}

        question_embedding = await MessageService._generate_embedding(query_data.question)
        if not question_embedding:
            return {"success": False, "message": "Failed to generate query embedding"}

        top_chunks = await MessageService._retrieve_relevant_chunks(
            repository_id=query_data.repository_id,
            question_embedding=question_embedding,
            top_k=max(1, query_data.top_k),
        )
        if not top_chunks:
            return {"success": False, "message": "No chunks found for this repository"}

        answer = await MessageService._generate_grounded_answer(query_data.question, top_chunks)
        references = [
            {
                "chunk_id": chunk["id"],
                "file_path": chunk["file_path"],
                "start_line": chunk.get("start_line"),
                "end_line": chunk.get("end_line"),
                "score": round(chunk["score"], 6),
            }
            for chunk in top_chunks
        ]

        user_message = MessageModel(
            conversation_id=query_data.conversation_id,
            user_id=user_id,
            role="user",
            content=query_data.question,
            references=[],
            created_at=datetime.utcnow(),
        )
        assistant_message = MessageModel(
            conversation_id=query_data.conversation_id,
            user_id=user_id,
            role="assistant",
            content=answer,
            references=references,
            created_at=datetime.utcnow(),
        )
        await messages_collection.insert_one(user_message.model_dump())
        await messages_collection.insert_one(assistant_message.model_dump())

        return {
            "success": True,
            "answer": answer,
            "references": references,
            "retrieved_chunks": len(top_chunks),
        }

    #method to generate embeddings for query text
    @staticmethod
    async def _generate_embedding(text: str) -> list[float]:
        from src.services.ingestion.llm_helpers import generate_embedding
        return await generate_embedding(text)

    #method to retrieve top similar chunks using cosine similarity
    @staticmethod
    async def _retrieve_relevant_chunks(repository_id: str, question_embedding: list[float], top_k: int) -> list[dict]:
        chunks_collection = MongoDB.database["chunks"]
        cursor = chunks_collection.find({"repository_id": repository_id})
        scored_chunks: list[dict] = []

        async for chunk in cursor:
            chunk_embedding = chunk.get("embedding") or []
            if not chunk_embedding:
                continue
            score = MessageService._cosine_similarity(question_embedding, chunk_embedding)
            chunk["score"] = score
            chunk["id"] = str(chunk.pop("_id"))
            scored_chunks.append(chunk)

        scored_chunks.sort(key=lambda item: item["score"], reverse=True)
        return scored_chunks[:top_k]

    #method to compute cosine similarity between two vectors
    @staticmethod
    def _cosine_similarity(vec_a: list[float], vec_b: list[float]) -> float:
        if not vec_a or not vec_b or len(vec_a) != len(vec_b):
            return -1.0

        dot_product = sum(a * b for a, b in zip(vec_a, vec_b))
        norm_a = math.sqrt(sum(a * a for a in vec_a))
        norm_b = math.sqrt(sum(b * b for b in vec_b))
        if norm_a == 0 or norm_b == 0:
            return -1.0
        return dot_product / (norm_a * norm_b)

    #method to generate grounded answer from retrieved chunks
    @staticmethod
    async def _generate_grounded_answer(question: str, chunks: list[dict]) -> str:
        llm = ChatGoogleGenerativeAI(
            model="gemini-1.5-flash",
            google_api_key=config.gemini_key,
            temperature=0.2,
        )

        context_blocks = []
        for idx, chunk in enumerate(chunks, start=1):
            context_blocks.append(
                f"[Chunk {idx}] File: {chunk.get('file_path')} Lines: {chunk.get('start_line')}-{chunk.get('end_line')}\n{chunk.get('content', '')}"
            )

        chain = (
            PromptTemplate.from_template(
                "You are a codebase assistant. Answer only using the provided context. "
                "If context is insufficient, clearly say so.\n\nQuestion:\n{question}\n\nContext:\n{context}"
            )
            | llm
            | StrOutputParser()
        )
        return await chain.ainvoke({"question": question, "context": "\n\n---\n\n".join(context_blocks)})
