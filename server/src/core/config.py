#importing all the needed modules
from dotenv import load_dotenv
import os

#loading the environment variables from the .env file
load_dotenv()

# defining the config class
class Config:
    mongo_uri = os.getenv("MONGO_URI")
    database_name = os.getenv("DATABASE_NAME")
    gemini_key = os.getenv("GEMINI_KEY")
    github_token = os.getenv("GITHUB_TOKEN")
    cloudinary_cloud_name = os.getenv("CLOUDINARY_CLOUD_NAME")
    cloudinary_api_key = os.getenv("CLOUDINARY_API_KEY")
    cloudinary_api_secret = os.getenv("CLOUDINARY_API_SECRET")
    port = int(os.getenv("PORT", 8000))
    secret_key = os.getenv("SECRET_KEY")
    algorithm = os.getenv("ALGORITHM")
    access_token_expire_minutes = int(os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES", "60"))
    vector_index_name = os.getenv("VECTOR_INDEX_NAME", "chunks_vector_index")

    #method to validate base required env vars for server startup
    def validate_required(self) -> None:
        required = {
            "MONGO_URI": self.mongo_uri,
            "DATABASE_NAME": self.database_name,
            "SECRET_KEY": self.secret_key,
            "ALGORITHM": self.algorithm,
            "ACCESS_TOKEN_EXPIRE_MINUTES": self.access_token_expire_minutes,
        }
        missing = [key for key, value in required.items() if value in (None, "")]
        if missing:
            raise ValueError(f"Missing required environment variables: {', '.join(missing)}")


#using the class
config = Config()
