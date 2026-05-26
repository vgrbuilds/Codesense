# importing all the required modules
from datetime import datetime

from fastapi import HTTPException, status
from bson import ObjectId

from app.core.db_connect import mongodb
from app.core.security import create_access_token
from app.modules.profile.user_schema import UpdateCreditsSchema, UpdateUserSchema

# defining the user service class
class UserService:

    @staticmethod
    async def get_user_by_id(user_id: str):
        users_collection = mongodb.database["users"]
        user = await users_collection.find_one({
            "_id": ObjectId(user_id)
        })

        if not user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="User not found"
            )

        user["_id"] = str(user["_id"])

        return user


    @staticmethod
    async def update_user(
        user_id: str,
        update_data: UpdateUserSchema
    ):

        users_collection = mongodb.database["users"]

        update_fields = {
            key: value
            for key, value in update_data.model_dump().items()
            if value is not None
        }

        if not update_fields:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="No fields provided"
            )

        update_fields["updated_at"] = datetime.utcnow()

        await users_collection.update_one(
            {"_id": ObjectId(user_id)},
            {"$set": update_fields}
        )

        updated_user = await users_collection.find_one({
            "_id": ObjectId(user_id)
        })

        updated_user["_id"] = str(updated_user["_id"])

        return updated_user

    @staticmethod
    async def delete_user(user_id: str):

        users_collection = mongodb.database["users"]

        result = await users_collection.delete_one({
            "_id": ObjectId(user_id)
        })

        if result.deleted_count == 0:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="User not found"
            )

        return {
            "message": "User deleted successfully"
        }