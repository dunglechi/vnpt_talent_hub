from pydantic import BaseModel, ConfigDict, Field
from typing import List, Optional, TYPE_CHECKING

# Use TYPE_CHECKING to avoid circular imports at runtime
if TYPE_CHECKING:
    from app.schemas.competency import CompetencyInDB

class CareerPathBase(BaseModel):
    job_family: str
    career_level: int
    role_name: str
    description: Optional[str] = None

class CareerPathCompetencyLinkCreate(BaseModel):
    """Schema for creating competency links with required proficiency level"""
    competency_id: int = Field(..., description="ID of the competency")
    required_level: int = Field(..., ge=1, le=5, description="Required proficiency level (1-5)")

class CareerPathCreate(CareerPathBase):
    competencies: List[CareerPathCompetencyLinkCreate] = Field(
        default=[],
        description="List of competencies with required proficiency levels"
    )

class CareerPathUpdate(BaseModel):
    """Schema for updating a career path (all fields optional for partial updates)"""
    job_family: Optional[str] = None
    career_level: Optional[int] = None
    role_name: Optional[str] = None
    description: Optional[str] = None
    competencies: Optional[List[CareerPathCompetencyLinkCreate]] = Field(
        default=None,
        description="Optional list of competencies to replace existing ones"
    )

class CareerPathCompetencyLink(BaseModel):
    """Competency with its required proficiency level for a career path"""
    id: int
    name: str
    code: Optional[str] = None
    definition: str
    group_id: int
    job_family_id: Optional[int] = None
    required_level: int = Field(..., ge=1, le=5, description="Required proficiency level (1-5)")
    
    model_config = ConfigDict(from_attributes=True)

class CareerPath(CareerPathBase):
    id: int
    
    # List of competencies with their required proficiency levels
    competencies: List[CareerPathCompetencyLink] = []

    model_config = ConfigDict(from_attributes=True)

# Import CompetencyInDB for potential future use
from app.schemas.competency import CompetencyInDB
CareerPath.model_rebuild()
