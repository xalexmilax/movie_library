from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from common.auth import authenticate_user, create_access_token
from common.response import success

auth_router = APIRouter()


@auth_router.post("/login")
def login(form_data: OAuth2PasswordRequestForm = Depends()):
    """
    Login endpoint to get JWT access token.
    
    **Request Body (form data):**
    - `username`: Your username
    - `password`: Your password
    
    **Returns:** Access token for authentication
    """
    user = authenticate_user(form_data.username, form_data.password)
    
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    access_token = create_access_token(
        data={"user_id": user.idusers}  # Use idusers, not user_id
    )
    
    return success(
        data={
            "access_token": access_token,
            "token_type": "bearer",
            "user_id": user.idusers,
            "username": user.username
        },
        message="Login successful"
    )