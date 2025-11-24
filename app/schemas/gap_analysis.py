"""
Pydantic schemas for Gap Analysis endpoints
"""

from typing import List, Optional
from pydantic import BaseModel, Field, ConfigDict


class GapAnalysisCompetency(BaseModel):
    """Competency gap analysis details"""
    id: int = Field(..., description="Competency ID")
    name: str = Field(..., description="Competency name")
    required_level: int = Field(..., ge=1, le=5, description="Required proficiency level for career path (1-5)")
    current_level: Optional[int] = Field(None, ge=0, le=5, description="Employee's current proficiency level (0 if not acquired)")
    gap: int = Field(..., description="Proficiency gap (required_level - current_level). Positive = needs improvement, Negative = exceeds requirement")
    
    model_config = ConfigDict(from_attributes=True)


class GapAnalysisResponse(BaseModel):
    """Complete gap analysis response"""
    employee_id: int = Field(..., description="Employee ID being analyzed")
    employee_name: str = Field(..., description="Employee full name")
    career_path_id: int = Field(..., description="Target career path ID")
    career_path_name: str = Field(..., description="Target career path role name")
    career_level: int = Field(..., description="Career path level")
    competency_gaps: List[GapAnalysisCompetency] = Field(..., description="List of competency gaps")
    summary: dict = Field(..., description="Summary statistics (total_competencies, acquired, not_acquired, avg_gap, etc.)")
    
    model_config = ConfigDict(from_attributes=True)
