# importing all the required modules
from datetime import datetime
from fastapi import HTTPException, status
from app.core.config import settings
from app.core.db_connect import mongodb
from app.modules.profile.user_schema import UserSchema,AuthSchema
from app.core.security import hash_password,verify_password,create_access_token,decode_access_token


# defining the auth service class
class AuthService:

    @staticmethod
    async def register_user(user_data: UserSchema):

        users_collection = mongodb.database["users"]

        # checking if user already exists
        existing_user = await users_collection.find_one({
            "email": user_data.email
        })

        if existing_user:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="User already exists"
            )

        # hashing password
        hashed_password = hash_password(
            user_data.password
        )

        # creating user document
        new_user = {
            "name": user_data.name,
            "email": user_data.email,
            "hashed_password": hashed_password,
            "profile_picture": user_data.profile_picture,
            "credits": settings.MONTHLY_FREE_CREDITS,
            "created_at": datetime.utcnow(),
            "updated_at": datetime.utcnow(),
            "credits_last_reset": datetime.utcnow()
        }

        # inserting user into database
        result = await users_collection.insert_one(
            new_user
        )

        # generating jwt token
        access_token = create_access_token({
            "user_id": str(result.inserted_id)
        })

        return {
            "access_token": access_token,
            "token_type": "bearer"
        }


    @staticmethod
    async def login_user(auth_data: AuthSchema):

        users_collection = mongodb.database["users"]

        # finding user
        user = await users_collection.find_one({
            "email": auth_data.email
        })

        if not user:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid credentials"
            )

        # verifying password
        is_password_valid = verify_password(
            auth_data.password,
            user["hashed_password"]
        )

        if not is_password_valid:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid credentials"
            )

        # generating access token
        access_token = create_access_token({
            "user_id": str(user["_id"])
        })

        return {
            "access_token": access_token,
            "token_type": "bearer"
        }


    @staticmethod
    async def get_current_user(token: str):

        try:

            payload = decode_access_token(token)

            return payload

        except Exception:

            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid or expired token"
            )