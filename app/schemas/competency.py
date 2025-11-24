"""
Pydantic schemas for Competency-related endpoints
"""

from typing import List, Optional
from pydantic import BaseModel, Field, ConfigDict

# CompetencyLevel schemas
class CompetencyLevelResponse(BaseModel):
    """Competency level response model"""
    id: int
    level: int = Field(..., ge=1, le=5, description="Proficiency level (1-5)")
    description: str
    competency_id: int
    
    model_config = ConfigDict(from_attributes=True)

# CompetencyGroup schemas
class CompetencyGroupBase(BaseModel):
    """Base competency group model"""
    name: str = Field(..., min_length=1, max_length=100)
    code: str = Field(..., min_length=1, max_length=50, description="CORE, LEAD, or FUNC")

class CompetencyGroupCreate(CompetencyGroupBase):
    """Schema for creating a new competency group"""
    pass

class CompetencyGroupUpdate(BaseModel):
    """Schema for updating a competency group (all fields optional)"""
    name: Optional[str] = Field(None, min_length=1, max_length=100)
    code: Optional[str] = Field(None, min_length=1, max_length=50)

class CompetencyGroupResponse(BaseModel):
    """Competency group response model"""
    id: int
    name: str
    code: str = Field(..., description="CORE, LEAD, or FUNC")
    
    model_config = ConfigDict(from_attributes=True)

# JobFamily schemas (minimal)
class JobFamilyResponse(BaseModel):
    """Job family response model"""
    id: int
    name: str
    
    model_config = ConfigDict(from_attributes=True)

# Competency schemas
class CompetencyBase(BaseModel):
    """Base competency model"""
    name: str = Field(..., min_length=1, max_length=200)
    code: Optional[str] = Field(None, max_length=50)
    definition: str = Field(..., min_length=1)
    group_id: int
    job_family_id: Optional[int] = None

class CompetencyCreate(CompetencyBase):
    """Schema for creating a new competency"""
    pass

class CompetencyUpdate(BaseModel):
    """Schema for updating a competency (all fields optional)"""
    name: Optional[str] = Field(None, min_length=1, max_length=200)
    code: Optional[str] = Field(None, max_length=50)
    definition: Optional[str] = Field(None, min_length=1)
    group_id: Optional[int] = None
    job_family_id: Optional[int] = None

class CompetencyInDB(CompetencyBase):
    """Competency with ID (from database)"""
    id: int
    group: CompetencyGroupResponse
    job_family: Optional[JobFamilyResponse] = None
    levels: List[CompetencyLevelResponse] = []
    
    model_config = ConfigDict(from_attributes=True)

# Response schemas
class CompetencyResponse(BaseModel):
    """Single competency response"""
    success: bool = True
    data: CompetencyInDB

class CompetencyListResponse(BaseModel):
    """List of competencies response"""
    success: bool = True
    data: List[CompetencyInDB]
    meta: dict = Field(..., description="Pagination and filter metadata")
