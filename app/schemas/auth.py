"""
Authentication schemas for request/response validation.
"""
from pydantic import BaseModel, EmailStr, Field, ConfigDict, field_validator
from typing import Optional
from datetime import datetime
import re


def validate_password_complexity(password: str) -> str:
    """
    Validate password complexity requirements.
    
    Requirements:
    - Minimum 8 characters
    - At least one uppercase letter
    - At least one lowercase letter
    - At least one digit
    - At least one special character
    
    Args:
        password: Password to validate
        
    Returns:
        Password if valid
        
    Raises:
        ValueError: If password doesn't meet complexity requirements
    """
    if len(password) < 8:
        raise ValueError("Password must be at least 8 characters long")
    
    if not re.search(r"[A-Z]", password):
        raise ValueError("Password must contain at least one uppercase letter")
    
    if not re.search(r"[a-z]", password):
        raise ValueError("Password must contain at least one lowercase letter")
    
    if not re.search(r"\d", password):
        raise ValueError("Password must contain at least one digit")
    
    if not re.search(r"[!@#$%^&*(),.?\":{}|<>]", password):
        raise ValueError("Password must contain at least one special character (!@#$%^&*(),.?\":{}|<>)")
    
    return password


class UserRole:
    """User role constants."""
    ADMIN = "admin"
    MANAGER = "manager"
    EMPLOYEE = "employee"


# Request schemas
class LoginRequest(BaseModel):
    """Login request schema."""
    email: EmailStr = Field(..., description="User email address")
    password: str = Field(..., min_length=8, max_length=100, description="User password")
    
    @field_validator('password')
    @classmethod
    def validate_password(cls, v: str) -> str:
        """Validate password complexity."""
        return validate_password_complexity(v)


class RegisterRequest(BaseModel):
    """User registration request schema."""
    email: EmailStr = Field(..., description="User email address")
    password: str = Field(..., min_length=8, max_length=100, description="Password: min 8 chars, uppercase, lowercase, digit, special char")
    full_name: str = Field(..., min_length=2, max_length=255, description="Full name")
    role: Optional[str] = Field(default="employee", description="User role (admin/manager/employee)")
    
    @field_validator('password')
    @classmethod
    def validate_password(cls, v: str) -> str:
        """Validate password complexity."""
        return validate_password_complexity(v)


class PasswordChangeRequest(BaseModel):
    """Password change request schema."""
    current_password: str = Field(..., min_length=8, max_length=100)
    new_password: str = Field(..., min_length=8, max_length=100, description="New password: min 8 chars, uppercase, lowercase, digit, special char")
    
    @field_validator('new_password')
    @classmethod
    def validate_new_password(cls, v: str) -> str:
        """Validate new password complexity."""
        return validate_password_complexity(v)


class RefreshTokenRequest(BaseModel):
    """Refresh token request schema."""
    refresh_token: str = Field(..., description="Refresh token")


# Response schemas
class TokenResponse(BaseModel):
    """Token response schema."""
    access_token: str = Field(..., description="JWT access token")
    token_type: str = Field(default="bearer", description="Token type")


# Alias for compatibility
Token = TokenResponse


class UserCreate(BaseModel):
    """User creation schema."""
    email: EmailStr = Field(..., description="User email address")
    password: str = Field(..., min_length=8, max_length=100, description="Password: min 8 chars, uppercase, lowercase, digit, special char")
    full_name: str = Field(..., min_length=2, max_length=255, description="Full name")
    role: Optional[str] = Field(default="user", description="User role (user/admin/manager)")
    
    @field_validator('password')
    @classmethod
    def validate_password(cls, v: str) -> str:
        """Validate password complexity."""
        return validate_password_complexity(v)


class UserUpdate(BaseModel):
    """User update schema."""
    full_name: Optional[str] = Field(None, min_length=2, max_length=255, description="Full name")
    password: Optional[str] = Field(None, min_length=8, max_length=100, description="New password: min 8 chars, uppercase, lowercase, digit, special char")
    
    @field_validator('password')
    @classmethod
    def validate_password(cls, v: Optional[str]) -> Optional[str]:
        """Validate password complexity if provided."""
        if v is not None:
            return validate_password_complexity(v)
        return v


class UserResponse(BaseModel):
    """User response schema."""
    id: int
    email: str
    full_name: str
    role: str
    is_active: bool
    is_verified: bool
    created_at: datetime
    last_login_at: Optional[datetime] = None
    
    model_config = ConfigDict(from_attributes=True)


class UserCreateResponse(BaseModel):
    """User creation response schema."""
    user: UserResponse
    message: str = "User created successfully"


class LoginResponse(BaseModel):
    """Login response schema."""
    user: UserResponse
    tokens: TokenResponse
    message: str = "Login successful"


class MessageResponse(BaseModel):
    """Generic message response schema."""
    message: str
    success: bool = True
