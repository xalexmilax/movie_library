from fastapi import APIRouter, Depends, Query, status
from typing import Optional
from data.models import MovieCreate, MovieUpdate, MovieResponse, User
from services import movie_service
from common.auth import get_current_user, get_current_admin
from common.response import success

movies_router = APIRouter(prefix="/movies", tags=["Movies"])


@movies_router.get("/", response_model=None)
def get_all_movies(
    title: Optional[str] = Query(None, description="Filter by movie title"),
    sort_by_rating: bool = Query(False, description="Sort by rating descending"),
    current_user: User = Depends(get_current_user)
):
    """Get all movies with optional filtering and sorting."""
    movies = movie_service.get_all_movies(
        title_filter=title,
        sort_by_rating=sort_by_rating
    )
    
    return success(
        data=movies,
        message=f"Found {len(movies)} movie(s)"
    )


@movies_router.get("/{movie_id}", response_model=None)
def get_movie(
    movie_id: int,
    current_user: User = Depends(get_current_user)
):
    """Get a specific movie by ID."""
    movie = movie_service.get_movie_by_id(movie_id)
    
    return success(
        data=movie,
        message="Movie retrieved successfully"
    )


@movies_router.post("/", status_code=status.HTTP_201_CREATED, response_model=None)
async def create_movie(
    movie_data: MovieCreate,
    current_user: User = Depends(get_current_admin)
):
    """Create a new movie. Rating enriched asynchronously from OMDb API."""
    movie = movie_service.create_movie(movie_data)
    
    return success(
        data=movie,
        message="Movie created successfully. Rating enrichment in progress.",
        status_code=status.HTTP_201_CREATED
    )


@movies_router.put("/{movie_id}", response_model=None)
def update_movie(
    movie_id: int,
    movie_data: MovieUpdate,
    current_user: User = Depends(get_current_admin)
):
    """Update an existing movie."""
    movie = movie_service.update_movie(movie_id, movie_data)
    
    return success(
        data=movie,
        message="Movie updated successfully"
    )


@movies_router.delete("/{movie_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_movie(
    movie_id: int,
    current_user: User = Depends(get_current_admin)
):
    """Delete a movie by ID."""
    movie_service.delete_movie(movie_id)
    return None