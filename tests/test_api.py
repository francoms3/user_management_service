"""
Integration tests for the API endpoints.
"""
import pytest
from fastapi.testclient import TestClient
from app.main import app


class TestUserAPI:
    """Test cases for user API endpoints."""
    
    def test_create_user_success(self, client):
        """Test successful user creation via API."""
        user_data = {
            "email": "test@example.com",
            "first_name": "John",
            "last_name": "Doe",
            "password": "SecurePass123",
            "is_active": True
        }
        
        response = client.post("/users/", json=user_data)
        
        assert response.status_code == 201
        data = response.json()
        assert data["message"] == "User created successfully"
        assert data["user"]["email"] == user_data["email"]
        assert data["user"]["first_name"] == user_data["first_name"]
        assert data["user"]["last_name"] == user_data["last_name"]
        assert data["user"]["is_active"] == user_data["is_active"]
        assert data["user"]["id"] is not None
        assert data["user"]["created_at"] is not None
        assert data["user"]["updated_at"] is not None
    
    def test_create_user_duplicate_email(self, client):
        """Test user creation with duplicate email via API."""
        user_data = {
            "email": "duplicate@example.com",
            "first_name": "John",
            "last_name": "Doe",
            "password": "SecurePass123",
            "is_active": True
        }
        
        # Create first user
        response1 = client.post("/users/", json=user_data)
        assert response1.status_code == 201
        
        # Try to create second user with same email
        response2 = client.post("/users/", json=user_data)
        assert response2.status_code == 409
        assert "already exists" in response2.json()["detail"]
    
    def test_create_user_invalid_email(self, client):
        """Test user creation with invalid email via API."""
        user_data = {
            "email": "invalid-email",
            "first_name": "John",
            "last_name": "Doe",
            "password": "SecurePass123",
            "is_active": True
        }
        
        response = client.post("/users/", json=user_data)
        assert response.status_code == 422  # Validation error

    def test_get_user_by_id_success(self, client):
        """Test successful user retrieval by ID via API."""
        # Create a user first
        user_data = {
            "email": "getbyid@example.com",
            "first_name": "John",
            "last_name": "Doe",
            "password": "SecurePass123",
            "is_active": True
        }
        
        create_response = client.post("/users/", json=user_data)
        created_user = create_response.json()["user"]
        
        # Get user by ID
        response = client.get(f"/users/{created_user['id']}")
        
        assert response.status_code == 200
        data = response.json()
        assert data["message"] == "User retrieved successfully"
        assert data["user"]["id"] == created_user["id"]
        assert data["user"]["email"] == created_user["email"]
        assert data["user"]["first_name"] == created_user["first_name"]
        assert data["user"]["last_name"] == created_user["last_name"]
    
    def test_get_user_by_id_not_found(self, client):
        """Test user retrieval by non-existent ID via API."""
        # Use a valid UUID format that doesn't exist
        fake_uuid = "550e8400-e29b-41d4-a716-446655440000"
        response = client.get(f"/users/{fake_uuid}")
        
        assert response.status_code == 404
        assert "not found" in response.json()["detail"]
    
    def test_update_user_success(self, client):
        """Test successful user update via API."""
        # Create a user first
        user_data = {
            "email": "update@example.com",
            "first_name": "John",
            "last_name": "Doe",
            "password": "SecurePass123",
            "is_active": True
        }
        
        create_response = client.post("/users/", json=user_data)
        created_user = create_response.json()["user"]
        
        # Update user
        update_data = {
            "first_name": "Jane",
            "last_name": "Smith",
            "is_active": False
        }
        
        response = client.put(f"/users/{created_user['id']}", json=update_data)
        
        assert response.status_code == 200
        data = response.json()
        assert data["message"] == "User updated successfully"
        assert data["user"]["first_name"] == "Jane"
        assert data["user"]["last_name"] == "Smith"
        assert data["user"]["is_active"] == False
        assert data["user"]["email"] == created_user["email"]  # Should remain unchanged
    
    def test_update_user_email_change(self, client):
        """Test user update with email change via API."""
        # Create a user first
        user_data = {
            "email": "emailchange@example.com",
            "first_name": "John",
            "last_name": "Doe",
            "password": "SecurePass123",
            "is_active": True
        }
        
        create_response = client.post("/users/", json=user_data)
        created_user = create_response.json()["user"]
        
        # Update user email
        update_data = {"email": "newemail@example.com"}
        
        response = client.put(f"/users/{created_user['id']}", json=update_data)
        
        assert response.status_code == 200
        data = response.json()
        assert data["user"]["email"] == "newemail@example.com"
    
    def test_delete_user_success(self, client):
        """Test successful user deletion via API."""
        # Create a user first
        user_data = {
            "email": "delete@example.com",
            "first_name": "John",
            "last_name": "Doe",
            "password": "SecurePass123",
            "is_active": True
        }
        
        create_response = client.post("/users/", json=user_data)
        created_user = create_response.json()["user"]
        
        # Delete user
        response = client.delete(f"/users/{created_user['id']}")
        
        assert response.status_code == 204
        
        # Verify user is deleted
        get_response = client.get(f"/users/{created_user['id']}")
        assert get_response.status_code == 404


class TestHealthEndpoints:
    """Test cases for health and info endpoints."""
    
    def test_root_endpoint(self, client):
        """Test root endpoint."""
        response = client.get("/")
        
        assert response.status_code == 200
        data = response.json()
        assert data["message"] == "User Management Service"
        assert "version" in data
        assert data["status"] == "healthy"
        assert data["docs"] == "/docs"
    
    def test_health_check(self, client):
        """Test health check endpoint."""
        response = client.get("/health")
        
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "healthy"
        assert data["service"] == "User Management Service"
        assert "version" in data

