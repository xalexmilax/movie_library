from pydantic import BaseModel, EmailStr, Field
from datetime import datetime
from typing import Optional


# -----------------  User Models -----------------


class UserRole:
    ADMIN = 1
    USER = 2


class UserCreate(BaseModel):
    first_name: str = Field(min_length=2, max_length=32)
    last_name: str = Field(min_length=2, max_length=32)
    email: EmailStr
    username: str = Field(min_length=2, max_length=16)
    password: str
    email: EmailStr


class User(BaseModel):
    idusers: int
    firstname: str
    lastname: str
    username: str
    password: str
    email: str
    
    @classmethod
    def from_query_result(cls, idusers, firstname, lastname, username, password, email):
        return cls(
            idusers=idusers,
            firstname=firstname,
            lastname=lastname,
            username=username,
            password=password,
            email=email
        )
    
class UserPublic(BaseModel):
    """ Public facing User representation. Hides sensitive fields. """
    user_id: int
    first_name: str
    last_name: str
    username: str
    is_deleted: bool = False

    @classmethod
    def from_user(cls, user: User):
        return cls(
            user_id=user.user_id,
            first_name=user.first_name,
            last_name=user.last_name,
            username=user.username,
            is_deleted=user.is_deleted
        )


    
# -----------------  Movie Models -----------------

class MovieCreate(BaseModel):
    """Model for creating a new movie"""
    title: str = Field(min_length=1, max_length=200)
    director: str = Field(min_length=1, max_length=100)
    releaseyear: int = Field(ge=1888, le=2100)  # First movie was published in 1888


class MovieUpdate(BaseModel):
    """Model for updating a movie"""
    title: str = Field(min_length=1, max_length=200)
    director: str = Field(min_length=1, max_length=100)
    releaseyear: int = Field(ge=1888, le=2100)
    rating: float = Field(ge=0.0, le=10.0)


class MovieResponse(BaseModel):
    """Model for movie response"""
    id: int
    title: str
    director: str
    releaseyear: int
    rating: float
    
    class Config:
        from_attributes = True