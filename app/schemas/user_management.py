"""
Combined User-Employee management schemas for admin operations.
"""
from pydantic import BaseModel, EmailStr, Field, ConfigDict, field_validator
from typing import Optional
from datetime import datetime
from app.schemas.auth import validate_password_complexity


class UserEmployeeCreate(BaseModel):
    """Schema for creating a User and their Employee profile together."""
    # User fields
    email: EmailStr = Field(..., description="User email address")
    password: str = Field(..., min_length=8, max_length=100, description="Password: min 8 chars, uppercase, lowercase, digit, special char")
    full_name: str = Field(..., min_length=2, max_length=255, description="Full name")
    role: str = Field(default="employee", description="User role (admin/manager/employee)")
    
    # Employee fields
    department: Optional[str] = Field(None, description="Employee department")
    job_title: Optional[str] = Field(None, description="Employee job title")
    manager_id: Optional[int] = Field(None, description="Manager's employee ID")
    
    @field_validator('password')
    @classmethod
    def validate_password(cls, v: str) -> str:
        """Validate password complexity."""
        return validate_password_complexity(v)


class UserEmployeeUpdate(BaseModel):
    """Schema for updating a User and/or their Employee profile (all fields optional)."""
    # User fields
    email: Optional[EmailStr] = Field(None, description="User email address")
    password: Optional[str] = Field(None, min_length=8, max_length=100, description="New password: min 8 chars, uppercase, lowercase, digit, special char")
    full_name: Optional[str] = Field(None, min_length=2, max_length=255, description="Full name")
    role: Optional[str] = Field(None, description="User role (admin/manager/employee)")
    is_active: Optional[bool] = Field(None, description="User active status")
    
    # Employee fields
    department: Optional[str] = Field(None, description="Employee department")
    job_title: Optional[str] = Field(None, description="Employee job title")
    manager_id: Optional[int] = Field(None, description="Manager's employee ID")
    
    @field_validator('password')
    @classmethod
    def validate_password(cls, v: Optional[str]) -> Optional[str]:
        """Validate password complexity if provided."""
        if v is not None:
            return validate_password_complexity(v)
        return v


class EmployeeInfo(BaseModel):
    """Employee information in response."""
    id: int
    department: Optional[str] = None
    job_title: Optional[str] = None
    manager_id: Optional[int] = None
    
    model_config = ConfigDict(from_attributes=True)


class UserEmployeeResponse(BaseModel):
    """Combined User-Employee response schema."""
    id: int
    email: str
    full_name: str
    role: str
    is_active: bool
    is_verified: bool
    created_at: datetime
    last_login_at: Optional[datetime] = None
    employee: Optional[EmployeeInfo] = None
    
    model_config = ConfigDict(from_attributes=True)
