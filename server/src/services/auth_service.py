#importing all the necessary modules
from datetime import datetime
from src.db.mongo import MongoDB
from src.models.user import UserModel
from src.core.security import ( hash_password ,verify_password ,create_access_token)

# defining the class to handle all authentication related operations
class AuthService:

    @staticmethod
    async def register_user(user_data):
        users_collection = MongoDB.database["users"]

        existing_user = await users_collection.find_one({
            "email": user_data.email
        })

        if existing_user:
            return {
                "success": False,
                "message": "User already exists"
            }

        hashed_password = hash_password(
            user_data.password
        )

        new_user = UserModel(
            email=user_data.email,
            username=user_data.username,
            hashed_password=hashed_password,
            created_at=datetime.utcnow()
        )

        result = await users_collection.insert_one(
            new_user.model_dump()
        )

        token = create_access_token({
            "user_id": str(result.inserted_id),
            "email": user_data.email
        })

        return {
            "success": True,
            "message": "User registered successfully",
            "user_id": str(result.inserted_id),
            "access_token": token,
            "token_type": "bearer"
        }

    @staticmethod
    async def login_user(user_data):
        users_collection = MongoDB.database["users"]

        user = await users_collection.find_one({
            "email": user_data.email
        })

        if not user:
            return {
                "success": False,
                "message": "Invalid credentials"
            }

        is_valid_password = verify_password(
            user_data.password,
            user["hashed_password"]
        )

        if not is_valid_password:
            return {
                "success": False,
                "message": "Invalid credentials"
            }

        token = create_access_token({
            "user_id": str(user["_id"]),
            "email": user["email"]
        })

        return {
            "success": True,
            "access_token": token,
            "token_type": "bearer"
        }