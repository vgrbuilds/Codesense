#importing all the necessary modules
from motor.motor_asyncio import AsyncIOMotorClient , AsyncIOMotorDatabase
from src.core.config import config



# Defining the MongoDB class to handle all database operations
class MongoDB:
    client: AsyncIOMotorClient | None = None
    database: AsyncIOMotorDatabase | None = None
    #defining the class method to connect to the MongoDB database
    @classmethod
    async def connect(cls):
        cls.cleint = AsyncIOMotorClient(config.mongo_uri)
        cls.database = cls.cleint[config.database_name]
        print("The server app is successfully connected to the MongoDB database")
    #defining the class method to disconnect from the MongoDB database
    @classmethod
    async def disconnect(cls):
        if cls.client:
            cls.client.close()
            print("the server app has successfully disconnected from the MongoDB database")

