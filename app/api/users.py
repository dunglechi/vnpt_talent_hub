"""
Admin-only API endpoints for User and Employee management.
All endpoints require admin privileges.
"""
from fastapi import APIRouter, Depends, HTTPException, status, Query, Request
from app.core.rate_limit import user_create_rate_limiter
from sqlalchemy.orm import Session
from typing import List, Optional

from app.core.database import get_db
from app.core.security import get_current_active_admin
from app.models.audit_log import AuditAction
from app.services.audit_service import log_user_created, log_user_updated, log_user_deleted
from app.schemas.user_management import (
    UserEmployeeCreate,
    UserEmployeeUpdate,
    UserEmployeeResponse
)
from app.services.user_service import (
    create_user_and_employee,
    get_user_by_id,
    get_all_users,
    update_user_and_employee,
    delete_user_and_employee
)

router = APIRouter(
    tags=["User Management (Admin)"]
)


@router.get("/", response_model=List[UserEmployeeResponse], status_code=status.HTTP_200_OK)
def list_users(
    skip: int = Query(0, ge=0, description="Number of records to skip"),
    limit: int = Query(100, ge=1, le=100, description="Maximum number of records to return"),
    name: Optional[str] = Query(None, description="Filter by full name (partial, case-insensitive)"),
    email: Optional[str] = Query(None, description="Filter by email (partial, case-insensitive)"),
    department: Optional[str] = Query(None, description="Filter by department (partial, case-insensitive)"),
    db: Session = Depends(get_db),
    current_user = Depends(get_current_active_admin)
):
    """List users (admin only) with optional filters.

    Supports case-insensitive partial matching on name, email, and department.
    Pagination applied after filtering.
    """
    users = get_all_users(
        db,
        skip=skip,
        limit=limit,
        name=name,
        email=email,
        department=department
    )
    return users


@router.post("/", response_model=UserEmployeeResponse, status_code=status.HTTP_201_CREATED, dependencies=[Depends(user_create_rate_limiter())])
def create_user(
    request: Request,
    user_data: UserEmployeeCreate,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_active_admin)
):
    """
    Create a new user and their employee profile (admin only).
    
    **Authorization**: Admin only
    
    Creates both User and Employee records in a single transaction.
    
    **Request Body**:
    - email: User email (must be unique)
    - password: User password (min 8 characters)
    - full_name: User's full name
    - role: User role (admin/manager/employee) [default: employee]
    - department: Employee department (optional)
    - job_title: Employee job title (optional)
    - manager_id: Manager's employee ID (optional)
    
    **Returns**: Created user with employee information
    
    **Error Cases**:
    - 400: Email already exists, invalid role, or manager_id not found
    - 403: Not admin
    """
    user = create_user_and_employee(db, user_data)
    
    # Log user creation
    log_user_created(
        db=db,
        admin_id=current_user.id,
        new_user_id=user.id,
        email=user.email,
        role=user.role,
        request=request
    )
    
    return user


@router.get("/{user_id}", response_model=UserEmployeeResponse, status_code=status.HTTP_200_OK)
def get_user(
    user_id: int,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_active_admin)
):
    """
    Get a specific user by ID with their employee profile (admin only).
    
    **Authorization**: Admin only
    
    **Path Parameters**:
    - user_id: User ID
    
    **Returns**: User with employee information
    
    **Error Cases**:
    - 404: User not found
    - 403: Not admin
    """
    user = get_user_by_id(db, user_id)
    
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"User with id {user_id} not found"
        )
    
    return user


@router.put("/{user_id}", response_model=UserEmployeeResponse, status_code=status.HTTP_200_OK)
def update_user(
    user_id: int,    request: Request,    user_data: UserEmployeeUpdate,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_active_admin)
):
    """
    Update a user and/or their employee profile (admin only).
    
    **Authorization**: Admin only
    
    Supports partial updates - only provided fields will be updated.
    
    **Path Parameters**:
    - user_id: User ID
    
    **Request Body** (all fields optional):
    - email: New email (must be unique if changed)
    - password: New password
    - full_name: New full name
    - role: New role (admin/manager/employee)
    - is_active: Active status
    - department: New department
    - job_title: New job title
    - manager_id: New manager's employee ID
    
    **Returns**: Updated user with employee information
    
    **Error Cases**:
    - 400: Email already exists, invalid role, or manager_id not found
    - 404: User not found
    - 403: Not admin
    """
    # Get existing user for change tracking
    existing_user = get_user_by_id(db, user_id)
    if not existing_user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"User with id {user_id} not found"
        )
    
    # Track changes for audit log
    changes = {}
    if user_data.full_name is not None and user_data.full_name != existing_user.full_name:
        changes["full_name"] = {"from": existing_user.full_name, "to": user_data.full_name}
    if user_data.role is not None and user_data.role != existing_user.role:
        changes["role"] = {"from": existing_user.role, "to": user_data.role}
    if user_data.email is not None and user_data.email != existing_user.email:
        changes["email"] = {"from": existing_user.email, "to": user_data.email}
    
    user = update_user_and_employee(db, user_id, user_data)
    
    # Log user update if there were changes
    if changes:
        log_user_updated(
            db=db,
            admin_id=current_user.id,
            user_id=user_id,
            changes=changes,
            request=request
        )
    
    return user


@router.delete("/{user_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_user(
    user_id: int,
    request: Request,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_active_admin)
):
    """
    Delete a user and their employee profile (admin only).
    
    **Authorization**: Admin only
    
    Deletes both User and Employee records.
    
    **Path Parameters**:
    - user_id: User ID
    
    **Returns**: 204 No Content on success
    
    **Error Cases**:
    - 404: User not found
    - 403: Not admin
    """
    # Get user before deletion for audit log
    existing_user = get_user_by_id(db, user_id)
    if not existing_user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"User with id {user_id} not found"
        )
    
    user_email = existing_user.email
    
    delete_user_and_employee(db, user_id)
    
    # Log user deletion
    log_user_deleted(
        db=db,
        admin_id=current_user.id,
        user_id=user_id,
        email=user_email,
        request=request
    )
    
    return None
