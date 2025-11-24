"""
Audit Service

Central service for logging security and administrative events.
Provides a consistent interface for audit trail creation across the application.

Usage:
    from app.services.audit_service import log_event, get_client_ip
    from app.models.audit_log import AuditAction
    
    # Log authentication event
    log_event(
        db=db,
        actor_id=user.id,
        action=AuditAction.LOGIN_SUCCESS,
        details={"ip": get_client_ip(request), "user_agent": request.headers.get("User-Agent")}
    )
    
    # Log admin operation
    log_event(
        db=db,
        actor_id=admin.id,
        action=AuditAction.USER_CREATE,
        target_type="User",
        target_id=new_user.id,
        details={"email": new_user.email, "role": new_user.role}
    )
"""

from datetime import datetime, timezone
from typing import Optional, Dict, Any
from sqlalchemy.orm import Session
from fastapi import Request

from app.models.audit_log import AuditLog, AuditAction


def log_event(
    db: Session,
    *,
    action: str,
    actor_id: Optional[int] = None,
    target_type: Optional[str] = None,
    target_id: Optional[int] = None,
    details: Optional[Dict[str, Any]] = None
) -> AuditLog:
    """
    Log an audit event to the database.
    
    This is the primary function for creating audit log entries.
    All audit logging should go through this function for consistency.
    
    Args:
        db: Database session
        action: Action performed (use AuditAction constants)
        actor_id: ID of user who performed the action (nullable for anonymous events)
        target_type: Type of resource affected (e.g., "User", "Employee")
        target_id: ID of the affected resource
        details: Additional context as JSON (IP, user agent, changed fields, etc.)
    
    Returns:
        Created AuditLog instance
    
    Examples:
        # Authentication event
        log_event(
            db=db,
            action=AuditAction.LOGIN_SUCCESS,
            actor_id=user.id,
            details={"ip": "192.168.1.1", "user_agent": "Chrome/90.0"}
        )
        
        # Failed login (anonymous)
        log_event(
            db=db,
            action=AuditAction.LOGIN_FAILURE,
            details={"email": "attacker@example.com", "ip": "1.2.3.4"}
        )
        
        # Admin operation
        log_event(
            db=db,
            action=AuditAction.USER_UPDATE,
            actor_id=admin.id,
            target_type="User",
            target_id=user.id,
            details={"changes": {"role": {"from": "employee", "to": "manager"}}}
        )
    """
    audit_log = AuditLog(
        timestamp=datetime.now(timezone.utc),
        user_id=actor_id,
        action=action,
        target_type=target_type,
        target_id=target_id,
        details=details or {}
    )
    
    db.add(audit_log)
    db.commit()
    db.refresh(audit_log)
    
    return audit_log


def log_auth_event(
    db: Session,
    *,
    action: str,
    user_id: Optional[int],
    email: str,
    request: Request,
    success: bool = True,
    details: Optional[Dict[str, Any]] = None
) -> AuditLog:
    """
    Convenience function for logging authentication events.
    
    Automatically captures IP address and user agent from request.
    
    Args:
        db: Database session
        action: Authentication action (use AuditAction.* constants)
        user_id: User ID (None for failed attempts)
        email: User email
        request: FastAPI Request object
        success: Whether the authentication was successful
        details: Additional details to log
    
    Returns:
        Created AuditLog instance
    """
    event_details = {
        "email": email,
        "ip": get_client_ip(request),
        "user_agent": request.headers.get("User-Agent", "Unknown"),
        "success": success
    }
    
    if details:
        event_details.update(details)
    
    return log_event(
        db=db,
        action=action,
        actor_id=user_id,
        details=event_details
    )


def log_admin_operation(
    db: Session,
    *,
    action: str,
    admin_id: int,
    target_type: str,
    target_id: int,
    changes: Optional[Dict[str, Any]] = None,
    request: Optional[Request] = None
) -> AuditLog:
    """
    Convenience function for logging administrative operations.
    
    Captures what changed and who made the change.
    
    Args:
        db: Database session
        action: Admin action (use AuditAction.* constants)
        admin_id: ID of admin performing the action
        target_type: Type of resource (e.g., "User", "Employee")
        target_id: ID of the affected resource
        changes: Dictionary of field changes (before/after values)
        request: Optional FastAPI Request object for IP/user agent
    
    Returns:
        Created AuditLog instance
    """
    event_details = {}
    
    if changes:
        event_details["changes"] = changes
    
    if request:
        event_details["ip"] = get_client_ip(request)
        event_details["user_agent"] = request.headers.get("User-Agent", "Unknown")
    
    return log_event(
        db=db,
        action=action,
        actor_id=admin_id,
        target_type=target_type,
        target_id=target_id,
        details=event_details
    )


def get_client_ip(request: Request) -> str:
    """
    Extract client IP address from request.
    
    Handles X-Forwarded-For header for proxied requests.
    
    Args:
        request: FastAPI Request object
    
    Returns:
        Client IP address as string
    """
    # Check for X-Forwarded-For (behind proxy/load balancer)
    forwarded = request.headers.get("X-Forwarded-For")
    if forwarded:
        # Take first IP (client IP) from comma-separated list
        return forwarded.split(",")[0].strip()
    
    # Check for X-Real-IP (nginx)
    real_ip = request.headers.get("X-Real-IP")
    if real_ip:
        return real_ip
    
    # Fallback to direct client
    return request.client.host if request.client else "Unknown"


def get_user_agent(request: Request) -> str:
    """
    Extract user agent from request headers.
    
    Args:
        request: FastAPI Request object
    
    Returns:
        User agent string
    """
    return request.headers.get("User-Agent", "Unknown")


# Convenience functions for common audit events

def log_login_success(db: Session, user_id: int, email: str, request: Request) -> AuditLog:
    """Log successful login attempt."""
    return log_auth_event(
        db=db,
        action=AuditAction.LOGIN_SUCCESS,
        user_id=user_id,
        email=email,
        request=request,
        success=True
    )


def log_login_failure(db: Session, email: str, request: Request, reason: str = "Invalid credentials") -> AuditLog:
    """Log failed login attempt."""
    return log_auth_event(
        db=db,
        action=AuditAction.LOGIN_FAILURE,
        user_id=None,  # No user ID for failed attempts
        email=email,
        request=request,
        success=False,
        details={"reason": reason}
    )


def log_logout(db: Session, user_id: int, email: str, request: Request) -> AuditLog:
    """Log user logout."""
    return log_auth_event(
        db=db,
        action=AuditAction.LOGOUT,
        user_id=user_id,
        email=email,
        request=request
    )


def log_token_refresh(db: Session, user_id: int, email: str, request: Request) -> AuditLog:
    """Log token refresh event."""
    return log_auth_event(
        db=db,
        action=AuditAction.TOKEN_REFRESH,
        user_id=user_id,
        email=email,
        request=request
    )


def log_user_created(db: Session, admin_id: int, new_user_id: int, email: str, role: str, request: Optional[Request] = None) -> AuditLog:
    """Log user creation by admin."""
    return log_admin_operation(
        db=db,
        action=AuditAction.USER_CREATE,
        admin_id=admin_id,
        target_type="User",
        target_id=new_user_id,
        changes={"email": email, "role": role},
        request=request
    )


def log_user_updated(db: Session, admin_id: int, user_id: int, changes: Dict[str, Any], request: Optional[Request] = None) -> AuditLog:
    """Log user update by admin."""
    return log_admin_operation(
        db=db,
        action=AuditAction.USER_UPDATE,
        admin_id=admin_id,
        target_type="User",
        target_id=user_id,
        changes=changes,
        request=request
    )


def log_user_deleted(db: Session, admin_id: int, user_id: int, email: str, request: Optional[Request] = None) -> AuditLog:
    """Log user deletion by admin."""
    return log_admin_operation(
        db=db,
        action=AuditAction.USER_DELETE,
        admin_id=admin_id,
        target_type="User",
        target_id=user_id,
        changes={"email": email},
        request=request
    )
