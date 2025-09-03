"""
Custom exceptions for the user management service.
"""


class UserManagementException(Exception):
    """Base exception for user management service."""
    pass


class UserNotFoundException(UserManagementException):
    """Raised when a user is not found."""
    pass


class UserAlreadyExistsError(UserManagementException):
    """Raised when trying to create a user that already exists."""
    pass


class InvalidUserDataError(UserManagementException):
    """Raised when user data is invalid."""
    pass


class DatabaseError(UserManagementException):
    """Raised when database operations fail."""
    pass


class ValidationError(UserManagementException):
    """Raised when data validation fails."""
    pass


class ConcurrencyError(UserManagementException):
    """Raised when concurrent operations conflict."""
    pass
