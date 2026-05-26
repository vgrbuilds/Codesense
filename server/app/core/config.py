#importing all the required modules
from pydantic_settings import BaseSettings
from pydantic import ConfigDict, Field

#defining the settings class
class Settings(BaseSettings):

    #mongo db
    MONGO_URI: str
    DATABASE_NAME: str
    #cloudinary
    CLOUDINARY_CLOUD_NAME: str
    CLOUDINARY_API_KEY: str
    CLOUDINARY_API_SECRET: str
    #ai 
    GEMINI_API_KEY: str
    GEMINI_MODEL: str = Field(validation_alias="GEMINI_MODEL_NAME")
    #others
    SECRET_KEY: str
    ALGORITHM: str
    ACCESS_TOKEN_EXPIRE_MINUTES: int
    MONTHLY_FREE_CREDITS: int
    #server
    PORT: int
    
    #config class
    model_config = ConfigDict(env_file=".env", extra="ignore")



# Backward-compatible singleton expected by other modules
settings = Settings()
