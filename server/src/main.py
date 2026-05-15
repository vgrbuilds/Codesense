#import all the necessary modules
from fastapi import FastAPI
from src.db.mongo import MongoDB
from src.api.auth import router as auth_router
from src.api.user import router as user_router
from src.api.project import router as project_router
from src.api.chunk import router as chunk_router
from src.api.message import router as message_router
from src.api.repository import router as repository_router
from src.api.ingest import router as ingest_router

# initializing the app
app = FastAPI()

# connecting the database
@app.on_event("startup")
async def startup():
    await MongoDB.connect()

# handle auth
app.include_router(auth_router)
app.include_router(user_router)
app.include_router(project_router)
app.include_router(chunk_router)
app.include_router(message_router)
app.include_router(repository_router)
app.include_router(ingest_router)

