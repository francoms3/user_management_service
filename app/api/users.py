"""
RESTful API endpoints for user management.
"""
from typing import List
from fastapi import APIRouter, HTTPException, status, Depends
from fastapi.responses import JSONResponse

from app.models.user import User, UserCreate, UserUpdate, UserResponse, UsersResponse, EmailUpdateRequest
from app.services.user_service import UserService
from app.repositories.user_repository import UserRepository
from app.core.exceptions import (
    UserNotFoundException,
    UserAlreadyExistsError, 
    InvalidUserDataError,
    ValidationError
)
from app.core.logging import get_logger

logger = get_logger(__name__)

# Create router
router = APIRouter(prefix="/users", tags=["users"])


# Singleton instance of UserRepository
_user_repository = UserRepository()

def get_user_service() -> UserService:
    """
    Dependency injection for user service.
    
    Returns:
        UserService instance
    """
    return UserService(_user_repository)


@router.post("/", response_model=UserResponse, status_code=status.HTTP_201_CREATED)
async def create_user(
    user_data: UserCreate,
    user_service: UserService = Depends(get_user_service)
) -> UserResponse:
    """
    Create a new user.
    
    Args:
        user_data: User creation data
        user_service: User service dependency
        
    Returns:
        Created user response
        
    Raises:
        HTTPException: If user creation fails
    """
    try:
        logger.info("Creating user", email=user_data.email)
        
        user = user_service.create_user(user_data)
        return UserResponse(user=user, message="User created successfully")
        
    except UserAlreadyExistsError as e:
        logger.warning("User creation failed - user already exists", email=user_data.email)
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=str(e)
        )
    except (InvalidUserDataError, ValidationError) as e:
        logger.warning("User creation failed - invalid data", email=user_data.email, error=str(e))
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )


@router.get("/", response_model=UsersResponse)
async def get_all_users(
    user_service: UserService = Depends(get_user_service)
) -> UsersResponse:
    """
    Get all users.
    
    Args:
        user_service: User service dependency
        
    Returns:
        List of all users with total count
    """
    result = user_service.get_all_users()
    return result


@router.get("/{user_id}", response_model=UserResponse)
async def get_user_by_id(
    user_id: str,
    user_service: UserService = Depends(get_user_service)
) -> UserResponse:
    """
    Get user by ID.
    
    Args:
        user_id: User's unique identifier
        user_service: User service dependency
        
    Returns:
        User response
        
    Raises:
        HTTPException: If user not found or retrieval fails
    """
    try:
        user = user_service.get_user_by_id(user_id)
        return UserResponse(user=user, message="User retrieved successfully")
        
    except UserNotFoundException as e:
        logger.warning("User not found", user_id=user_id)
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(e)
        )
    except InvalidUserDataError as e:
        logger.warning("Invalid user ID provided", user_id=user_id, error=str(e))
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )


@router.put("/{user_id}", response_model=UserResponse)
async def update_user(
    user_id: str,
    user_data: UserUpdate,
    user_service: UserService = Depends(get_user_service)
) -> UserResponse:
    """
    Update user by ID.
    
    Args:
        user_id: User's unique identifier
        user_data: User update data
        user_service: User service dependency
        
    Returns:
        Updated user response
        
    Raises:
        HTTPException: If user not found or update fails
    """
    try:
        user = user_service.update_user(user_id, user_data)
        return UserResponse(user=user, message="User updated successfully")
        
    except UserNotFoundException as e:
        logger.warning("User not found for update", user_id=user_id)
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(e)
        )
    except UserAlreadyExistsError as e:
        logger.warning("User update failed - email already exists", user_id=user_id)
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=str(e)
        )
    except (InvalidUserDataError, ValidationError) as e:
        logger.warning("User update failed - invalid data", user_id=user_id, error=str(e))
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )


@router.put("/{user_id}/email", response_model=UserResponse)
async def update_user_email(
    user_id: str,
    email_data: EmailUpdateRequest,
    user_service: UserService = Depends(get_user_service)
) -> UserResponse:
    """
    Update user email by ID.
    
    Args:
        user_id: User's unique identifier
        email_data: Email update request data
        user_service: User service dependency
        
    Returns:
        Updated user response
        
    Raises:
        HTTPException: If user not found or update fails
    """
    try:
        # Create UserUpdate object - FastAPI will handle validation
        update_data = UserUpdate(email=email_data.email)
        
        user = user_service.update_user(user_id, update_data)
        return UserResponse(user=user, message="User email updated successfully")
        
    except UserNotFoundException as e:
        logger.warning("User not found for email update", user_id=user_id)
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(e)
        )
    except UserAlreadyExistsError as e:
        logger.warning("User email update failed - email already exists", user_id=user_id)
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=str(e)
        )
    except (InvalidUserDataError, ValidationError) as e:
        logger.warning("User email update failed - invalid data", user_id=user_id, error=str(e))
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )


@router.delete("/{user_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_user(
    user_id: str,
    user_service: UserService = Depends(get_user_service)
) -> None:
    """
    Delete user by ID.
    
    Args:
        user_id: User's unique identifier
        user_service: User service dependency
        
    Raises:
        HTTPException: If user not found or deletion fails
    """
    try:
        user_service.delete_user(user_id)
        
    except UserNotFoundException as e:
        logger.warning("User not found for deletion", user_id=user_id)
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(e)
        )
    except InvalidUserDataError as e:
        logger.warning("Invalid user ID for deletion", user_id=user_id, error=str(e))
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
