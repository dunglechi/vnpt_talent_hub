"""
Refresh Token Model

This model handles refresh tokens for JWT authentication with token rotation.
Refresh tokens allow users to obtain new access tokens without re-authenticating.

Security Features:
- Long-lived tokens (7 days default) stored securely
- Token rotation: old token revoked when new one issued
- Revocation support for logout and security events
- Indexed token field for fast lookups
"""

from datetime import datetime, timezone
from sqlalchemy import Column, Integer, String, DateTime, Boolean, ForeignKey, Index
from sqlalchemy.orm import relationship
from app.core.database import Base


class RefreshToken(Base):
    """
    Refresh Token Model
    
    Stores refresh tokens for JWT authentication with rotation support.
    Each token is single-use and revoked after generating a new access token.
    
    Attributes:
        id: Primary key
        user_id: Foreign key to users table
        token: Cryptographically secure random string (UUID4)
        expires_at: Token expiration timestamp
        created_at: Token creation timestamp
        is_revoked: Revocation flag (set True on use or logout)
        user: Relationship to User model
    """
    
    __tablename__ = "refresh_tokens"
    
    # Primary Key
    id = Column(Integer, primary_key=True, index=True)
    
    # User Relationship
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    
    # Token Data
    token = Column(String(255), unique=True, nullable=False, index=True)
    
    # Timestamps
    expires_at = Column(DateTime(timezone=True), nullable=False)
    created_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc), nullable=False)
    
    # Revocation
    is_revoked = Column(Boolean, default=False, nullable=False)
    
    # Relationships
    user = relationship("User", back_populates="refresh_tokens")
    
    # Indexes for performance
    __table_args__ = (
        Index('ix_refresh_tokens_user_id_not_revoked', 'user_id', 'is_revoked'),
        Index('ix_refresh_tokens_expires_at', 'expires_at'),
    )
    
    def is_valid(self) -> bool:
        """
        Check if token is valid (not revoked and not expired)
        
        Returns:
            bool: True if token is valid, False otherwise
        """
        if self.is_revoked:
            return False
        if self.expires_at < datetime.now(timezone.utc):
            return False
        return True
    
    def revoke(self):
        """Revoke this token"""
        self.is_revoked = True
    
    def __repr__(self):
        return f"<RefreshToken(id={self.id}, user_id={self.user_id}, revoked={self.is_revoked})>"
