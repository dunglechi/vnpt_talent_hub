from pydantic import BaseModel, ConfigDict
from typing import Optional, List

class EmployeeCompetency(BaseModel):
    """Schema for employee's competency with proficiency level"""
    id: int
    name: str
    code: Optional[str] = None
    domain: str  # Group name (CORE/LEAD/FUNC)
    proficiency_level: int  # 1-5
    
    model_config = ConfigDict(from_attributes=True)


class EmployeeBase(BaseModel):
    user_id: int
    department: Optional[str] = None
    job_title: Optional[str] = None
    # Assuming 'manager_id' would be a link to another employee
    manager_id: Optional[int] = None

class EmployeeCreate(EmployeeBase):
    pass

class Employee(EmployeeBase):
    id: int
    
    model_config = ConfigDict(from_attributes=True)

# This schema will be used for the 'GET /employees/me' endpoint
class EmployeeProfile(Employee):
    email: str # Assuming we'll fetch this from the related User model
    competencies: List[EmployeeCompetency] = []
    # Add other profile-related fields as needed
