"""
Competency API endpoints
"""

from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session, joinedload
from app.core.database import get_db
from app.core.security import get_current_active_user, get_current_active_admin
from app.models import Competency, CompetencyGroup, CompetencyLevel
from app.models.user import User
from app.schemas.competency import (
    CompetencyResponse,
    CompetencyListResponse,
    CompetencyCreate,
    CompetencyUpdate,
    CompetencyGroupResponse,
    CompetencyGroupCreate,
    CompetencyGroupUpdate
)
from app.services import competency_service

router = APIRouter()

@router.get("/competencies", response_model=CompetencyListResponse)
def list_competencies(
    skip: int = Query(0, ge=0, description="Number of records to skip"),
    limit: int = Query(100, ge=1, le=1000, description="Max records to return"),
    group_code: Optional[str] = Query(None, description="Filter by group code (CORE/LEAD/FUNC)"),
    name: Optional[str] = Query(None, description="Filter by competency name (partial, case-insensitive)"),
    include_levels: bool = Query(True, description="Include proficiency levels"),
    db: Session = Depends(get_db)
):
    """Get list of competencies with pagination & filters (group_code, name).

    Delegates filtering logic to service layer for consistency & reuse.
    """
    competencies, total = competency_service.get_competencies(
        db=db,
        skip=skip,
        limit=limit,
        group_code=group_code,
        name=name,
        include_levels=include_levels
    )
    return {
        "success": True,
        "data": competencies,
        "meta": {
            "total": total,
            "skip": skip,
            "limit": limit,
            "returned": len(competencies),
            "filters": {
                "group_code": group_code,
                "name": name
            }
        }
    }

@router.get("/competencies/{competency_id}", response_model=CompetencyResponse)
def get_competency(
    competency_id: int,
    include_levels: bool = Query(True, description="Include proficiency levels"),
    db: Session = Depends(get_db)
):
    """
    Get a specific competency by ID
    
    - **competency_id**: Competency ID
    - **include_levels**: Include 5 proficiency levels
    """
    query = db.query(Competency)
    
    # Eager load relationships
    if include_levels:
        query = query.options(joinedload(Competency.levels))
    query = query.options(joinedload(Competency.group))
    query = query.options(joinedload(Competency.job_family))
    
    competency = query.filter(Competency.id == competency_id).first()
    
    if not competency:
        raise HTTPException(status_code=404, detail=f"Competency with id {competency_id} not found")
    
    return {
        "success": True,
        "data": competency
    }

@router.get("/competencies/group/{group_code}", response_model=CompetencyListResponse)
def get_competencies_by_group(
    group_code: str,
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
    include_levels: bool = Query(True),
    db: Session = Depends(get_db)
):
    """
    Get competencies by group code (CORE/LEAD/FUNC)
    
    - **group_code**: CORE, LEAD, or FUNC
    - **skip**: Pagination offset
    - **limit**: Max results
    - **include_levels**: Include proficiency levels
    """
    # Validate group code
    valid_codes = ["CORE", "LEAD", "FUNC"]
    group_code = group_code.upper()
    if group_code not in valid_codes:
        raise HTTPException(
            status_code=400,
            detail=f"Invalid group code. Must be one of: {', '.join(valid_codes)}"
        )
    
    query = db.query(Competency).join(CompetencyGroup).filter(
        CompetencyGroup.code == group_code
    )
    
    # Eager load relationships
    if include_levels:
        query = query.options(joinedload(Competency.levels))
    query = query.options(joinedload(Competency.group))
    query = query.options(joinedload(Competency.job_family))
    
    total = query.count()
    competencies = query.offset(skip).limit(limit).all()
    
    return {
        "success": True,
        "data": competencies,
        "meta": {
            "total": total,
            "skip": skip,
            "limit": limit,
            "returned": len(competencies),
            "group_code": group_code
        }
    }

@router.post("/competencies", response_model=CompetencyResponse, status_code=201)
def create_competency(
    competency: CompetencyCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_admin)
):
    """
    Create a new competency (Admin only)
    
    Requires: Admin role
    
    - **name**: Competency name
    - **code**: Unique code (optional)
    - **definition**: Competency definition
    - **group_id**: Reference to CompetencyGroup
    - **job_family_id**: Reference to JobFamily (optional, for FUNC competencies)
    """
    db_competency = competency_service.create_competency(db, competency)
    
    return {
        "success": True,
        "data": db_competency
    }

@router.put("/competencies/{competency_id}", response_model=CompetencyResponse)
def update_competency(
    competency_id: int,
    competency_update: CompetencyUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_admin)
):
    """
    Update an existing competency (Admin only)
    
    Requires: Admin role
    
    - **competency_id**: Competency ID
    - **competency_update**: Fields to update (partial update supported)
    """
    db_competency = competency_service.update_competency(db, competency_id, competency_update)
    
    if not db_competency:
        raise HTTPException(status_code=404, detail=f"Competency with id {competency_id} not found")
    
    return {
        "success": True,
        "data": db_competency
    }

@router.delete("/competencies/{competency_id}", status_code=204)
def delete_competency(
    competency_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_admin)
):
    """
    Delete a competency (Admin only)
    
    Requires: Admin role
    
    Validates that competency is not:
    - Assigned to any employees
    - Required by any career paths
    
    - **competency_id**: Competency ID
    """
    competency_service.delete_competency(db, competency_id)
    return None


# ===== CompetencyGroup CRUD Endpoints (Admin only) =====

@router.get("/groups", response_model=List[CompetencyGroupResponse])
def list_competency_groups(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """
    Get all competency groups (authenticated users)
    
    Returns all groups: CORE, LEAD, FUNC
    """
    groups = db.query(CompetencyGroup).all()
    return groups


@router.get("/groups/{group_id}", response_model=CompetencyGroupResponse)
def get_competency_group(
    group_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """
    Get a specific competency group by ID (authenticated users)
    
    - **group_id**: CompetencyGroup ID
    """
    group = db.query(CompetencyGroup).filter(CompetencyGroup.id == group_id).first()
    
    if not group:
        raise HTTPException(status_code=404, detail=f"CompetencyGroup with id {group_id} not found")
    
    return group


@router.post("/groups", response_model=CompetencyGroupResponse, status_code=201)
def create_competency_group(
    group: CompetencyGroupCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_admin)
):
    """
    Create a new competency group (Admin only)
    
    Requires: Admin role
    
    Validates uniqueness of name and code.
    
    - **name**: Group name (e.g., "Core Competencies")
    - **code**: Group code (e.g., "CORE")
    """
    db_group = competency_service.create_competency_group(db, group)
    return db_group


@router.put("/groups/{group_id}", response_model=CompetencyGroupResponse)
def update_competency_group(
    group_id: int,
    group_update: CompetencyGroupUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_admin)
):
    """
    Update an existing competency group (Admin only)
    
    Requires: Admin role
    
    Validates uniqueness of name and code if changed.
    
    - **group_id**: CompetencyGroup ID
    - **group_update**: Fields to update (partial update supported)
    """
    db_group = competency_service.update_competency_group(db, group_id, group_update)
    
    if not db_group:
        raise HTTPException(status_code=404, detail=f"CompetencyGroup with id {group_id} not found")
    
    return db_group


@router.delete("/groups/{group_id}", status_code=204)
def delete_competency_group(
    group_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_admin)
):
    """
    Delete a competency group (Admin only)
    
    Requires: Admin role
    
    Validates that group has no associated competencies.
    
    - **group_id**: CompetencyGroup ID
    """
    competency_service.delete_competency_group(db, group_id)
    return None
