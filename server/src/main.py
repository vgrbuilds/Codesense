#import all the necessary modules
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from src.core.config import config
from src.db.mongo import MongoDB
from src.api.auth import router as auth_router
from src.api.user import router as user_router
from src.api.project import router as project_router
from src.api.chunk import router as chunk_router
from src.api.message import router as message_router
from src.api.repository import router as repository_router
from src.api.ingest import router as ingest_router
from src.api.system import router as system_router

# initializing the app
app = FastAPI()

# enabling permissive cors for all clients
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# connecting the database
@app.on_event("startup")
async def startup():
    config.validate_required()
    await MongoDB.connect()


# disconnecting the database on shutdown
@app.on_event("shutdown")
async def shutdown():
    await MongoDB.disconnect()

# handle auth
app.include_router(auth_router)
app.include_router(user_router)
app.include_router(project_router)
app.include_router(chunk_router)
app.include_router(message_router)
app.include_router(repository_router)
app.include_router(ingest_router)
app.include_router(system_router)
