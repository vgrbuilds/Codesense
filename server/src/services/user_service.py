# importing all the necessary modules
from src.db.mongo import MongoDB
from src.schemas.user import UserUpdateSchema, UserResponseSchema
from src.core.security import hash_password
from bson import ObjectId  # Use lowercase 'd'

class UserService:
    @staticmethod
    async def get_user_details(user_id: str):
        users_collection = MongoDB.database["users"]
        
        try:
            # Convert string ID to BSON ObjectId for MongoDB
            user = await users_collection.find_one({"_id": ObjectId(user_id)})
        except Exception:
            return {"success": False, "message": "Invalid user ID format"}

        if not user:
            return {"success": False, "message": "User not found"}
        
        # Prepare data for UserResponseSchema: map _id to id
        user["id"] = str(user.pop("_id"))
        
        return {
            "success": True, 
            "data": UserResponseSchema(**user).model_dump()
        }

    @staticmethod
    async def update_user(user_id: str, update_data: UserUpdateSchema):
        users_collection = MongoDB.database["users"]
        
        # Filter out None values to allow partial updates (PATCH style)
        update_dict = {k: v for k, v in update_data.model_dump().items() if v is not None}

        # Hash password updates before saving to the database.
        if "new_password" in update_dict:
            update_dict["hashed_password"] = hash_password(update_dict.pop("new_password"))
        elif "password" in update_dict:
            update_dict["hashed_password"] = hash_password(update_dict.pop("password"))
        
        if not update_dict:
            return {"success": False, "message": "No data provided for update"}

        try:
            result = await users_collection.update_one(
                {"_id": ObjectId(user_id)},
                {"$set": update_dict}
            )
            
            if result.modified_count > 0:
                return {"success": True, "message": "User updated successfully"}
            return {"success": False, "message": "User not found or no changes made"}
            
        except Exception as e:
            return {"success": False, "message": f"Update failed: {str(e)}"}

    @staticmethod
    async def delete_user(user_id: str):
        users_collection = MongoDB.database["users"]
        
        try:
            result = await users_collection.delete_one({"_id": ObjectId(user_id)})
            if result.deleted_count > 0:
                return {"success": True, "message": "User deleted successfully"}
            return {"success": False, "message": "User not found"}
        except Exception:
            return {"success": False, "message": "Invalid user ID format"}