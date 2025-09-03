"""
Pytest configuration and fixtures for the user management service.
"""
import pytest
from fastapi.testclient import TestClient
from app.main import app
from app.repositories.user_repository import UserRepository
from app.services.user_service import UserService
from app.models.user import UserCreate


@pytest.fixture
def client():
    """Test client for FastAPI."""
    return TestClient(app)


@pytest.fixture
def user_repository():
    """User repository instance for testing."""
    return UserRepository()


@pytest.fixture
def user_service(user_repository):
    """User service instance for testing."""
    return UserService(user_repository)


@pytest.fixture
def sample_user_data():
    """Sample user data for testing."""
    return UserCreate(
        email="test@example.com",
        first_name="John",
        last_name="Doe",
        password="SecurePass123",
        is_active=True
    )


@pytest.fixture
def sample_user(user_service, sample_user_data):
    """Sample user created in the service."""
    return user_service.create_user(sample_user_data)


@pytest.fixture
def multiple_users(user_service):
    """Multiple users for testing."""
    users = []
    user_data_list = [
        UserCreate(
            email="user1@example.com",
            first_name="Alice",
            last_name="Johnson",
            password="SecurePass123",
            is_active=True
        ),
        UserCreate(
            email="user2@example.com",
            first_name="Bob",
            last_name="Smith",
            password="SecurePass123",
            is_active=False
        ),
        UserCreate(
            email="user3@example.com",
            first_name="Charlie",
            last_name="Brown",
            password="SecurePass123",
            is_active=True
        )
    ]
    
    for user_data in user_data_list:
        user = user_service.create_user(user_data)
        users.append(user)
    
    return users
