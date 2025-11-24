"""
Gap Analysis API endpoints
Compare employee competencies against career path requirements
"""

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.api.auth import get_current_active_user
from app.models.user import User, UserRole
from app.models.employee import Employee
from app.schemas.gap_analysis import GapAnalysisResponse
from app.services.gap_analysis_service import perform_gap_analysis

router = APIRouter()


@router.get(
    "/employee/{employee_id}/career-path/{career_path_id}",
    response_model=GapAnalysisResponse,
    summary="Perform gap analysis for employee against career path",
    description="""
    Compare an employee's current competencies and proficiency levels 
    against the requirements of a specific career path.
    
    **Authorization:**
    - Employee can view their own gap analysis
    - Manager can view their direct reports' gap analysis
    - Admin can view any employee's gap analysis
    """
)
def get_gap_analysis(
    employee_id: int,
    career_path_id: int,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """
    Perform gap analysis comparing employee's competencies against career path requirements.
    
    Returns detailed gap analysis including:
    - List of all required competencies with current vs required levels
    - Summary statistics (total, acquired, gaps, readiness percentage)
    - Career path details
    """
    # Fetch target employee to check authorization
    target_employee = db.query(Employee).filter(Employee.id == employee_id).first()
    
    if not target_employee:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Employee with ID {employee_id} not found"
        )
    
    # Authorization logic
    is_authorized = False
    
    # 1. Check if user is admin
    if current_user.role == UserRole.ADMIN:
        is_authorized = True
    
    # 2. Check if user is the employee themselves
    elif current_user.id == target_employee.user_id:
        is_authorized = True
    
    # 3. Check if user is the employee's manager
    else:
        # Get current user's employee record
        current_employee = db.query(Employee).filter(
            Employee.user_id == current_user.id
        ).first()
        
        if current_employee and target_employee.manager_id == current_employee.id:
            is_authorized = True
    
    if not is_authorized:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized to view this employee's gap analysis. "
                   "You must be the employee, their manager, or an admin."
        )
    
    # Perform gap analysis
    result = perform_gap_analysis(db, employee_id, career_path_id)
    
    if result is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Employee {employee_id} or Career Path {career_path_id} not found"
        )
    
    return result
