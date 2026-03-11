from data.database import read_query, insert_query, update_query
from data.models import User, UserCreate
from common.security import hash_password
from common.exceptions import NotFoundError
from typing import Optional


def _get_user_by_username_internal(username: str) -> Optional[User]:
    """Internal method to get user by username."""
    rows = read_query(
        """
        SELECT idusers, firstname, lastname, username, password, email
        FROM users
        WHERE username = ?
        """,
        (username,)
    )
    
    if not rows:
        return None
    
    return User.from_query_result(*rows[0])


def _get_by_id_internal(user_id: int) -> Optional[User]:
    """Internal method to get user by ID."""
    rows = read_query(
        """
        SELECT idusers, firstname, lastname, username, password, email
        FROM users
        WHERE idusers = ?
        """,
        (user_id,)
    )
    
    if not rows:
        return None
    
    return User.from_query_result(*rows[0])


def create_user(user_data: UserCreate) -> User:
    """Create a new user."""
    # Check if username already exists
    existing_user = _get_user_by_username_internal(user_data.username)
    
    if existing_user:
        raise ValueError("Username already exists")
    
    # Hash password
    hashed_password = hash_password(user_data.password)
    
    # Insert user
    user_id = insert_query(
        """
        INSERT INTO users (firstname, lastname, username, password, email)
        VALUES (?, ?, ?, ?, ?)
        """,
        (
            user_data.firstname,
            user_data.lastname,
            user_data.username,
            hashed_password,
            user_data.email
        )
    )
    
    # Return created user
    user = _get_by_id_internal(user_id)
    
    if not user:
        raise NotFoundError("Failed to retrieve created user")
    
    return user