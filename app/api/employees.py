from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List

# Import dependencies, schemas, models, and services
from app.core.database import get_db
from app.models.user import User
from app.models.employee import Employee
from app.schemas.employee import EmployeeProfile
from app.schemas.employee_competency import EmployeeCompetencyCreate
from app.core.security import get_current_active_user
from app.api.auth import get_current_active_manager, get_current_active_admin
from app.services.employee_service import (
    get_employee_profile_by_user_id,
    get_team_by_manager_id,
    _build_employee_profile_data,
    assign_competency_to_employee,
    remove_competency_from_employee,
    get_all_employees
)

router = APIRouter()

@router.get("/", response_model=List[EmployeeProfile])
def list_all_employees(
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db),
    current_admin: User = Depends(get_current_active_admin)
):
    """
    Get all employees across the organization (Admin only).
    Supports pagination via skip and limit parameters.
    
    Args:
        skip: Number of records to skip (default: 0)
        limit: Maximum number of records to return (default: 100, max: 100)
        
    Returns:
        List of all employee profiles with competencies
        
    Raises:
        403: User does not have admin privileges
    """
    # Enforce max limit
    if limit > 100:
        limit = 100
    
    # Get all employees using service layer
    employees = get_all_employees(db, skip=skip, limit=limit)
    
    # Map to EmployeeProfile using helper function
    return [EmployeeProfile(**_build_employee_profile_data(emp, db)) for emp in employees]


@router.get("/{employee_id}", response_model=EmployeeProfile)
def get_employee_by_id(
    employee_id: int,
    db: Session = Depends(get_db),
    current_admin: User = Depends(get_current_active_admin)
):
    """
    Get a specific employee by their ID (Admin only).
    Admin can view any employee in the organization.
    
    Args:
        employee_id: ID of the employee to retrieve
        
    Returns:
        Employee profile with competencies
        
    Raises:
        403: User does not have admin privileges
        404: Employee not found
    """
    # Query for specific employee with eager loading
    from sqlalchemy.orm import joinedload
    from app.models.competency import Competency
    
    employee = db.query(Employee).options(
        joinedload(Employee.user),
        joinedload(Employee.competencies).joinedload(Competency.group)
    ).filter(Employee.id == employee_id).first()
    
    if not employee:
        raise HTTPException(
            status_code=404,
            detail="Employee not found"
        )
    
    # Use helper function to build profile data
    return EmployeeProfile(**_build_employee_profile_data(employee, db))


@router.get("/me", response_model=EmployeeProfile)
def read_current_employee_profile(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """
    Get the profile of the currently logged-in user.
    Includes all competencies with proficiency levels.
    """
    profile_data = get_employee_profile_by_user_id(db, current_user.id)
    
    if not profile_data:
        raise HTTPException(
            status_code=404, 
            detail="Employee profile not found for the current user."
        )
    
    return EmployeeProfile(**profile_data)


@router.get("/my-team", response_model=List[EmployeeProfile])
def read_manager_team(
    db: Session = Depends(get_db),
    current_manager: User = Depends(get_current_active_manager)
):
    """
    Get all team members reporting to the current manager.
    Includes all competencies with proficiency levels for each team member.
    
    Requires manager role.
    """
    # Get the manager's employee record
    manager_employee = db.query(Employee).filter(
        Employee.user_id == current_manager.id
    ).first()
    
    if not manager_employee:
        raise HTTPException(
            status_code=404,
            detail="Manager employee profile not found."
        )
    
    # Get all team members reporting to this manager
    team_members = get_team_by_manager_id(db, manager_employee.id)
    
    # Build profile data for each team member using helper function
    team_profiles = [
        _build_employee_profile_data(member, db)
        for member in team_members
    ]
    
    return [EmployeeProfile(**profile) for profile in team_profiles]


@router.post("/my-team/{employee_id}/competencies", response_model=EmployeeProfile)
def assign_competency_to_team_member(
    employee_id: int,
    competency_data: EmployeeCompetencyCreate,
    db: Session = Depends(get_db),
    current_manager: User = Depends(get_current_active_manager)
):
    """
    Assign or update a competency for a direct report.
    Manager can only assign competencies to employees in their team.
    
    Args:
        employee_id: ID of the team member employee
        competency_data: Contains competency_id and proficiency_level (1-5)
        
    Returns:
        Updated employee profile of the team member
        
    Raises:
        404: Manager profile not found OR target employee not found
        403: Target employee is not in manager's team
    """
    # Get the manager's employee record
    manager_employee = db.query(Employee).filter(
        Employee.user_id == current_manager.id
    ).first()
    
    if not manager_employee:
        raise HTTPException(
            status_code=404,
            detail="Manager employee profile not found."
        )
    
    # Get the target employee record
    target_employee = db.query(Employee).filter(
        Employee.id == employee_id
    ).first()
    
    if not target_employee:
        raise HTTPException(
            status_code=404,
            detail="Target employee not found"
        )
    
    # Verify target employee reports to this manager
    if target_employee.manager_id != manager_employee.id:
        raise HTTPException(
            status_code=403,
            detail="Forbidden: This employee is not in your team"
        )
    
    # Assign competency using service layer
    success = assign_competency_to_employee(
        db=db,
        employee_id=target_employee.id,
        competency_id=competency_data.competency_id,
        proficiency_level=competency_data.proficiency_level
    )
    
    if not success:
        raise HTTPException(
            status_code=400,
            detail="Failed to assign competency. Check that competency exists."
        )
    
    # Get and return updated profile of the team member
    return EmployeeProfile(**_build_employee_profile_data(target_employee, db))


@router.post("/me/competencies", response_model=EmployeeProfile)
def add_competency_to_current_employee(
    competency_data: EmployeeCompetencyCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """
    Assign a competency with proficiency level to the current employee.
    If the competency is already assigned, updates the proficiency level.
    
    Args:
        competency_data: Contains competency_id and proficiency_level (1-5)
        
    Returns:
        Updated employee profile with all competencies
    """
    # Get the employee record for current user
    employee = db.query(Employee).filter(
        Employee.user_id == current_user.id
    ).first()
    
    if not employee:
        raise HTTPException(
            status_code=404,
            detail="Employee profile not found for the current user."
        )
    
    # Assign competency using service layer
    success = assign_competency_to_employee(
        db=db,
        employee_id=employee.id,
        competency_id=competency_data.competency_id,
        proficiency_level=competency_data.proficiency_level
    )
    
    if not success:
        raise HTTPException(
            status_code=400,
            detail="Failed to assign competency. Check that competency exists."
        )
    
    # Get and return updated profile
    profile_data = get_employee_profile_by_user_id(db, current_user.id)
    return EmployeeProfile(**profile_data)


@router.delete("/me/competencies/{competency_id}", status_code=204)
def remove_competency_from_current_employee(
    competency_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """
    Remove a competency assignment from the current employee.
    
    Args:
        competency_id: ID of the competency to remove
        
    Returns:
        204 No Content on success
        
    Raises:
        404: If employee profile not found or competency not assigned to employee
    """
    # Get the employee record for current user
    employee = db.query(Employee).filter(
        Employee.user_id == current_user.id
    ).first()
    
    if not employee:
        raise HTTPException(
            status_code=404,
            detail="Employee profile not found for the current user."
        )
    
    # Remove competency using service layer
    success = remove_competency_from_employee(
        db=db,
        employee_id=employee.id,
        competency_id=competency_id
    )
    
    if not success:
        raise HTTPException(
            status_code=404,
            detail="Competency not found for this employee"
        )
    
    # Return 204 No Content (no response body)
    return None


@router.delete("/my-team/{employee_id}/competencies/{competency_id}", status_code=204)
def remove_competency_from_team_member(
    employee_id: int,
    competency_id: int,
    db: Session = Depends(get_db),
    current_manager: User = Depends(get_current_active_manager)
):
    """
    Remove a competency assignment from a direct report.
    Manager can only remove competencies from employees in their team.
    
    Args:
        employee_id: ID of the team member employee
        competency_id: ID of the competency to remove
        
    Returns:
        204 No Content on success
        
    Raises:
        404: Manager profile not found OR target employee not found OR competency not assigned
        403: Target employee is not in manager's team
    """
    # Layer 1: Manager role (via dependency - get_current_active_manager)
    
    # Layer 2: Get the manager's employee record
    manager_employee = db.query(Employee).filter(
        Employee.user_id == current_manager.id
    ).first()
    
    if not manager_employee:
        raise HTTPException(
            status_code=404,
            detail="Manager employee profile not found."
        )
    
    # Layer 3: Get the target employee record
    target_employee = db.query(Employee).filter(
        Employee.id == employee_id
    ).first()
    
    if not target_employee:
        raise HTTPException(
            status_code=404,
            detail="Target employee not found"
        )
    
    # Layer 4: Verify target employee reports to this manager
    if target_employee.manager_id != manager_employee.id:
        raise HTTPException(
            status_code=403,
            detail="Forbidden: This employee is not in your team"
        )
    
    # Remove competency using service layer
    success = remove_competency_from_employee(
        db=db,
        employee_id=target_employee.id,
        competency_id=competency_id
    )
    
    if not success:
        raise HTTPException(
            status_code=404,
            detail="Competency not found for this employee"
        )
    
    # Return 204 No Content (no response body)
    return None
