"""
FilaDB - Filament Management System
Main FastAPI application
"""

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
import os
from contextlib import asynccontextmanager

from .database import engine, Base
from .api import auth, users, manufacturers, materials, filaments, spools, printers
from .config import settings


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan events"""
    # Startup
    print("🚀 Starting FilaDB...")
    
    # Create database tables
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    
    yield
    
    # Shutdown
    print("🛑 Shutting down FilaDB...")


# Create FastAPI app
app = FastAPI(
    title="FilaDB",
    description="Comprehensive Filament Management System for 3D Printing",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc",
    lifespan=lifespan
)

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# Health check endpoint
@app.get("/health")
async def health_check():
    """Health check endpoint for Docker health checks"""
    return {"status": "healthy", "service": "FilaDB Backend"}


# Root endpoint
@app.get("/")
async def root():
    """Root endpoint with API information"""
    return {
        "message": "Welcome to FilaDB API",
        "version": "1.0.0",
        "docs": "/docs",
        "redoc": "/redoc"
    }


# Include API routers
app.include_router(auth.router, prefix="/api/auth", tags=["Authentication"])
app.include_router(users.router, prefix="/api/users", tags=["Users"])
app.include_router(manufacturers.router, prefix="/api/manufacturers", tags=["Manufacturers"])
app.include_router(materials.router, prefix="/api/materials", tags=["Materials"])
app.include_router(filaments.router, prefix="/api/filaments", tags=["Filaments"])
app.include_router(spools.router, prefix="/api/spools", tags=["Spools"])
app.include_router(printers.router, prefix="/api/printers", tags=["Printers"])


# Global exception handler
@app.exception_handler(Exception)
async def global_exception_handler(request, exc):
    """Global exception handler"""
    return JSONResponse(
        status_code=500,
        content={
            "detail": "Internal server error",
            "type": "internal_error"
        }
    )


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=8000,
        reload=True
    )
