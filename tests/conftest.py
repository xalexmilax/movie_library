import pytest
from fastapi.testclient import TestClient
from main import app
from data.database import read_query, insert_query, delete_query
from common.security import hash_password
import os
from dotenv import load_dotenv

load_dotenv()

# Test client
@pytest.fixture
def client():
    """FastAPI test client"""
    return TestClient(app)


# Database fixtures
@pytest.fixture(scope="function")
def clean_database():
    """Clean test data before and after each test"""
    # Clean before test
    _clean_test_data()
    yield
    # Clean after test
    _clean_test_data()


def _clean_test_data():
    """Remove all test data from database"""
    try:
        # Delete test movies
        delete_query("DELETE FROM movies WHERE title LIKE 'Test%'")
        # Delete test users
        delete_query("DELETE FROM users WHERE username LIKE 'test%'")
    except Exception as e:
        print(f"Error cleaning database: {e}")


# User fixtures
@pytest.fixture
def test_admin_user(clean_database):
    """Create a test admin user and return credentials"""
    hashed_pw = hash_password("adminpass123")
    
    user_id = insert_query(
        """
        INSERT INTO users (firstname, lastname, username, password, email)
        VALUES (?, ?, ?, ?, ?)
        """,
        ("Test", "Admin", "testadmin", hashed_pw, "testadmin@example.com")
    )
    
    return {
        "user_id": user_id,
        "username": "testadmin",  # IMPORTANT: Must be "testadmin" for admin check
        "password": "adminpass123",
        "firstname": "Test",
        "lastname": "Admin",
        "email": "testadmin@example.com"
    }


@pytest.fixture
def test_regular_user(clean_database):
    """Create a test regular user and return credentials"""
    hashed_pw = hash_password("userpass123")
    
    user_id = insert_query(
        """
        INSERT INTO users (firstname, lastname, username, password, email)
        VALUES (?, ?, ?, ?, ?)
        """,
        ("Test", "User", "testuser", hashed_pw, "testuser@example.com")
    )
    
    return {
        "user_id": user_id,
        "username": "testuser",
        "password": "userpass123",
        "firstname": "Test",
        "lastname": "User",
        "email": "testuser@example.com"
    }


@pytest.fixture
def admin_token(client, test_admin_user):
    """Get authentication token for admin user"""
    response = client.post(
        "/auth/login",
        data={
            "username": test_admin_user["username"],
            "password": test_admin_user["password"]
        }
    )
    
    if response.status_code != 200:
        print(f"Login failed: {response.json()}")
    
    assert response.status_code == 200, f"Admin login failed: {response.json()}"
    data = response.json()
    return data["data"]["access_token"]


@pytest.fixture
def user_token(client, test_regular_user):
    """Get authentication token for regular user"""
    response = client.post(
        "/auth/login",
        data={
            "username": test_regular_user["username"],
            "password": test_regular_user["password"]
        }
    )
    
    if response.status_code != 200:
        print(f"Login failed: {response.json()}")
    
    assert response.status_code == 200, f"User login failed: {response.json()}"
    data = response.json()
    return data["data"]["access_token"]


@pytest.fixture
def test_movie(clean_database):
    """Create a test movie in database"""
    movie_id = insert_query(
        """
        INSERT INTO movies (title, director, releaseyear, rating)
        VALUES (?, ?, ?, ?)
        """,
        ("Test Movie 1", "Test Director", 2020, 8.5)
    )
    
    return {
        "movie_id": movie_id,
        "title": "Test Movie 1",
        "director": "Test Director",
        "releaseyear": 2020,
        "rating": 8.5
    }