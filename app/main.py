"""
Main FastAPI application for the user management service.
"""
from fastapi import FastAPI, Request, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
import time

from app.core.config import settings
from app.core.logging import get_logger
from app.core.exceptions import UserManagementException
from app.api.users import router as users_router

logger = get_logger(__name__)

# Create FastAPI application
app = FastAPI(
    title=settings.app_name,
    version=settings.app_version,
    description="User management backend service",
    docs_url="/docs",
    redoc_url="/redoc",
    openapi_url="/openapi.json"
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # This should be configured appropriately
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.middleware("http")
async def add_process_time_header(request: Request, call_next):
    """Add processing time header to responses."""
    start_time = time.time()
    response = await call_next(request)
    process_time = time.time() - start_time
    response.headers["X-Process-Time"] = str(process_time)
    return response


@app.middleware("http")
async def log_requests(request: Request, call_next):
    """Log all incoming requests."""
    start_time = time.time()
    
    logger.info(
        "Incoming request",
        method=request.method,
        url=str(request.url),
        client_ip=request.client.host if request.client else None
    )
    
    response = await call_next(request)
    
    process_time = time.time() - start_time
    logger.info(
        "Request completed",
        method=request.method,
        url=str(request.url),
        status_code=response.status_code,
        process_time=process_time
    )
    
    return response


@app.exception_handler(UserManagementException)
async def user_management_exception_handler(request: Request, exc: UserManagementException):
    """Handle custom user management exceptions."""
    logger.error(
        "User management exception",
        exception_type=type(exc).__name__,
        exception_message=str(exc),
        url=str(request.url)
    )
    
    return JSONResponse(
        status_code=500,
        content={"detail": str(exc)}
    )


@app.exception_handler(Exception)
async def general_exception_handler(request: Request, exc: Exception):
    """Handle general exceptions."""
    logger.error(
        "Unhandled exception",
        exception_type=type(exc).__name__,
        exception_message=str(exc),
        url=str(request.url)
    )
    
    return JSONResponse(
        status_code=500,
        content={"detail": "Internal server error"}
    )


# Include routers
app.include_router(users_router)


@app.get("/", tags=["health"])
async def root():
    """Root endpoint with service info."""
    return {
        "message": "User Management Service",
        "version": settings.app_version,
        "status": "healthy",
        "docs": "/docs"
    }


@app.get("/health", tags=["health"])
async def health_check():
    """Health check endpoint."""
    return {
        "status": "healthy",
        "service": settings.app_name,
        "version": settings.app_version
    }


if __name__ == "__main__":
    import uvicorn
    
    logger.info("Starting User Management Service", version=settings.app_version)
    
    uvicorn.run(
        "app.main:app",
        host=settings.host,
        port=settings.port,
        reload=settings.debug,
        log_level=settings.log_level.lower()
    )
