from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from common.auth import authenticate_user, create_access_token
from common.response import success
from common.exceptions import UnauthorizedError
from data.models import User, UserCreate, UserPublic
from services import user_service

auth_router = APIRouter()


@auth_router.post('/register')
def register_user(user: UserCreate):
    create_user = user_service.create_user(user)
    return success(
        data = UserPublic
    )


@auth_router.post('/login')
def login(form_data: OAuth2PasswordRequestForm = Depends()):

    '''
    Login endpoint to get JWT access token.
    Returns access token for authentication.
    '''
