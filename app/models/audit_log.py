"""
Audit Log Model

Records security and administrative events for compliance and security analysis.
Provides a comprehensive audit trail of all critical actions in the system.

Security Use Cases:
- Track authentication events (login, logout, token refresh)
- Monitor admin operations (user CRUD, role changes, data modifications)
- Compliance reporting (who did what, when, and from where)
- Security incident investigation
- Debugging and troubleshooting
"""

from datetime import datetime, timezone
from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, Index, Text
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import relationship
from app.core.database import Base


class AuditLog(Base):
    """
    Audit Log Model
    
    Records all security-relevant and administrative events in the system.
    Immutable records - never updated or deleted, only created.
    
    Attributes:
        id: Primary key
        timestamp: When the event occurred (timezone-aware)
        user_id: Who performed the action (nullable for anonymous events)
        action: What action was performed (e.g., "login.success", "user.create")
        target_type: Type of resource affected (e.g., "User", "Employee")
        target_id: ID of the affected resource
        details: Additional metadata (IP address, changed fields, etc.)
        user: Relationship to User model
    """
    
    __tablename__ = "audit_logs"
    
    # Primary Key
    id = Column(Integer, primary_key=True, index=True)
    
    # Timestamp
    timestamp = Column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        nullable=False,
        index=True
    )
    
    # Actor (who performed the action)
    user_id = Column(
        Integer,
        ForeignKey("users.id", ondelete="SET NULL"),
        nullable=True,  # Nullable for anonymous events (failed login attempts)
        index=True
    )
    
    # Action Details
    action = Column(String(100), nullable=False, index=True)  # e.g., "login.success", "user.create"
    
    # Target (what was affected)
    target_type = Column(String(50), nullable=True)  # e.g., "User", "Employee", "CareerPath"
    target_id = Column(Integer, nullable=True)
    
    # Additional Context (JSON)
    details = Column(JSONB, nullable=True)  # IP address, user agent, changed fields, etc.
    
    # Relationships
    user = relationship("User", foreign_keys=[user_id])
    
    # Composite Indexes for common queries
    __table_args__ = (
        Index('ix_audit_logs_action_timestamp', 'action', 'timestamp'),
        Index('ix_audit_logs_user_timestamp', 'user_id', 'timestamp'),
        Index('ix_audit_logs_target', 'target_type', 'target_id'),
    )
    
    def __repr__(self):
        return f"<AuditLog(id={self.id}, action={self.action}, user_id={self.user_id}, timestamp={self.timestamp})>"
    
    @property
    def event_summary(self) -> str:
        """
        Human-readable event summary
        
        Returns:
            String describing the event
        """
        user_info = f"User {self.user_id}" if self.user_id else "Anonymous"
        target_info = f" on {self.target_type}:{self.target_id}" if self.target_type else ""
        return f"{user_info} - {self.action}{target_info}"


# Common action constants for consistency
class AuditAction:
    """
    Standard audit action names for consistency across the application.
    
    Naming Convention: <resource>.<action>
    - Authentication: auth.*
    - User Management: user.*
    - Employee Management: employee.*
    - Career Path Management: career_path.*
    - Competency Management: competency.*
    - Administrative: admin.*
    """
    
    # Authentication Events
    LOGIN_SUCCESS = "auth.login.success"
    LOGIN_FAILURE = "auth.login.failure"
    LOGOUT = "auth.logout"
    TOKEN_REFRESH = "auth.token.refresh"
    PASSWORD_CHANGE = "auth.password.change"
    EMAIL_VERIFY_REQUEST = "auth.email.verify_request"
    EMAIL_VERIFY_SUCCESS = "auth.email.verify_success"
    
    # User Management
    USER_CREATE = "user.create"
    USER_UPDATE = "user.update"
    USER_DELETE = "user.delete"
    USER_ROLE_CHANGE = "user.role.change"
    USER_ACTIVATE = "user.activate"
    USER_DEACTIVATE = "user.deactivate"
    
    # Employee Management
    EMPLOYEE_CREATE = "employee.create"
    EMPLOYEE_UPDATE = "employee.update"
    EMPLOYEE_DELETE = "employee.delete"
    EMPLOYEE_COMPETENCY_ADD = "employee.competency.add"
    EMPLOYEE_COMPETENCY_UPDATE = "employee.competency.update"
    EMPLOYEE_COMPETENCY_REMOVE = "employee.competency.remove"
    
    # Career Path Management
    CAREER_PATH_CREATE = "career_path.create"
    CAREER_PATH_UPDATE = "career_path.update"
    CAREER_PATH_DELETE = "career_path.delete"
    CAREER_PATH_COMPETENCY_ADD = "career_path.competency.add"
    CAREER_PATH_COMPETENCY_REMOVE = "career_path.competency.remove"
    
    # Competency Management
    COMPETENCY_CREATE = "competency.create"
    COMPETENCY_UPDATE = "competency.update"
    COMPETENCY_DELETE = "competency.delete"
    
    # Administrative Actions
    ADMIN_ACCESS = "admin.access"
    ADMIN_EXPORT_DATA = "admin.export.data"
    ADMIN_IMPORT_DATA = "admin.import.data"
    ADMIN_SYSTEM_CONFIG = "admin.system.config"
    
    # Gap Analysis
    GAP_ANALYSIS_VIEW = "gap_analysis.view"
    GAP_ANALYSIS_EXPORT = "gap_analysis.export"
