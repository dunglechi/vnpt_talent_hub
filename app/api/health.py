"""
Health check endpoints
"""

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.models import CompetencyGroup

router = APIRouter()

@router.get("/health")
def health_check(db: Session = Depends(get_db)):
    """
    Health check endpoint
    
    Returns:
        - API status
        - Database connectivity
        - Basic statistics
    """
    try:
        # Test database connection
        groups_count = db.query(CompetencyGroup).count()
        
        return {
            "status": "healthy",
            "api": "operational",
            "database": "connected",
            "version": "1.1.0",
            "stats": {
                "competency_groups": groups_count
            }
        }
    except Exception as e:
        return {
            "status": "unhealthy",
            "api": "operational",
            "database": "disconnected",
            "error": str(e)
        }
