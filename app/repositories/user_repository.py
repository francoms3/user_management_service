"""
Thread-safe user repository with in-memory storage.
"""
import threading
import uuid
from datetime import datetime, timezone
from typing import Dict, List, Optional
from passlib.context import CryptContext

from app.models.user import User, UserCreate, UserUpdate
from app.core.exceptions import UserNotFoundException, UserAlreadyExistsError, DatabaseError
from app.core.logging import get_logger

logger = get_logger(__name__)

# Password hashing context
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


class UserRepository:
    """
    Thread-safe user repository with in-memory storage.
    
    This implementation uses proper locking mechanisms to ensure thread safety
    for concurrent operations on user data.
    """
    
    def __init__(self):
        """Initialize the repository with thread-safe storage."""
        self._users: Dict[str, User] = {}
        self._email_index: Dict[str, str] = {}  # email -> user_id mapping
        self._lock = threading.RLock()  # Reentrant lock for nested operations
        self._logger = logger
    
    def _hash_password(self, password: str) -> str:
        """Hash a password using bcrypt."""
        return pwd_context.hash(password)
    
    def _verify_password(self, plain_password: str, hashed_password: str) -> bool:
        """Verify a password against its hash."""
        return pwd_context.verify(plain_password, hashed_password)
    
    def create_user(self, user_data: UserCreate) -> User:
        """
        Create a new user with thread-safe operations.
        
        Args:
            user_data: User creation data
            
        Returns:
            Created user object
            
        Raises:
            UserAlreadyExistsError: If user with email already exists
            DatabaseError: If database operation fails
        """
        with self._lock:
            try:
                # Check if user with email already exists
                if user_data.email in self._email_index:
                    raise UserAlreadyExistsError(f"User with email {user_data.email} already exists")
                
                # Generate unique ID and timestamps
                user_id = str(uuid.uuid4())
                now = datetime.now(timezone.utc)
                
                # Create user object
                user = User(
                    id=user_id,
                    email=user_data.email,
                    first_name=user_data.first_name,
                    last_name=user_data.last_name,
                    is_active=user_data.is_active,
                    created_at=now,
                    updated_at=now
                )
                
                # Store user data (password is hashed separately for security)
                self._users[user_id] = user
                self._email_index[user_data.email] = user_id
                
                return user
                
            except Exception as e:
                self._logger.error("Failed to create user", error=str(e), email=user_data.email)
                if isinstance(e, UserAlreadyExistsError):
                    raise
                raise DatabaseError(f"Failed to create user: {str(e)}")
    
    def get_user_by_id(self, user_id: str) -> User:
        """
        Get user by ID with thread-safe read operation.
        
        Args:
            user_id: User's unique identifier
            
        Returns:
            User object
            
        Raises:
            UserNotFoundError: If user is not found
        """
        with self._lock:
            if user_id not in self._users:
                raise UserNotFoundException(f"User with ID {user_id} not found")
            
            return self._users[user_id]
    
    def get_user_by_email(self, email: str) -> User:
        """
        Get user by email with thread-safe read operation.
        
        Args:
            email: User's email address
            
        Returns:
            User object
            
        Raises:
            UserNotFoundError: If user is not found
        """
        with self._lock:
            if email not in self._email_index:
                raise UserNotFoundException(f"User with email {email} not found")
            
            user_id = self._email_index[email]
            return self._users[user_id]
    
    def get_all_users(self) -> List[User]:
        """
        Get all users with thread-safe read operation.
        
        Returns:
            List of all users
        """
        with self._lock:
            return list(self._users.values())
    
    def update_user(self, user_id: str, user_data: UserUpdate) -> User:
        """
        Update user with thread-safe operations.
        
        Args:
            user_id: User's unique identifier
            user_data: User update data
            
        Returns:
            Updated user object
            
        Raises:
            UserNotFoundError: If user is not found
            UserAlreadyExistsError: If email is being changed to one that already exists
            DatabaseError: If database operation fails
        """
        with self._lock:
            try:
                if user_id not in self._users:
                    raise UserNotFoundException(f"User with ID {user_id} not found")
                
                user = self._users[user_id]
                update_data = user_data.model_dump(exclude_unset=True)
                
                # Check if email is being changed and if it already exists
                if 'email' in update_data and update_data['email'] != user.email:
                    if update_data['email'] in self._email_index:
                        raise UserAlreadyExistsError(f"User with email {update_data['email']} already exists")
                    
                    # Remove old email from index
                    del self._email_index[user.email]
                    # Add new email to index
                    self._email_index[update_data['email']] = user_id
                
                # Update user fields
                for field, value in update_data.items():
                    setattr(user, field, value)
                
                # Update timestamp
                user.updated_at = datetime.now(timezone.utc)
                
                return user
                
            except Exception as e:
                self._logger.error("Failed to update user", error=str(e), user_id=user_id)
                if isinstance(e, (UserNotFoundException, UserAlreadyExistsError)):
                    raise
                raise DatabaseError(f"Failed to update user: {str(e)}")
    
    def delete_user(self, user_id: str) -> bool:
        """
        Delete user with thread-safe operations.
        
        Args:
            user_id: User's unique identifier
            
        Returns:
            True if user was deleted, False otherwise
            
        Raises:
            UserNotFoundError: If user is not found
            DatabaseError: If database operation fails
        """
        with self._lock:
            try:
                if user_id not in self._users:
                    raise UserNotFoundException(f"User with ID {user_id} not found")
                
                user = self._users[user_id]
                
                # Remove from storage
                del self._users[user_id]
                del self._email_index[user.email]
                
                return True
                
            except Exception as e:
                self._logger.error("Failed to delete user", error=str(e), user_id=user_id)
                if isinstance(e, UserNotFoundException):
                    raise
                raise DatabaseError(f"Failed to delete user: {str(e)}")
    
    def get_user_count(self) -> int:
        """
        Get total number of users with thread-safe read operation.
        
        Returns:
            Total number of users
        """
        with self._lock:
            return len(self._users)