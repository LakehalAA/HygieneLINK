from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.trustedhost import TrustedHostMiddleware
from contextlib import asynccontextmanager
import uvicorn
import redis
from sqlalchemy import text

from app.core.config import settings
from app.core.database import engine
from app.api.v1 import (
    dashboard,
    forecasting,
    inventory,
    compliance,
    auth_router,
    facilities_router,
    hygiene_products_router,
    inventory_router,
    suppliers_router,
    users_router
)

# Lifespan context manager for startup/shutdown
@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup
    print("🚀 Starting HygieneLINK API...")
    
    # Test database connection
    try:
        with engine.connect() as conn:
            conn.execute(text("SELECT 1"))
        print("✅ Database connection successful")
    except Exception as e:
        print(f"❌ Database connection failed: {e}")
    
    # Test Redis connection
    try:
        redis_client = redis.Redis.from_url(settings.REDIS_URL)
        if redis_client is None:
            raise RuntimeError("Redis client is not initialized")
        redis_client.ping()
        print("✅ Redis connection successful")
    except Exception as e:
        print(f"❌ Redis connection failed: {e}")
    
    yield
    
    # Shutdown
    print("🛑 Shutting down HygieneLINK API...")

# Create FastAPI app
app = FastAPI(
    title="HygieneLINK API",
    description="Smart Hygiene Management System with AI-Powered Forecasting",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc",
    lifespan=lifespan
)

# Add middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.add_middleware(
    TrustedHostMiddleware,
    allowed_hosts=settings.ALLOWED_HOSTS
)

# Include routers
app.include_router(
    auth_router.router,
    prefix="/api/v1/auth",
    tags=["Auth"]
)

app.include_router(
    dashboard.router,
    prefix="/api/v1/dashboard",
    tags=["Dashboard"]
)

app.include_router(
    forecasting.router,
    prefix="/api/v1/forecasting",
    tags=["Forecasting"]
)

app.include_router(
    inventory.router,
    prefix="/api/v1/inventory",
    tags=["Inventory"]
)

app.include_router(
    compliance.router,
    prefix="/api/v1/compliance",
    tags=["Compliance"]
)

app.include_router(
    facilities_router.router,
    prefix="/api/v1/facilities",
    tags=["Facilities"]
)

app.include_router(
    hygiene_products_router.router,
    prefix="/api/v1/hygiene-products",
    tags=["Hygiene Products"]
)

app.include_router(
    inventory_router.router,
    prefix="/api/v1/inventory-management",
    tags=["Inventory Management"]
)

app.include_router(
    suppliers_router.router,
    prefix="/api/v1/suppliers",
    tags=["Suppliers"]
)

app.include_router(
    users_router.router,
    prefix="/api/v1/users",
    tags=["Users"]
)

# Root endpoints
@app.get("/")
async def root():
    return {
        "message": "HygieneLINK API - Smart Hygiene Management System",
        "version": "1.0.0",
        "docs": "/docs",
        "status": "operational"
    }

@app.get("/health")
async def health_check():
    """Health check endpoint for monitoring"""
    return {
        "status": "healthy",
        "service": "hygienelink-api",
        "timestamp": "2025-01-17T12:00:00Z"
    }