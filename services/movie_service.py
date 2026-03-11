from data.database import read_query, insert_query, update_query, delete_query
from data.models import MovieCreate, MovieUpdate, MovieResponse
from common.exceptions import NotFoundError
from typing import Optional
import httpx
import asyncio
import os
from dotenv import load_dotenv

load_dotenv()

# External API configuration (using OMDb API)
OMDB_API_KEY = os.getenv("OMDB_API_KEY")
OMDB_BASE_URL = "http://www.omdbapi.com/"


# ==================== INTERNAL HELPERS ====================

def _row_to_movie(row) -> MovieResponse:
    """Convert database row to MovieResponse model."""
    movie_id, title, director, release_year, rating = row
    
    return MovieResponse(
        movie_id=movie_id,
        title=title,
        director=director,
        release_year=release_year,
        rating=rating if rating is not None else 0.0
    )


def _get_movie_by_id_internal(movie_id: int) -> MovieResponse | None:
    """Internal method to get movie by ID without raising exceptions."""
    rows = read_query(
        """
        SELECT movie_id, title, director, release_year, rating
        FROM movies
        WHERE movie_id = ?
        """,
        (movie_id,)
    )
    
    if not rows:
        return None
    
    return _row_to_movie(rows[0])


# ==================== ASYNC BACKGROUND ENRICHMENT ====================

async def enrich_movie_rating(movie_id: int, title: str):
    """
    Background task to fetch rating from external API and update the movie.
    This runs asynchronously and does not block the create endpoint.
    """
    try:
        # Fetch rating from external API
        rating = await _fetch_rating_from_omdb(title)
        
        if rating is not None:
            # Update the movie with the fetched rating
            update_query(
                "UPDATE movies SET rating = ? WHERE movie_id = ?",
                (rating, movie_id)
            )
            print(f"✅ Successfully enriched movie {movie_id} '{title}' with rating: {rating}")
        else:
            print(f"⚠️  No rating found for movie: {title}")
            
    except Exception as e:
        print(f"❌ Error enriching movie {movie_id}: {e}")


async def _fetch_rating_from_omdb(title: str) -> Optional[float]:
    """
    Fetch movie rating from OMDb API.
    Returns IMDb rating as float or None if not found.
    """
    if not OMDB_API_KEY:
        print("⚠️  OMDB_API_KEY not set in .env file")
        return None
    
    try:
        async with httpx.AsyncClient() as client:
            response = await client.get(
                OMDB_BASE_URL,
                params={
                    "apikey": OMDB_API_KEY,
                    "t": title,  # Search by title
                    "type": "movie"
                },
                timeout=10.0
            )
            
            if response.status_code == 200:
                data = response.json()
                
                # Check if movie was found
                if data.get("Response") == "True":
                    imdb_rating = data.get("imdbRating")
                    
                    # Convert to float if valid
                    if imdb_rating and imdb_rating != "N/A":
                        return float(imdb_rating)
                
                print(f"⚠️  Movie not found in OMDb: {title}")
                return None
            else:
                print(f"❌ OMDb API error: {response.status_code}")
                return None
                
    except Exception as e:
        print(f"❌ Error fetching from OMDb: {e}")
        return None


# ==================== PUBLIC SERVICE METHODS ====================

def create_movie(movie_data: MovieCreate) -> MovieResponse:
    """
    Create a new movie in the database.
    Immediately returns the created movie and starts background enrichment.
    """
    # Insert movie with initial rating (0.0)
    movie_id = insert_query(
        """
        INSERT INTO movies (title, director, release_year, rating)
        VALUES (?, ?, ?, ?)
        """,
        (
            movie_data.title,
            movie_data.director,
            movie_data.release_year,
            0.0  # Initial rating, will be enriched in background
        )
    )
    
    # Start background enrichment (non-blocking)
    asyncio.create_task(enrich_movie_rating(movie_id, movie_data.title))
    
    # Return the created movie immediately
    movie = _get_movie_by_id_internal(movie_id)
    
    if not movie:
        raise NotFoundError("Failed to retrieve created movie")
    
    return movie


def get_movie_by_id(movie_id: int) -> MovieResponse:
    """Get a specific movie by ID."""
    movie = _get_movie_by_id_internal(movie_id)
    
    if not movie:
        raise NotFoundError(f"Movie with ID {movie_id} not found")
    
    return movie


def get_all_movies(
    title_filter: Optional[str] = None,
    sort_by_rating: bool = False
) -> list[MovieResponse]:
    """
    Get all movies with optional filtering and sorting.
    
    Args:
        title_filter: Filter movies by title (case-insensitive partial match)
        sort_by_rating: If True, sort by rating descending
    """
    query = """
        SELECT movie_id, title, director, release_year, rating
        FROM movies
        WHERE 1=1
    """
    params = []
    
    # Add title filter if provided
    if title_filter:
        query += " AND title LIKE ?"
        params.append(f"%{title_filter}%")
    
    # Add sorting
    if sort_by_rating:
        query += " ORDER BY rating DESC"
    else:
        query += " ORDER BY title ASC"
    
    rows = read_query(query, tuple(params))
    
    return [_row_to_movie(row) for row in rows]


def update_movie(movie_id: int, movie_data: MovieUpdate) -> MovieResponse:
    """Update an existing movie."""
    # Check if movie exists
    existing_movie = _get_movie_by_id_internal(movie_id)
    
    if not existing_movie:
        raise NotFoundError(f"Movie with ID {movie_id} not found")
    
    # Update movie
    update_query(
        """
        UPDATE movies
        SET title = ?, director = ?, release_year = ?, rating = ?
        WHERE movie_id = ?
        """,
        (
            movie_data.title,
            movie_data.director,
            movie_data.release_year,
            movie_data.rating,
            movie_id
        )
    )
    
    # Return updated movie
    updated_movie = _get_movie_by_id_internal(movie_id)
    
    if not updated_movie:
        raise NotFoundError("Failed to retrieve updated movie")
    
    return updated_movie


def delete_movie(movie_id: int) -> None:
    """Delete a movie by ID."""
    # Check if movie exists
    existing_movie = _get_movie_by_id_internal(movie_id)
    
    if not existing_movie:
        raise NotFoundError(f"Movie with ID {movie_id} not found")
    
    # Delete movie
    delete_query("DELETE FROM movies WHERE movie_id = ?", (movie_id,))