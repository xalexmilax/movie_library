from datetime import datetime, timedelta
from jose import JWTError, jwt
from fastapi import HTTPException, status, Depends
from fastapi.security import OAuth2PasswordBearer, HTTPBearer, HTTPAuthorizationCredentials
from data.models import User, UserRole
from services import user_service
from common.security import verify_password
import os
from dotenv import load_dotenv

load_dotenv()

SECRET_KEY = os.getenv("SECRET_KEY")
ALGORITHM = os.getenv("ALGORITHM")
ACCESS_TOKEN_EXPIRE_MINUTES = 30

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="auth/login")
security = HTTPBearer(auto_error=False)


def authenticate_user(username: str, password: str):
    """Authenticate user by username and password."""
    user = user_service._get_user_by_username_internal(username)
    
    if not user:
        return False
    
    if not verify_password(password, user.password):
        return False
    
    return user


def create_access_token(data: dict):
    """Create JWT access token."""
    to_encode = data.copy()
    expire = datetime.now() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    to_encode.update({"exp": expire})
    return jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)


def get_current_user(credentials: HTTPAuthorizationCredentials = Depends(security)) -> User:
    """Get current authenticated user from JWT token."""
    if not credentials:
        raise HTTPException(status_code=401, detail="Not authenticated")
    
    token = credentials.credentials
    
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        user_id: int = payload.get("user_id")
        
        if not user_id:
            raise HTTPException(status_code=401, detail="Invalid token payload")
        
        user = user_service._get_by_id_internal(user_id)
        
        if not user:
            raise HTTPException(status_code=401, detail="User not found")
        
        return user
        
    except JWTError:
        raise HTTPException(status_code=401, detail="Invalid token")


async def get_optional_user(
    credentials: HTTPAuthorizationCredentials | None = Depends(security)
) -> User | None:
    """Get current user if authenticated, otherwise return None."""
    if not credentials:
        return None
    
    try:
        payload = jwt.decode(
            credentials.credentials,
            SECRET_KEY,
            algorithms=[ALGORITHM]
        )
        user_id: int | None = payload.get("user_id")
        
        if user_id is None:
            return None
        
        user = user_service._get_by_id_internal(user_id)
        
        return user if user else None
        
    except JWTError:
        return None


def get_current_admin(current_user: User = Depends(get_current_user)) -> User:
    """Verify that current user is an Admin."""
    # Since your users table doesn't have role_id, you'll need to add it
    # For now, check if user is admin by username or add a role check
    # Option 1: Check by username
    if current_user.username != "admin":  # Temporary check
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Admin privileges required"
        )
    
    return current_user