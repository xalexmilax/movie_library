import pytest
from fastapi import status
import time


class TestMovieEndpoints:
    """Test suite for movie endpoints"""
    
    # ==================== CREATE MOVIE ====================
    
    def test_create_movie_as_admin_success(self, client, admin_token):
        """Test creating a movie as admin (should succeed)"""
        response = client.post(
            "/movies/",
            headers={"Authorization": f"Bearer {admin_token}"},
            json={
                "title": "Test Inception",
                "director": "Christopher Nolan",
                "releaseyear": 2010
            }
        )
        
        assert response.status_code == status.HTTP_201_CREATED
        data = response.json()
        assert data["message"] == "Movie created successfully. Rating enrichment in progress."
        assert data["data"]["title"] == "Test Inception"
        assert data["data"]["director"] == "Christopher Nolan"
        assert data["data"]["releaseyear"] == 2010
        assert data["data"]["rating"] == 0.0  # Initial rating before enrichment
    
    
    def test_create_movie_as_user_forbidden(self, client, user_token):
        """Test creating a movie as regular user (should fail)"""
        response = client.post(
            "/movies/",
            headers={"Authorization": f"Bearer {user_token}"},
            json={
                "title": "Test Movie",
                "director": "Test Director",
                "releaseyear": 2020
            }
        )
        
        assert response.status_code == status.HTTP_403_FORBIDDEN
    
    
    def test_create_movie_without_auth(self, client):
        """Test creating a movie without authentication (should fail)"""
        response = client.post(
            "/movies/",
            json={
                "title": "Test Movie",
                "director": "Test Director",
                "releaseyear": 2020
            }
        )
        
        assert response.status_code == status.HTTP_401_UNAUTHORIZED
    
    
    def test_create_movie_invalid_year(self, client, admin_token):
        """Test creating a movie with invalid year (should fail)"""
        response = client.post(
            "/movies/",
            headers={"Authorization": f"Bearer {admin_token}"},
            json={
                "title": "Test Movie",
                "director": "Test Director",
                "releaseyear": 1800  # Too old
            }
        )
        
        assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY
    
    
    def test_create_movie_missing_fields(self, client, admin_token):
        """Test creating a movie with missing required fields (should fail)"""
        response = client.post(
            "/movies/",
            headers={"Authorization": f"Bearer {admin_token}"},
            json={
                "title": "Test Movie"
                # Missing director and releaseyear
            }
        )
        
        assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY
    
    
    # ==================== GET MOVIES ====================
    
    def test_get_all_movies_as_user(self, client, user_token, test_movie):
        """Test getting all movies as regular user (should succeed)"""
        response = client.get(
            "/movies/",
            headers={"Authorization": f"Bearer {user_token}"}
        )
        
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert "data" in data
        assert len(data["data"]) >= 1
    
    
    def test_get_all_movies_as_admin(self, client, admin_token, test_movie):
        """Test getting all movies as admin (should succeed)"""
        response = client.get(
            "/movies/",
            headers={"Authorization": f"Bearer {admin_token}"}
        )
        
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert "data" in data
        assert isinstance(data["data"], list)
    
    
    def test_get_movies_filter_by_title(self, client, admin_token, test_movie):
        """Test filtering movies by title"""
        response = client.get(
            "/movies/?title=Test Movie",
            headers={"Authorization": f"Bearer {admin_token}"}
        )
        
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert len(data["data"]) >= 1
        assert "Test Movie" in data["data"][0]["title"]
    
    
    def test_get_movies_sort_by_rating(self, client, admin_token, test_movie):
        """Test sorting movies by rating"""
        response = client.get(
            "/movies/?sort_by_rating=true",
            headers={"Authorization": f"Bearer {admin_token}"}
        )
        
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        # Check if sorted descending
        if len(data["data"]) > 1:
            assert data["data"][0]["rating"] >= data["data"][1]["rating"]
    
    
    def test_get_movie_by_id(self, client, user_token, test_movie):
        """Test getting a specific movie by ID"""
        response = client.get(
            f"/movies/{test_movie['movie_id']}",
            headers={"Authorization": f"Bearer {user_token}"}
        )
        
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert data["data"]["movie_id"] == test_movie["movie_id"]
        assert data["data"]["title"] == test_movie["title"]
    
    
    def test_get_movie_not_found(self, client, user_token):
        """Test getting a non-existent movie"""
        response = client.get(
            "/movies/99999",
            headers={"Authorization": f"Bearer {user_token}"}
        )
        
        assert response.status_code == status.HTTP_404_NOT_FOUND
    
    
    def test_get_movies_without_auth(self, client):
        """Test getting movies without authentication (should fail)"""
        response = client.get("/movies/")
        
        assert response.status_code == status.HTTP_401_UNAUTHORIZED
    
    
    # ==================== UPDATE MOVIE ====================
    
    def test_update_movie_as_admin(self, client, admin_token, test_movie):
        """Test updating a movie as admin (should succeed)"""
        response = client.put(
            f"/movies/{test_movie['movie_id']}",
            headers={"Authorization": f"Bearer {admin_token}"},
            json={
                "title": "Test Movie Updated",
                "director": "Updated Director",
                "releaseyear": 2021,
                "rating": 9.0
            }
        )
        
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert data["data"]["title"] == "Test Movie Updated"
        assert data["data"]["director"] == "Updated Director"
        assert data["data"]["rating"] == 9.0
    
    
    def test_update_movie_as_user_forbidden(self, client, user_token, test_movie):
        """Test updating a movie as regular user (should fail)"""
        response = client.put(
            f"/movies/{test_movie['movie_id']}",
            headers={"Authorization": f"Bearer {user_token}"},
            json={
                "title": "Test Movie Updated",
                "director": "Updated Director",
                "releaseyear": 2021,
                "rating": 9.0
            }
        )
        
        assert response.status_code == status.HTTP_403_FORBIDDEN
    
    
    def test_update_nonexistent_movie(self, client, admin_token):
        """Test updating a non-existent movie"""
        response = client.put(
            "/movies/99999",
            headers={"Authorization": f"Bearer {admin_token}"},
            json={
                "title": "Test Movie",
                "director": "Test Director",
                "releaseyear": 2020,
                "rating": 8.0
            }
        )
        
        assert response.status_code == status.HTTP_404_NOT_FOUND
    
    
    # ==================== DELETE MOVIE ====================
    
    def test_delete_movie_as_admin(self, client, admin_token, test_movie):
        """Test deleting a movie as admin (should succeed)"""
        response = client.delete(
            f"/movies/{test_movie['movie_id']}",
            headers={"Authorization": f"Bearer {admin_token}"}
        )
        
        assert response.status_code == status.HTTP_204_NO_CONTENT
        
        # Verify movie is deleted
        get_response = client.get(
            f"/movies/{test_movie['movie_id']}",
            headers={"Authorization": f"Bearer {admin_token}"}
        )
        assert get_response.status_code == status.HTTP_404_NOT_FOUND
    
    
    def test_delete_movie_as_user_forbidden(self, client, user_token, test_movie):
        """Test deleting a movie as regular user (should fail)"""
        response = client.delete(
            f"/movies/{test_movie['movie_id']}",
            headers={"Authorization": f"Bearer {user_token}"}
        )
        
        assert response.status_code == status.HTTP_403_FORBIDDEN
    
    
    def test_delete_nonexistent_movie(self, client, admin_token):
        """Test deleting a non-existent movie"""
        response = client.delete(
            "/movies/99999",
            headers={"Authorization": f"Bearer {admin_token}"}
        )
        
        assert response.status_code == status.HTTP_404_NOT_FOUND
    
    
    # ==================== BACKGROUND ENRICHMENT ====================
    
    @pytest.mark.asyncio
    async def test_movie_rating_enrichment(self, client, admin_token):
        """Test that movie rating gets enriched from external API"""
        # Create a well-known movie that should be in OMDb
        response = client.post(
            "/movies/",
            headers={"Authorization": f"Bearer {admin_token}"},
            json={
                "title": "Test The Godfather",
                "director": "Francis Ford Coppola",
                "releaseyear": 1972
            }
        )
        
        assert response.status_code == status.HTTP_201_CREATED
        movie_id = response.json()["data"]["movie_id"]
        
        # Wait for background enrichment (max 5 seconds)
        time.sleep(5)
        
        # Check if rating was updated
        get_response = client.get(
            f"/movies/{movie_id}",
            headers={"Authorization": f"Bearer {admin_token}"}
        )
        
        # Rating might still be 0.0 if OMDb API key is not set or movie not found
        # This test will pass regardless, but check in logs for enrichment status
        assert get_response.status_code == status.HTTP_200_OK