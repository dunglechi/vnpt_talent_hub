"""
Employee Service Layer
Business logic for employee operations
"""

from sqlalchemy.orm import Session, joinedload
from sqlalchemy import select
from typing import Optional, List, Dict
from app.models.employee import Employee
from app.models.competency import Competency, CompetencyGroup
from app.models.employee_competency import employee_competencies
from app.schemas.employee import EmployeeProfile, EmployeeCompetency


def _build_employee_profile_data(employee: Employee, db: Session) -> Dict:
    """
    Private helper function to build employee profile data dictionary.
    Constructs profile including competencies with proficiency levels.
    
    Args:
        employee: Employee ORM object (should have user and competencies loaded)
        db: Database session
        
    Returns:
        Dictionary with complete employee profile data
    """
    # Get proficiency levels from association table
    stmt = select(
        employee_competencies.c.competency_id,
        employee_competencies.c.proficiency_level
    ).where(employee_competencies.c.employee_id == employee.id)
    
    proficiency_map = {
        row.competency_id: row.proficiency_level 
        for row in db.execute(stmt).fetchall()
    }
    
    # Build competencies list with proficiency levels
    competencies_data = []
    for comp in employee.competencies:
        competencies_data.append({
            "id": comp.id,
            "name": comp.name,
            "code": comp.code,
            "domain": comp.group.name if comp.group else "Unknown",
            "proficiency_level": proficiency_map.get(comp.id, 0)
        })
    
    # Build and return profile data
    return {
        "id": employee.id,
        "user_id": employee.user_id,
        "department": employee.department,
        "job_title": employee.job_title,
        "manager_id": employee.manager_id,
        "email": employee.user.email,
        "competencies": competencies_data
    }


def get_employee_profile_by_user_id(db: Session, user_id: int) -> Optional[Dict]:
    """
    Get detailed employee profile including competencies with proficiency levels.
    
    Args:
        db: Database session
        user_id: User ID to look up employee
        
    Returns:
        Dictionary with employee profile data or None if not found
    """
    # Query employee with eager loading of user and competencies
    employee = db.query(Employee).options(
        joinedload(Employee.user),
        joinedload(Employee.competencies).joinedload(Competency.group)
    ).filter(Employee.user_id == user_id).first()
    
    if not employee:
        return None
    
    # Use helper function to build profile data
    return _build_employee_profile_data(employee, db)


def get_team_by_manager_id(db: Session, manager_id: int) -> List[Employee]:
    """
    Get all team members (employees) reporting to a specific manager.
    
    Args:
        db: Database session
        manager_id: Employee ID of the manager
        
    Returns:
        List of Employee objects with eager-loaded relationships
    """
    # Query employees where manager_id matches, with eager loading
    team_members = db.query(Employee).options(
        joinedload(Employee.user),
        joinedload(Employee.competencies).joinedload(Competency.group)
    ).filter(Employee.manager_id == manager_id).all()
    
    return team_members


def assign_competency_to_employee(
    db: Session, 
    employee_id: int, 
    competency_id: int, 
    proficiency_level: int
) -> bool:
    """
    Assign a competency with proficiency level to an employee.
    
    Args:
        db: Database session
        employee_id: Employee ID
        competency_id: Competency ID
        proficiency_level: Proficiency level (1-5)
        
    Returns:
        True if successful, False otherwise
    """
    if not (1 <= proficiency_level <= 5):
        return False
    
    # Check if assignment already exists
    stmt = select(employee_competencies).where(
        employee_competencies.c.employee_id == employee_id,
        employee_competencies.c.competency_id == competency_id
    )
    existing = db.execute(stmt).first()
    
    if existing:
        # Update proficiency level
        stmt = employee_competencies.update().where(
            employee_competencies.c.employee_id == employee_id,
            employee_competencies.c.competency_id == competency_id
        ).values(proficiency_level=proficiency_level)
        db.execute(stmt)
    else:
        # Insert new assignment
        stmt = employee_competencies.insert().values(
            employee_id=employee_id,
            competency_id=competency_id,
            proficiency_level=proficiency_level
        )
        db.execute(stmt)
    
    db.commit()
    return True


def remove_competency_from_employee(
    db: Session,
    employee_id: int,
    competency_id: int
) -> bool:
    """
    Remove a competency assignment from an employee.
    
    Args:
        db: Database session
        employee_id: Employee ID
        competency_id: Competency ID to remove
        
    Returns:
        True if a row was deleted (competency was assigned), False otherwise
    """
    # Execute DELETE on employee_competencies table
    stmt = employee_competencies.delete().where(
        employee_competencies.c.employee_id == employee_id,
        employee_competencies.c.competency_id == competency_id
    )
    result = db.execute(stmt)
    db.commit()
    
    # Return True if at least one row was deleted
    return result.rowcount > 0


def get_employee_competencies(db: Session, employee_id: int) -> List[Dict]:
    """
    Get all competencies for an employee with proficiency levels.
    
    Args:
        db: Database session
        employee_id: Employee ID
        
    Returns:
        List of competency dictionaries with proficiency levels
    """
    stmt = select(
        Competency,
        employee_competencies.c.proficiency_level,
        CompetencyGroup.name.label('group_name')
    ).join(
        employee_competencies,
        employee_competencies.c.competency_id == Competency.id
    ).join(
        CompetencyGroup,
        CompetencyGroup.id == Competency.group_id
    ).where(
        employee_competencies.c.employee_id == employee_id
    )
    
    results = db.execute(stmt).fetchall()
    
    competencies = []
    for comp, level, group_name in results:
        competencies.append({
            "id": comp.id,
            "name": comp.name,
            "code": comp.code,
            "domain": group_name,
            "proficiency_level": level
        })
    
    return competencies


def get_all_employees(db: Session, skip: int = 0, limit: int = 100) -> List[Employee]:
    """
    Get all employees in the organization with pagination.
    
    Args:
        db: Database session
        skip: Number of records to skip (for pagination)
        limit: Maximum number of records to return
        
    Returns:
        List of Employee objects with eager-loaded relationships
    """
    # Query all employees with eager loading, applying pagination
    employees = db.query(Employee).options(
        joinedload(Employee.user),
        joinedload(Employee.competencies).joinedload(Competency.group)
    ).offset(skip).limit(limit).all()
    
    return employees
