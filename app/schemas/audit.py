"""
Audit Log Pydantic Schemas

Response models for audit log API endpoints.
"""

from pydantic import BaseModel, Field
from datetime import datetime
from typing import Optional, Dict, Any, List


class AuditLogResponse(BaseModel):
    """Audit log response schema"""
    
    id: int = Field(..., description="Audit log ID")
    timestamp: datetime = Field(..., description="When the event occurred")
    user_id: Optional[int] = Field(None, description="User who performed the action (null for anonymous)")
    user_email: Optional[str] = Field(None, description="Email of user who performed the action")
    action: str = Field(..., description="Action performed (e.g., 'auth.login.success')")
    target_type: Optional[str] = Field(None, description="Type of resource affected (e.g., 'User')")
    target_id: Optional[int] = Field(None, description="ID of affected resource")
    details: Optional[Dict[str, Any]] = Field(None, description="Additional event details (IP, user agent, changes, etc.)")
    event_summary: str = Field(..., description="Human-readable event summary")
    
    class Config:
        from_attributes = True


class AuditLogListResponse(BaseModel):
    """Paginated audit log list response"""
    
    total: int = Field(..., description="Total number of logs matching filters")
    skip: int = Field(..., description="Number of records skipped")
    limit: int = Field(..., description="Maximum records returned")
    logs: List[AuditLogResponse] = Field(..., description="List of audit logs")
