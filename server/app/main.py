#importing the necessary modules
from fastapi import FastAPI
from app.core.config import Settings
from app.core.db_connect import mongodb
from app.modules.profile.auth_api import router as auth_router
from app.modules.project.project_api import router as project_router
from app.modules.chat.chat_api import router as chat_router
from app.modules.profile.profile_api import router as profile_router

# creating the FastAPI app instance
app = FastAPI(title="Codesense API", version="1.0")

# including the API routers
app.include_router(auth_router)
app.include_router(project_router)
app.include_router(chat_router)
app.include_router(profile_router)




