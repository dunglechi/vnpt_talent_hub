from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from typing import List, Optional

from app.core.database import get_db
from app.core.security import get_current_active_user, get_current_active_admin
from app.schemas.career_path import CareerPath, CareerPathCreate, CareerPathUpdate
from app.services.career_path_service import (
    get_all_career_paths,
    get_career_path_by_id,
    create_career_path,
    update_career_path,
    delete_career_path
)
from app.services.career_path_service import _transform_to_schema

router = APIRouter()

@router.get("/", response_model=List[CareerPath])
def list_career_paths(
    skip: int = Query(0, ge=0, description="Number of records to skip"),
    limit: int = Query(100, ge=1, le=100, description="Maximum records to return"),
    role_name: Optional[str] = Query(None, description="Filter by role name (partial, case-insensitive)"),
    db: Session = Depends(get_db),
    current_user = Depends(get_current_active_user)
):
    """List career paths with optional role name filtering (authenticated users)."""
    paths = get_all_career_paths(db, skip=skip, limit=limit, role_name=role_name)
    return paths

@router.get("/{path_id}", response_model=CareerPath)
def get_career_path(
    path_id: int,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_active_user)
):
    """Get a specific career path by ID. Accessible to any authenticated user."""
    path = get_career_path_by_id(db, path_id)
    if not path:
        raise HTTPException(status_code=404, detail="Career path not found")
    return path


# ===== Admin CRUD Endpoints =====

@router.post("/", response_model=CareerPath, status_code=201)
def create_new_career_path(
    path_data: CareerPathCreate,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_active_admin)
):
    """
    Create a new career path with competency requirements (Admin only).
    
    Requires: Admin role
    
    - **job_family**: Job family category
    - **career_level**: Career level number
    - **role_name**: Role/position name
    - **description**: Optional description
    - **competencies**: List of competency links with required proficiency levels
    """
    career_path = create_career_path(db, path_data)
    return _transform_to_schema(career_path)


@router.put("/{path_id}", response_model=CareerPath)
def update_existing_career_path(
    path_id: int,
    path_data: CareerPathUpdate,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_active_admin)
):
    """
    Update an existing career path (Admin only).
    
    Requires: Admin role
    
    Supports partial updates. If competencies list is provided, it replaces
    all existing competency links (full replacement strategy).
    
    - **job_family**: Optional job family update
    - **career_level**: Optional career level update
    - **role_name**: Optional role name update
    - **description**: Optional description update
    - **competencies**: Optional list to replace all competency links
    """
    career_path = update_career_path(db, path_id, path_data)
    
    if not career_path:
        raise HTTPException(status_code=404, detail=f"Career path with id {path_id} not found")
    
    return _transform_to_schema(career_path)


@router.delete("/{path_id}", status_code=204)
def delete_existing_career_path(
    path_id: int,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_active_admin)
):
    """
    Delete a career path (Admin only).
    
    Requires: Admin role
    
    Automatically deletes associated competency links via cascade.
    
    - **path_id**: Career path ID to delete
    """
    delete_career_path(db, path_id)
    return None
