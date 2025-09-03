"""
User service
"""
from typing import List, Optional
from app.models.user import User, UserCreate, UserUpdate, UsersResponse
from app.repositories.user_repository import UserRepository
from app.core.exceptions import (
    UserNotFoundException,
    UserAlreadyExistsError, 
    InvalidUserDataError,
    ValidationError
)
from app.core.logging import get_logger

logger = get_logger(__name__)


class UserService:
    """
    User service with business logic and validation.
    
    This service layer encapsulates business rules and provides
    a clean interface for user management operations.
    """
    
    def __init__(self, user_repository: UserRepository):
        """
        Initialize the user service.
        
        Args:
            user_repository: Repository for data access operations
        """
        self._repository = user_repository
        self._logger = logger
    
    def create_user(self, user_data: UserCreate) -> User:
        """
        Create a new user with business logic validation.
        
        Args:
            user_data: User creation data
            
        Returns:
            Created user object
            
        Raises:
            UserAlreadyExistsError: If user with email already exists
            InvalidUserDataError: If user data is invalid
            ValidationError: If validation fails
        """
        try:
            self._logger.info("Creating user", email=user_data.email)
            
            # Additional business logic validation
            self._validate_user_creation(user_data)
            
            # Create user through repository
            user = self._repository.create_user(user_data)
            return user
            
        except (UserAlreadyExistsError, InvalidUserDataError, ValidationError):
            raise
        except Exception as e:
            self._logger.error("Unexpected error creating user", error=str(e), email=user_data.email)
            raise InvalidUserDataError(f"Failed to create user: {str(e)}")
    
    def get_user_by_id(self, user_id: str) -> User:
        """
        Get user by ID with business logic validation.
        
        Args:
            user_id: User's unique identifier
            
        Returns:
            User object
            
        Raises:
            UserNotFoundError: If user is not found
            InvalidUserDataError: If user ID is invalid
        """
        try:
            self._validate_user_id(user_id)
            
            user = self._repository.get_user_by_id(user_id)
            return user
            
        except UserNotFoundException:
            raise
        except Exception as e:
            self._logger.error("Unexpected error retrieving user", error=str(e), user_id=user_id)
            raise InvalidUserDataError(f"Failed to retrieve user: {str(e)}")
    
    def get_user_by_email(self, email: str) -> User:
        """
        Get user by email with business logic validation.
        
        Args:
            email: User's email address
            
        Returns:
            User object
            
        Raises:
            UserNotFoundError: If user is not found
            InvalidUserDataError: If email is invalid
        """
        try:
            self._validate_email(email)
            
            user = self._repository.get_user_by_email(email)
            return user
            
        except UserNotFoundException:
            raise
        except Exception as e:
            self._logger.error("Unexpected error retrieving user by email", error=str(e), email=email)
            raise InvalidUserDataError(f"Failed to retrieve user by email: {str(e)}")
    
    def get_all_users(self) -> UsersResponse:
        """
        Get all users with business logic processing.
        
        Returns:
            UsersResponse with list of users and total count
        """
        try:
            users = self._repository.get_all_users()
            total = self._repository.get_user_count()
            return UsersResponse(users=users, total=total)
            
        except Exception as e:
            self._logger.error("Unexpected error retrieving all users", error=str(e))
            raise InvalidUserDataError(f"Failed to retrieve users: {str(e)}")
    
    def update_user(self, user_id: str, user_data: UserUpdate) -> User:
        """
        Update user with business logic validation.
        
        Args:
            user_id: User's unique identifier
            user_data: User update data
            
        Returns:
            Updated user object
            
        Raises:
            UserNotFoundError: If user is not found
            UserAlreadyExistsError: If email is being changed to one that already exists
            InvalidUserDataError: If user data is invalid
            ValidationError: If validation fails
        """
        try:
            self._validate_user_id(user_id)
            self._validate_user_update(user_data)
            
            user = self._repository.update_user(user_id, user_data)
            return user
            
        except (UserNotFoundException, UserAlreadyExistsError, ValidationError):
            raise
        except Exception as e:
            self._logger.error("Unexpected error updating user", error=str(e), user_id=user_id)
            raise InvalidUserDataError(f"Failed to update user: {str(e)}")
    
    def delete_user(self, user_id: str) -> bool:
        """
        Delete user with business logic validation.
        
        Args:
            user_id: User's unique identifier
            
        Returns:
            True if user was deleted
            
        Raises:
            UserNotFoundError: If user is not found
            InvalidUserDataError: If user ID is invalid
        """
        try:
            self._validate_user_id(user_id)
            
            # Additional business logic: check if user is active before deletion
            user = self._repository.get_user_by_id(user_id)
            if not user.is_active:
                self._logger.warning("Attempting to delete inactive user", user_id=user_id)
            
            result = self._repository.delete_user(user_id)
            return result
            
        except UserNotFoundException:
            raise
        except Exception as e:
            self._logger.error("Unexpected error deleting user", error=str(e), user_id=user_id)
            raise InvalidUserDataError(f"Failed to delete user: {str(e)}")

    
    def _validate_user_creation(self, user_data: UserCreate) -> None:
        """
        Validate user creation data.
        
        Args:
            user_data: User creation data
            
        Raises:
            ValidationError: If validation fails
        """
        if not user_data.email or '@' not in user_data.email:
            raise ValidationError("Invalid email address")
        
        if not user_data.first_name or len(user_data.first_name.strip()) == 0:
            raise ValidationError("First name is required")
        
        if not user_data.last_name or len(user_data.last_name.strip()) == 0:
            raise ValidationError("Last name is required")
        
        if len(user_data.password) < 8:
            raise ValidationError("Password must be at least 8 characters long")
    
    def _validate_user_update(self, user_data: UserUpdate) -> None:
        """
        Validate user update data.
        
        Args:
            user_data: User update data
            
        Raises:
            ValidationError: If validation fails
        """
        if user_data.email is not None and ('@' not in user_data.email):
            raise ValidationError("Invalid email address")
        
        if user_data.first_name is not None and len(user_data.first_name.strip()) == 0:
            raise ValidationError("First name cannot be empty")
        
        if user_data.last_name is not None and len(user_data.last_name.strip()) == 0:
            raise ValidationError("Last name cannot be empty")
        
        if user_data.password is not None and len(user_data.password) < 8:
            raise ValidationError("Password must be at least 8 characters long")
    
    def _validate_user_id(self, user_id: str) -> None:
        """
        Validate user ID format.
        
        Args:
            user_id: User's unique identifier
            
        Raises:
            ValidationError: If user ID is invalid
        """
        if not user_id or len(user_id.strip()) == 0:
            raise ValidationError("User ID is required")
        
        # Basic UUID validation (simplified)
        if len(user_id) != 36:  # UUID v4 length
            raise ValidationError("Invalid user ID format")
    
    def _validate_email(self, email: str) -> None:
        """
        Validate email format.
        
        Args:
            email: Email address
            
        Raises:
            ValidationError: If email is invalid
        """
        if not email or '@' not in email:
            raise ValidationError("Invalid email address")
