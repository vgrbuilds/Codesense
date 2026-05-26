# importing all the required modules
from fastapi import APIRouter

from app.modules.profile.user_schema import (
    UserSchema,
    AuthSchema,
    AuthResponseSchema,
)

from app.modules.profile.auth_service import AuthService


# creating auth router
router = APIRouter(
    prefix="/auth",
    tags=["Authentication"],
)


# register route
@router.post(
    "/register",
    response_model=AuthResponseSchema,
)
async def register_user(user_data: UserSchema):
    return await AuthService.register_user(user_data)


# login route
@router.post(
    "/login",
    response_model=AuthResponseSchema,
)
async def login_user(auth_data: AuthSchema):
    return await AuthService.login_user(auth_data)
