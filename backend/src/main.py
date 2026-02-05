"""FastAPI application entry point."""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from src.api.v1.router import api_router
from src.database.connection import create_tables
from src.config import get_settings

settings = get_settings()

# Create FastAPI application
app = FastAPI(
    title="Todo API",
    version="2.0.0",
    description="Full-stack todo application REST API with JWT authentication",
    docs_url="/docs",
    redoc_url="/redoc",
)

# Configure CORS for Next.js frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.allowed_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# Startup event - create database tables
@app.on_event("startup")
def on_startup():
    """Initialize database tables on application startup."""
    create_tables()


# Include API routers
app.include_router(api_router, prefix="/api/v1")


# Health check endpoint
@app.get("/", tags=["health"])
def health_check():
    """
    Health check endpoint to verify the API is running.

    Returns:
        JSON with status and version information
    """
    return {
        "status": "ok",
        "service": "Todo API",
        "version": "2.0.0",
        "environment": settings.environment
    }


@app.get("/health", tags=["health"])
def health():
    """
    Alternative health check endpoint.

    Returns:
        JSON with status
    """
    return {"status": "healthy"}
