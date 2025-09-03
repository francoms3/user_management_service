"""
User data models for the user management service.
"""
from datetime import datetime
from typing import Optional
from pydantic import BaseModel, EmailStr, Field, field_validator
import uuid


class UserBase(BaseModel):
    """Base user model with common fields."""
    
    email: EmailStr = Field(..., description="User's email address")
    first_name: str = Field(..., min_length=1, max_length=50, description="User's first name")
    last_name: str = Field(..., min_length=1, max_length=50, description="User's last name")
    is_active: bool = Field(default=True, description="Whether the user account is active")


class UserCreate(UserBase):
    """Model for creating a new user."""
    
    password: str = Field(..., min_length=8, description="User's password (min 8 characters)")
    
    @field_validator('password')
    @classmethod
    def validate_password(cls, v):
        """Validate password strength."""
        if len(v) < 8:
            raise ValueError('Password must be at least 8 characters long')
        if not any(c.isupper() for c in v):
            raise ValueError('Password must contain at least one uppercase letter')
        if not any(c.islower() for c in v):
            raise ValueError('Password must contain at least one lowercase letter')
        if not any(c.isdigit() for c in v):
            raise ValueError('Password must contain at least one digit')
        return v


class UserUpdate(BaseModel):
    """Model for updating an existing user."""
    
    email: Optional[EmailStr] = Field(None, description="User's email address")
    first_name: Optional[str] = Field(None, min_length=1, max_length=50, description="User's first name")
    last_name: Optional[str] = Field(None, min_length=1, max_length=50, description="User's last name")
    is_active: Optional[bool] = Field(None, description="Whether the user account is active")
    password: Optional[str] = Field(None, min_length=8, description="User's new password")
    
    @field_validator('password')
    @classmethod
    def validate_password(cls, v):
        """Validate password strength if provided."""
        if v is not None:
            if len(v) < 8:
                raise ValueError('Password must be at least 8 characters long')
            if not any(c.isupper() for c in v):
                raise ValueError('Password must contain at least one uppercase letter')
            if not any(c.islower() for c in v):
                raise ValueError('Password must contain at least one lowercase letter')
            if not any(c.isdigit() for c in v):
                raise ValueError('Password must contain at least one digit')
        return v


class User(UserBase):
    """Complete user model with all fields."""
    
    id: str = Field(..., description="Unique user identifier")
    created_at: datetime = Field(..., description="User creation timestamp")
    updated_at: datetime = Field(..., description="User last update timestamp")
    
    model_config = {
        "json_schema_extra": {
            "example": {
                "id": "550e8400-e29b-41d4-a716-446655440000",
                "email": "john.doe@example.com",
                "first_name": "John",
                "last_name": "Doe",
                "is_active": True,
                "created_at": "2023-01-01T00:00:00Z",
                "updated_at": "2023-01-01T00:00:00Z"
            }
        }
    }


class UserResponse(BaseModel):
    """User response model for API responses."""
    
    user: User
    message: str = "Success"


class UsersResponse(BaseModel):
    """Multiple users response model for API responses."""
    
    users: list[User]
    total: int
    message: str = "Success"


class EmailUpdateRequest(BaseModel):
    """Model for email update requests."""
    
    email: EmailStr = Field(..., description="New email address")
