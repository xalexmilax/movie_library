import pytest
from fastapi import status


class TestAuthEndpoints:
    """Test suite for authentication endpoints"""
    
    # ==================== LOGIN ====================
    
    def test_login_success(self, client, test_admin_user):
        """Test successful login"""
        response = client.post(
            "/auth/login",
            data={
                "username": test_admin_user["username"],
                "password": test_admin_user["password"]
            }
        )
        
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert "data" in data
        assert "access_token" in data["data"]
        assert data["data"]["token_type"] == "bearer"
        assert data["data"]["username"] == test_admin_user["username"]
    
    
    def test_login_wrong_password(self, client, test_admin_user):
        """Test login with wrong password"""
        response = client.post(
            "/auth/login",
            data={
                "username": test_admin_user["username"],
                "password": "definitelywrongpassword12345"
            }
        )
        
        assert response.status_code == status.HTTP_401_UNAUTHORIZED
    
    
    def test_login_nonexistent_user(self, client, clean_database):
        """Test login with non-existent username"""
        response = client.post(
            "/auth/login",
            data={
                "username": "user_that_absolutely_does_not_exist_999",
                "password": "somepassword"
            }
        )
        
        assert response.status_code == status.HTTP_401_UNAUTHORIZED
    
    
    def test_login_missing_credentials(self, client):
        """Test login with missing credentials"""
        response = client.post("/auth/login", data={})
        
        assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY
    
    
    # ==================== TOKEN VALIDATION ====================
    
    def test_access_protected_endpoint_with_valid_token(self, client, admin_token):
        """Test accessing protected endpoint with valid token"""
        response = client.get(
            "/movies/",
            headers={"Authorization": f"Bearer {admin_token}"}
        )
        
        assert response.status_code == status.HTTP_200_OK
    
    
    def test_access_protected_endpoint_with_invalid_token(self, client):
        """Test accessing protected endpoint with invalid token"""
        response = client.get(
            "/movies/",
            headers={"Authorization": "Bearer invalid_token_here_12345"}
        )
        
        assert response.status_code == status.HTTP_401_UNAUTHORIZED
    
    
    def test_access_protected_endpoint_without_token(self, client):
        """Test accessing protected endpoint without token"""
        response = client.get("/movies/")
        
        assert response.status_code == status.HTTP_401_UNAUTHORIZED
    
    
    # ==================== AUTHORIZATION ====================
    
    def test_admin_can_create_movie(self, client, admin_token):
        """Test that admin can create movies"""
        response = client.post(
            "/movies/",
            headers={"Authorization": f"Bearer {admin_token}"},
            json={
                "title": "Test Admin Movie",
                "director": "Test Director",
                "release_year": 2020
            }
        )
        
        assert response.status_code == status.HTTP_201_CREATED
    
    
    def test_user_cannot_create_movie(self, client, user_token):
        """Test that regular user cannot create movies"""
        response = client.post(
            "/movies/",
            headers={"Authorization": f"Bearer {user_token}"},
            json={
                "title": "Test User Movie",
                "director": "Test Director",
                "release_year": 2020
            }
        )
        
        assert response.status_code == status.HTTP_403_FORBIDDEN
    
    
    def test_user_can_read_movies(self, client, user_token, test_movie):
        """Test that regular user can read movies"""
        response = client.get(
            "/movies/",
            headers={"Authorization": f"Bearer {user_token}"}
        )
        
        assert response.status_code == status.HTTP_200_OK
    
    
    def test_admin_can_delete_movie(self, client, admin_token, test_movie):
        """Test that admin can delete movies"""
        response = client.delete(
            f"/movies/{test_movie['movie_id']}",
            headers={"Authorization": f"Bearer {admin_token}"}
        )
        
        assert response.status_code == status.HTTP_204_NO_CONTENT
    
    
    def test_user_cannot_delete_movie(self, client, user_token, test_movie):
        """Test that regular user cannot delete movies"""
        response = client.delete(
            f"/movies/{test_movie['movie_id']}",
            headers={"Authorization": f"Bearer {user_token}"}
        )
        
        assert response.status_code == status.HTTP_403_FORBIDDEN


class TestUserModel:
    """Test suite for User model and data handling"""
    
    def test_user_password_is_hashed(self, test_admin_user):
        """Test that user password is hashed in database"""
        from data.database import read_query
        
        rows = read_query(
            "SELECT password FROM users WHERE username = ?",
            (test_admin_user["username"],)
        )
        
        assert len(rows) > 0
        hashed_password = rows[0][0]
        
        # Hashed password should not equal plain password
        assert hashed_password != test_admin_user["password"]
        # Hashed password should be longer
        assert len(hashed_password) > 50
    
    
    def test_user_data_retrieved_correctly(self, test_admin_user):
        """Test that user data is retrieved correctly from database"""
        from data.database import read_query
        
        rows = read_query(
            "SELECT idusers, firstname, lastname, username, email FROM users WHERE username = ?",
            (test_admin_user["username"],)
        )
        
        assert len(rows) > 0
        user_id, firstname, lastname, username, email = rows[0]
        
        assert firstname == test_admin_user["firstname"]
        assert lastname == test_admin_user["lastname"]
        assert username == test_admin_user["username"]
        assert email == test_admin_user["email"]