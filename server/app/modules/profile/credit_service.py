# importing all the required modules
from datetime import datetime, timedelta
from fastapi import HTTPException, status
from bson import ObjectId
from app.core.config import settings
from app.core.db_connect import mongodb

# defining the credit service class
class CreditService:

    # method to refresh credits if needed
    @staticmethod
    async def refresh_credits_if_needed(user_id: str):

        users_collection = mongodb.database["users"]

        user = await users_collection.find_one({
            "_id": ObjectId(user_id)
        })

        if not user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="User not found"
            )

        last_reset = user.get(
            "credits_last_reset"
        )

        # first time setup
        if not last_reset:

            await users_collection.update_one(
                {"_id": ObjectId(user_id)},
                {
                    "$set": {
                        "credits": settings.MONTHLY_FREE_CREDITS,
                        "credits_last_reset": datetime.utcnow()
                    }
                }
            )

            return

        # checking if 30 days passed
        if datetime.utcnow() >= (
            last_reset + timedelta(days=30)
        ):

            await users_collection.update_one(
                {"_id": ObjectId(user_id)},
                {
                    "$set": {
                        "credits": settings.MONTHLY_FREE_CREDITS,
                        "credits_last_reset": datetime.utcnow()
                    }
                }
            )

    #method ot get credits
    @staticmethod
    async def get_user_credits(user_id: str):

        users_collection = mongodb.database["users"]

        user = await users_collection.find_one({
            "_id": ObjectId(user_id)
        })

        if not user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="User not found"
            )

        return {
            "credits": user["credits"]
        }
    
    #method to decrement credits
    @staticmethod
    async def decrement_credits(
        user_id: str,
        amount: int = 30
    ):

        users_collection = mongodb.database["users"]

        user = await users_collection.find_one({
            "_id": ObjectId(user_id)
        })

        if not user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="User not found"
            )

        if user["credits"] < amount:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Insufficient credits"
            )

        await users_collection.update_one(
            {"_id": ObjectId(user_id)},
            {
                "$inc": {
                    "credits": -amount
                },
                "$set": {
                    "updated_at": datetime.utcnow()
                }
            }
        )

        updated_user = await users_collection.find_one({
            "_id": ObjectId(user_id)
        })

        return {
            "credits": updated_user["credits"]
        }