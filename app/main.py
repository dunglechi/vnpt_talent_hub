"""
FastAPI Main Application - VNPT Talent Hub
"""

from fastapi import FastAPI, Depends
import asyncio
from app.core.rate_limit import init_rate_limiter
from fastapi.middleware.cors import CORSMiddleware
from app.core.database import engine, Base
from app.api import competencies, health, auth, employees, career_paths, gap_analysis, users, audit

# Create database tables (development only - use Alembic in production)
Base.metadata.create_all(bind=engine)

# Initialize FastAPI app
app = FastAPI(
    title="VNPT Talent Hub API",
    description="API for VNPT Competency Management System",
    version="1.1.0",
    docs_url="/api/docs",
    redoc_url="/api/redoc",
    openapi_url="/api/openapi.json"
)

# CORS configuration
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://localhost:8000"],  # Frontend URLs
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(health.router, prefix="/api/v1", tags=["Health"])
app.include_router(competencies.router, prefix="/api/v1", tags=["Competencies"])
app.include_router(auth.router, prefix="/api/v1", tags=["Authentication"])
@app.on_event("startup")
async def _startup_rate_limit():
    await init_rate_limiter()

app.include_router(employees.router, prefix="/api/v1/employees", tags=["Employees"])
app.include_router(career_paths.router, prefix="/api/v1/career-paths", tags=["Career Paths"])
app.include_router(gap_analysis.router, prefix="/api/v1/gap-analysis", tags=["Gap Analysis"])
app.include_router(users.router, prefix="/api/v1/users", tags=["User Management"])
app.include_router(audit.router, prefix="/api/v1", tags=["Audit Logs"])


# Root endpoint
@app.get("/")
def root():
    """Root endpoint - API information"""
    return {
        "name": "VNPT Talent Hub API",
        "version": "1.1.0",
        "status": "operational",
        "docs": "/api/docs",
        "health": "/api/v1/health"
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("app.main:app", host="0.0.0.0", port=8000, reload=True)
