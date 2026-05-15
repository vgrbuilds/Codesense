# import all the necessary modules
from fastapi import APIRouter, Depends, HTTPException, Path, status
from src.schemas.user import UserUpdateSchema
from src.services.user_service import UserService
from src.core.security import get_current_user

# defining the router
router = APIRouter(prefix="/users", tags=["users"])

# helper to enforce ownership of user resources
def ensure_ownership(user_id: str, current_user: dict):
    if current_user["id"] != user_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized to access this resource"
        )

# defining the endpoint to get user details
@router.get("/{user_id}")
async def get_user_details(
    user_id: str = Path(..., description="The ID of the user to retrieve"),
    current_user: dict = Depends(get_current_user),
):
    ensure_ownership(user_id, current_user)
    response = await UserService.get_user_details(user_id)
    return response

# defining the endpoint to update user details
@router.patch("/{user_id}")
async def update_user_details(
    update_data: UserUpdateSchema,
    user_id: str = Path(...),
    current_user: dict = Depends(get_current_user),
):
    ensure_ownership(user_id, current_user)
    response = await UserService.update_user(user_id, update_data)
    return response

# defining the endpoint to delete user account
@router.delete("/{user_id}")
async def delete_user_account(
    user_id: str = Path(...),
    current_user: dict = Depends(get_current_user),
):
    ensure_ownership(user_id, current_user)
    response = await UserService.delete_user(user_id)
    return response