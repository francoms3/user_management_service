"""
Unit tests for the user service.
"""
import pytest
from datetime import datetime

from app.models.user import UserCreate, UserUpdate
from app.services.user_service import UserService
from app.core.exceptions import (
    UserNotFoundException,
    UserAlreadyExistsError,
    InvalidUserDataError,
    ValidationError
)


class TestUserService:
    """Test cases for UserService."""
    
    def test_create_user_success(self, user_service):
        """Test successful user creation."""
        user_data = UserCreate(
            email="test@example.com",
            first_name="John",
            last_name="Doe",
            password="SecurePass123"
        )
        
        user = user_service.create_user(user_data)
        
        assert user.email == "test@example.com"
        assert user.first_name == "John"
        assert user.last_name == "Doe"
        assert user.is_active == True
        assert user.created_at is not None
        assert user.updated_at is not None
    
    def test_create_user_duplicate_email(self, user_service):
        """Test user creation with duplicate email."""
        user_data1 = UserCreate(
            email="test@example.com",
            first_name="John",
            last_name="Doe",
            password="SecurePass123"
        )
        
        user_data2 = UserCreate(
            email="test@example.com",
            first_name="Jane",
            last_name="Smith",
            password="SecurePass456"
        )
        
        # Create first user
        user_service.create_user(user_data1)
        
        # Try to create second user with same email
        with pytest.raises(UserAlreadyExistsError):
            user_service.create_user(user_data2)
    
    def test_get_user_by_id_success(self, user_service, sample_user):
        """Test successful user retrieval by ID."""
        retrieved_user = user_service.get_user_by_id(sample_user.id)
        
        assert retrieved_user.id == sample_user.id
        assert retrieved_user.email == sample_user.email
        assert retrieved_user.first_name == sample_user.first_name
        assert retrieved_user.last_name == sample_user.last_name
    
    def test_get_user_by_email_success(self, user_service, sample_user):
        """Test successful user retrieval by email."""
        retrieved_user = user_service.get_user_by_email(sample_user.email)
        
        assert retrieved_user.id == sample_user.id
        assert retrieved_user.email == sample_user.email
    
    def test_get_all_users(self, user_service, multiple_users):
        """Test retrieval of all users."""
        result = user_service.get_all_users()
        
        assert result.total == 3
        assert len(result.users) == 3
    
    def test_update_user_success(self, user_service, sample_user):
        """Test successful user update."""
        update_data = UserUpdate(
            first_name="Jane",
            last_name="Smith",
            is_active=False
        )
        
        updated_user = user_service.update_user(sample_user.id, update_data)
        
        assert updated_user.first_name == "Jane"
        assert updated_user.last_name == "Smith"
        assert updated_user.is_active == False
        assert updated_user.email == sample_user.email  # Should remain unchanged
        # Allow for microsecond precision issues
        assert updated_user.updated_at >= sample_user.updated_at
    
    def test_update_user_email_change(self, user_service, sample_user):
        """Test user update with email change."""
        update_data = UserUpdate(email="newemail@example.com")
        
        updated_user = user_service.update_user(sample_user.id, update_data)
        
        assert updated_user.email == "newemail@example.com"
    
    def test_delete_user_success(self, user_service, sample_user):
        """Test successful user deletion."""
        result = user_service.delete_user(sample_user.id)
        
        assert result == True
