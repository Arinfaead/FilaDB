from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from .core.config import settings
from .core.database import create_db_and_tables
from .api import auth, files, inventory, admin

# Create FastAPI app
app = FastAPI(
    title=settings.app_name,
    version=settings.app_version,
    description="A self-hosted application that centralises 3D-printing assets for teams",
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include API routers
app.include_router(auth.router, prefix="/api/v1/auth", tags=["auth"])
app.include_router(files.router, prefix="/api/v1/files", tags=["files"])
app.include_router(inventory.router, prefix="/api/v1/inventory", tags=["inventory"])
app.include_router(admin.router, prefix="/api/v1/admin", tags=["admin"])

# Serve static files (frontend)
app.mount("/static", StaticFiles(directory="../frontend"), name="static")

# Serve frontend at root
@app.get("/")
async def read_root():
    """Serve the main frontend page"""
    from fastapi.responses import FileResponse
    return FileResponse("../frontend/index.html")


@app.on_event("startup")
async def startup_event():
    """Initialize database on startup"""
    create_db_and_tables()


@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {"status": "healthy", "version": settings.app_version}
