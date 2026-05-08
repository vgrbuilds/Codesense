#import all the necessary modules
from fastapi import FastAPI
from src.db.mongo import MongoDB
from src.api.auth import router as auth_router
#initializing the app
app = FastAPI()
#connecting the database
@app.on_event("startup")
async def startup():
    await MongoDB.connect()

#handle auth

app.include_router(auth_router)

