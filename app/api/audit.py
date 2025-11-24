"""
Audit Logs API Endpoints

Admin-only endpoints for viewing audit logs.
Provides read-only access to security and administrative event logs.
"""

from fastapi import APIRouter, Depends, Query, HTTPException, status
from sqlalchemy.orm import Session
from sqlalchemy import desc, or_
from typing import List, Optional
from datetime import datetime

from app.core.database import get_db
from app.core.security import get_current_active_admin
from app.models.audit_log import AuditLog
from app.models.user import User
from app.schemas.audit import AuditLogResponse, AuditLogListResponse

router = APIRouter(
    prefix="/audit-logs",
    tags=["Audit Logs (Admin)"]
)


@router.get("/", response_model=AuditLogListResponse, status_code=status.HTTP_200_OK)
def list_audit_logs(
    skip: int = Query(0, ge=0, description="Number of records to skip"),
    limit: int = Query(50, ge=1, le=100, description="Maximum number of records to return"),
    user_id: Optional[int] = Query(None, description="Filter by user ID"),
    action: Optional[str] = Query(None, description="Filter by action (e.g., 'auth.login.success')"),
    target_type: Optional[str] = Query(None, description="Filter by target type (e.g., 'User')"),
    start_date: Optional[datetime] = Query(None, description="Filter by start date (ISO 8601)"),
    end_date: Optional[datetime] = Query(None, description="Filter by end date (ISO 8601)"),
    db: Session = Depends(get_db),
    current_admin: User = Depends(get_current_active_admin)
):
    """
    List audit logs with filtering and pagination (admin only).
    
    **Authorization**: Admin only
    
    Returns audit logs in reverse chronological order (newest first).
    
    **Query Parameters**:
    - skip: Number of records to skip (default: 0)
    - limit: Maximum records to return (default: 50, max: 100)
    - user_id: Filter by user who performed the action
    - action: Filter by action name (exact match)
    - target_type: Filter by resource type (exact match)
    - start_date: Filter events after this timestamp
    - end_date: Filter events before this timestamp
    
    **Returns**: List of audit logs with total count
    
    **Example Queries**:
    - All login attempts: `?action=auth.login.success`
    - User operations: `?target_type=User`
    - Specific user's actions: `?user_id=5`
    - Date range: `?start_date=2025-11-01T00:00:00Z&end_date=2025-11-23T23:59:59Z`
    """
    # Build query
    query = db.query(AuditLog)
    
    # Apply filters
    if user_id is not None:
        query = query.filter(AuditLog.user_id == user_id)
    
    if action:
        query = query.filter(AuditLog.action == action)
    
    if target_type:
        query = query.filter(AuditLog.target_type == target_type)
    
    if start_date:
        query = query.filter(AuditLog.timestamp >= start_date)
    
    if end_date:
        query = query.filter(AuditLog.timestamp <= end_date)
    
    # Get total count before pagination
    total = query.count()
    
    # Order by timestamp descending (newest first)
    query = query.order_by(desc(AuditLog.timestamp))
    
    # Apply pagination
    logs = query.offset(skip).limit(limit).all()
    
    # Convert to response model
    log_responses = []
    for log in logs:
        log_response = AuditLogResponse(
            id=log.id,
            timestamp=log.timestamp,
            user_id=log.user_id,
            user_email=log.user.email if log.user else None,
            action=log.action,
            target_type=log.target_type,
            target_id=log.target_id,
            details=log.details,
            event_summary=log.event_summary
        )
        log_responses.append(log_response)
    
    return AuditLogListResponse(
        total=total,
        skip=skip,
        limit=limit,
        logs=log_responses
    )


@router.get("/{log_id}", response_model=AuditLogResponse, status_code=status.HTTP_200_OK)
def get_audit_log(
    log_id: int,
    db: Session = Depends(get_db),
    current_admin: User = Depends(get_current_active_admin)
):
    """
    Get a specific audit log by ID (admin only).
    
    **Authorization**: Admin only
    
    **Path Parameters**:
    - log_id: Audit log ID
    
    **Returns**: Audit log details
    
    **Error Cases**:
    - 404: Audit log not found
    - 403: Not admin
    """
    log = db.query(AuditLog).filter(AuditLog.id == log_id).first()
    
    if not log:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Audit log with id {log_id} not found"
        )
    
    return AuditLogResponse(
        id=log.id,
        timestamp=log.timestamp,
        user_id=log.user_id,
        user_email=log.user.email if log.user else None,
        action=log.action,
        target_type=log.target_type,
        target_id=log.target_id,
        details=log.details,
        event_summary=log.event_summary
    )


@router.get("/actions/list", response_model=List[str], status_code=status.HTTP_200_OK)
def list_actions(
    db: Session = Depends(get_db),
    current_admin: User = Depends(get_current_active_admin)
):
    """
    Get list of distinct action types in the audit log (admin only).
    
    **Authorization**: Admin only
    
    Useful for filtering and analytics.
    
    **Returns**: List of unique action names
    """
    actions = db.query(AuditLog.action).distinct().order_by(AuditLog.action).all()
    return [action[0] for action in actions]


@router.get("/stats/summary", response_model=dict, status_code=status.HTTP_200_OK)
def get_audit_stats(
    start_date: Optional[datetime] = Query(None, description="Start date for statistics"),
    end_date: Optional[datetime] = Query(None, description="End date for statistics"),
    db: Session = Depends(get_db),
    current_admin: User = Depends(get_current_active_admin)
):
    """
    Get audit log statistics (admin only).
    
    **Authorization**: Admin only
    
    Provides summary statistics for audit logs.
    
    **Query Parameters**:
    - start_date: Start date for statistics (optional)
    - end_date: End date for statistics (optional)
    
    **Returns**: Statistics including:
    - total_events: Total number of audit events
    - auth_events: Number of authentication events
    - admin_operations: Number of admin operations
    - unique_users: Number of unique users in logs
    - failed_logins: Number of failed login attempts
    """
    query = db.query(AuditLog)
    
    if start_date:
        query = query.filter(AuditLog.timestamp >= start_date)
    
    if end_date:
        query = query.filter(AuditLog.timestamp <= end_date)
    
    total_events = query.count()
    
    auth_events = query.filter(AuditLog.action.like("auth.%")).count()
    admin_operations = query.filter(
        or_(
            AuditLog.action.like("user.%"),
            AuditLog.action.like("employee.%"),
            AuditLog.action.like("admin.%")
        )
    ).count()
    
    failed_logins = query.filter(AuditLog.action == "auth.login.failure").count()
    
    unique_users = db.query(AuditLog.user_id).filter(AuditLog.user_id.isnot(None)).distinct().count()
    
    return {
        "total_events": total_events,
        "auth_events": auth_events,
        "admin_operations": admin_operations,
        "failed_logins": failed_logins,
        "unique_users": unique_users,
        "date_range": {
            "start": start_date.isoformat() if start_date else None,
            "end": end_date.isoformat() if end_date else None
        }
    }
