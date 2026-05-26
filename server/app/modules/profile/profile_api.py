# importing the necessary modules
from fastapi import APIRouter, Header, HTTPException, status

from app.modules.profile.auth_service import AuthService
from app.modules.profile.user_schema import (
    UpdateUserSchema,
    UserResponseSchema,
    UserDeleteResponseSchema,
)
from app.modules.profile.user_service import UserService

router = APIRouter(prefix="/profile", tags=["Profile"])


def _extract_user_id_from_authorization(authorization: str) -> str:
    try:
        token = authorization.split(" ")[1]
    except Exception:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid Authorization header",
        )

    return token


@router.get("/me", response_model=UserResponseSchema)
async def get_profile(authorization: str = Header(...)):
    token = _extract_user_id_from_authorization(authorization)
    current_user = await AuthService.get_current_user(token)
    return await UserService.get_user_by_id(current_user["user_id"])


@router.patch("/me", response_model=UserResponseSchema)
async def update_profile(update_data: UpdateUserSchema, authorization: str = Header(...)):
    token = _extract_user_id_from_authorization(authorization)
    current_user = await AuthService.get_current_user(token)
    return await UserService.update_user(current_user["user_id"], update_data)


@router.delete("/me", response_model=UserDeleteResponseSchema)
async def delete_profile(authorization: str = Header(...)):
    token = _extract_user_id_from_authorization(authorization)
    current_user = await AuthService.get_current_user(token)
    return await UserService.delete_user(current_user["user_id"])

