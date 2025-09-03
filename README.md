# User Management Backend Service

A high-availability backend service built with modern concurrency and testing practices, featuring thread-safe user management with robust error handling.

### ✅ Task 1: Custom Exception
- **UserNotFoundException**: Custom exception thrown when a user is not found for a given ID
- Implemented in `app/core/exceptions.py` and used throughout the application

### ✅ Task 2: Thread Safety
- **Thread-safe operations**: Uses `threading.RLock` for concurrent access
- **Concurrent maps**: Thread-safe in-memory storage with proper locking
- **Atomic operations**: Safe concurrent user creation, updates, and deletions

### ✅ Task 3: Unit Tests
- **Comprehensive test suite**: 100% coverage of all service methods
- **Positive and negative cases**: Tests for success scenarios and error conditions
- **Thread safety tests**: Concurrent operation testing
- **API integration tests**: End-to-end HTTP endpoint testing

### ✅ Task 4: Dependency Injection
- **Repository pattern**: Clean separation between business logic and data access
- **Service layer**: Business logic encapsulation with injectable dependencies
- **Extensible architecture**: Easy to swap in-memory storage for database

### ✅ Task 5: Web API Integration
- **FastAPI library**: Modern, fast web library for building APIs
- **HTTP server setup**: Complete server configuration in main entrypoint
- **Handler/controller module**: All routes defined in `app/api/users.py`
- **Required endpoints**:
  - `POST /users` - Create user
  - `GET /users/{id}` - Get user by ID
  - `PUT /users/{id}/email` - Update user email
  - `DELETE /users/{id}` - Delete user
- **Error handling**: Proper HTTP status codes and meaningful error messages
- **Input validation**: Comprehensive request validation with Pydantic

### ✅ Task 6: Docker Containerization
- **Dockerfile**: Production-ready container configuration
- **Single command execution**: `docker run` ready

## Setup and Installation

### Local Development

1. **Install dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

2. **Run the application**:
   ```bash
   uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
   ```

3. **Run tests**:
   ```bash
   pytest tests/ -v
   ```

### Docker Deployment

1. **Build the container**:
   ```bash
   docker build -t user-management-service .
   ```

2. **Run the container**:
   ```bash
   docker run -d --name user-management-service -p 8000:8000 user-management-service
   ```

3. **Check health**
   ```bash
   curl http://localhost:8000/health
   ```

4. **View logs**
   ```bash
   docker logs user-management-service
   ```

## API Documentation

Once the server is running, visit:
- **Interactive API docs**: http://localhost:8000/docs
- **ReDoc documentation**: http://localhost:8000/redoc

## API Endpoints

### Required Assessment Endpoints
- `POST /users` - Create new user
- `GET /users/{user_id}` - Get user by ID
- `PUT /users/{user_id}/email` - Update user email
- `DELETE /users/{user_id}` - Delete user

### Additional Endpoints
- `GET /users` - List all users
- `PUT /users/{user_id}` - Update user (full update)
- `GET /health` - Health check

## Example API Usage

### Create a User
```bash
curl -X POST "http://localhost:8000/users/" \
  -H "Content-Type: application/json" \
  -d '{
    "email": "john.doe@example.com",
    "first_name": "John",
    "last_name": "Doe",
    "password": "SecurePass123",
    "is_active": true
  }'
```

### Get User by ID
```bash
curl -X GET "http://localhost:8000/users/{user_id}"
```

### Update User Email
```bash
curl -X PUT "http://localhost:8000/users/{user_id}/email" \
  -H "Content-Type: application/json" \
  -d '{"email": "newemail@example.com"}'
```

### Delete User
```bash
curl -X DELETE "http://localhost:8000/users/{user_id}"
```

### Get All Users
```bash
curl -X GET "http://localhost:8000/users/"
```

## Project Structure

```
├── app/
│   ├── __init__.py
│   ├── main.py              # FastAPI application entry point
│   ├── models/              # Pydantic models
│   │   ├── __init__.py
│   │   └── user.py
│   ├── services/            # Business logic layer
│   │   ├── __init__.py
│   │   └── user_service.py
│   ├── repositories/        # Data access layer
│   │   ├── __init__.py
│   │   └── user_repository.py
│   ├── api/                 # API routes
│   │   ├── __init__.py
│   │   └── users.py
│   └── core/                # Core utilities
│       ├── __init__.py
│       ├── config.py
│       ├── exceptions.py
│       └── logging.py
├── tests/                   # Test suite
│   ├── __init__.py
│   ├── conftest.py
│   ├── test_user_service.py
│   ├── test_user_repository.py
│   └── test_api.py
├── requirements.txt
└── README.md
```