#importing all the needed modules
from motor.motor_asyncio import AsyncIOMotorClient
from pymongo import MongoClient
from app.core.config import settings

# creating the database client class
class DatabaseClient:

    # init function that initializes the mongo db client
    def __init__(self):
        try:
            self.client = AsyncIOMotorClient(settings.MONGO_URI)
            self.database = self.client[settings.DATABASE_NAME]
            self.sync_client = MongoClient(settings.MONGO_URI)
            self.sync_database = self.sync_client[settings.DATABASE_NAME]
            print("MongoDB client initialized successfully.")
        
        except Exception as error:
            print(f"Error initializing MongoDB client: {error}")
            raise

    # function to establish the database connection
    async def connect_to_database(self):
        try:
            await self.client.server_info()
            print("Connected to MongoDB successfully.")
        except Exception as error:
            print(f"Error connecting to MongoDB: {error}")
            raise

    # function to retrieve the database
    def get_database(self):
        return self.database

    # function to retrieve the synchronous database
    def get_sync_database(self):
        return self.sync_database
    
    # function to close the database connection
    async def close_database_connection(self):
        try:
            self.client.close()
            print("MongoDB connection closed successfully.")
        except Exception as error:
            print(f"Error closing MongoDB connection: {error}")
            raise

    # function to get a specific collection from the database
    def get_collection(self, name: str):
        return self.get_database()[name]


# creating the database client instance
mongodb = DatabaseClient()

