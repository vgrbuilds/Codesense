#importing all the needed modules
from dotenv import load_dotenv
from pydantic_settings import BaseSettings
import os

#loading the environment variables from the .env file
load_dotenv()

# defining the config class
class Config:
    mongo_uri = os.getenv("MONGO_URI")
    database_name = os.getenv("DATABASE_NAME")
    gemini_key = os.getenv("GEMINI_KEY")
    port = int(os.getenv("PORT", 8000))
    secret_key = os.getenv("SECRET_KEY")
    algorithm = os.getenv("ALGORITHM")
    access_token_expire_minutes = int(os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES"))


#using the class
config = Config()