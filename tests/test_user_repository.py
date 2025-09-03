"""
Unit tests for the user repository.
"""
import pytest
import threading
import time
from concurrent.futures import ThreadPoolExecutor, as_completed

from app.repositories.user_repository import UserRepository
from app.models.user import UserCreate, UserUpdate
from app.core.exceptions import UserNotFoundException, UserAlreadyExistsError


class TestUserRepository:
    """Test cases for UserRepository."""
    
    def test_create_user_success(self, user_repository):
        """Test successful user creation."""
        user_data = UserCreate(
            email="test@example.com",
            first_name="John",
            last_name="Doe",
            password="SecurePass123",
            is_active=True
        )
        
        user = user_repository.create_user(user_data)
        
        assert user.email == user_data.email
        assert user.first_name == user_data.first_name
        assert user.last_name == user_data.last_name
        assert user.is_active == user_data.is_active
        assert user.id is not None
        assert user.created_at is not None
        assert user.updated_at is not None
    
    def test_create_user_duplicate_email(self, user_repository):
        """Test user creation with duplicate email."""
        user_data = UserCreate(
            email="test@example.com",
            first_name="John",
            last_name="Doe",
            password="SecurePass123",
            is_active=True
        )
        
        # Create first user
        user_repository.create_user(user_data)
        
        # Try to create second user with same email
        with pytest.raises(UserAlreadyExistsError):
            user_repository.create_user(user_data)
    
    def test_get_user_by_id_success(self, user_repository):
        """Test successful user retrieval by ID."""
        user_data = UserCreate(
            email="test@example.com",
            first_name="John",
            last_name="Doe",
            password="SecurePass123",
            is_active=True
        )
        
        created_user = user_repository.create_user(user_data)
        retrieved_user = user_repository.get_user_by_id(created_user.id)
        
        assert retrieved_user.id == created_user.id
        assert retrieved_user.email == created_user.email
    
    def test_get_user_by_email_success(self, user_repository):
        """Test successful user retrieval by email."""
        user_data = UserCreate(
            email="test@example.com",
            first_name="John",
            last_name="Doe",
            password="SecurePass123",
            is_active=True
        )
        
        created_user = user_repository.create_user(user_data)
        retrieved_user = user_repository.get_user_by_email(user_data.email)
        
        assert retrieved_user.id == created_user.id
        assert retrieved_user.email == created_user.email
    
    def test_update_user_success(self, user_repository):
        """Test successful user update."""
        user_data = UserCreate(
            email="test@example.com",
            first_name="John",
            last_name="Doe",
            password="SecurePass123",
            is_active=True
        )
        
        created_user = user_repository.create_user(user_data)
        
        update_data = UserUpdate(
            first_name="Jane",
            last_name="Smith",
            is_active=False
        )
        
        updated_user = user_repository.update_user(created_user.id, update_data)
        
        assert updated_user.first_name == "Jane"
        assert updated_user.last_name == "Smith"
        assert updated_user.is_active == False
        assert updated_user.email == created_user.email  # Should remain unchanged
        # Allow for microsecond precision issues
        assert updated_user.updated_at >= created_user.updated_at
    
    def test_delete_user_success(self, user_repository):
        """Test successful user deletion."""
        user_data = UserCreate(
            email="test@example.com",
            first_name="John",
            last_name="Doe",
            password="SecurePass123",
            is_active=True
        )
        
        created_user = user_repository.create_user(user_data)
        
        result = user_repository.delete_user(created_user.id)
        
        assert result == True


class TestUserRepositoryThreadSafety:
    """Test cases for thread safety of UserRepository."""
    
    def test_concurrent_user_creation(self, user_repository):
        """Test basic thread safety with concurrent user creation."""
        def create_user(email_suffix):
            user_data = UserCreate(
                email=f"user{email_suffix}@example.com",
                first_name=f"User{email_suffix}",
                last_name="Test",
                password="SecurePass123",
                is_active=True
            )
            return user_repository.create_user(user_data)
        
        # Create users concurrently
        with ThreadPoolExecutor(max_workers=5) as executor:
            futures = [executor.submit(create_user, i) for i in range(5)]
            users = [future.result() for future in as_completed(futures)]
        
        # Verify all users were created
        assert len(users) == 5
        assert user_repository.get_user_count() == 5
        
        # Verify all emails are unique
        emails = [user.email for user in users]
        assert len(set(emails)) == 5
