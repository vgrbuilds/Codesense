#import all the necessary modules
from fastapi import APIRouter, Depends
from fastapi.security import OAuth2PasswordRequestForm
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
async def login_user(form_data: OAuth2PasswordRequestForm = Depends()):
    login_data = UserLoginSchema(email=form_data.username, password=form_data.password)
    response = await AuthService.login_user(login_data)
    return response
