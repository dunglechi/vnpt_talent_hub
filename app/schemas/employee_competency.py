"""
Employee Competency Schemas
Pydantic models for employee competency assignment operations
"""

from pydantic import BaseModel, field_validator


class EmployeeCompetencyCreate(BaseModel):
    """
    Schema for creating/updating employee competency assignment.
    Used when an employee assigns a competency to themselves with a proficiency level.
    """
    competency_id: int
    proficiency_level: int
    
    @field_validator('proficiency_level')
    @classmethod
    def validate_proficiency_level(cls, v: int) -> int:
        """
        Validate that proficiency_level is between 1 and 5 (inclusive).
        
        Args:
            v: The proficiency level value to validate
            
        Returns:
            The validated proficiency level
            
        Raises:
            ValueError: If proficiency level is not between 1 and 5
        """
        if not (1 <= v <= 5):
            raise ValueError('proficiency_level must be between 1 and 5')
        return v
