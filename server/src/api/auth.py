#import all the necessary modules
from fastapi import APIRouter
from src.schemas.user import UserRegisterSchema , UserLoginSchema
from src.services.auth_service import AuthService

# defining the router
router = APIRouter(prefix="/auth", tags=["authentication"])


# defining the register endpoint
@router.post("/register")
#function to post
async def register_user(user: UserRegisterSchema):
    response = await AuthService.register_user(user)
    return response

#defining the login endpoint
@router.post("/login")
#function to login
async def login_user(user: UserLoginSchema):
    response = await AuthService.login_user(user)
    return response
