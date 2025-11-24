"""
Gap Analysis Service Layer
Business logic for comparing employee competencies against career path requirements
"""

from typing import Optional
from sqlalchemy.orm import Session, joinedload
from sqlalchemy import select
from app.models.employee import Employee
from app.models.career_path import CareerPath
from app.models.career_path_competency import CareerPathCompetency
from app.models.employee_competency import employee_competencies


def perform_gap_analysis(
    db: Session, 
    employee_id: int, 
    career_path_id: int
) -> Optional[dict]:
    """
    Perform gap analysis comparing employee's current competencies 
    against career path requirements.
    
    Args:
        db: Database session
        employee_id: ID of employee to analyze
        career_path_id: ID of target career path
    
    Returns:
        Dictionary structured for GapAnalysisResponse schema, or None if employee/path not found
    """
    # Fetch employee with user relationship
    employee = db.query(Employee).options(
        joinedload(Employee.user)
    ).filter(Employee.id == employee_id).first()
    
    if not employee:
        return None
    
    # Fetch career path with competency links
    career_path = db.query(CareerPath).options(
        joinedload(CareerPath.competency_links).joinedload(CareerPathCompetency.competency)
    ).filter(CareerPath.id == career_path_id).first()
    
    if not career_path:
        return None
    
    # Build employee's competency map: {competency_id: proficiency_level}
    employee_comp_map = {}
    stmt = select(
        employee_competencies.c.competency_id,
        employee_competencies.c.proficiency_level
    ).where(employee_competencies.c.employee_id == employee_id)
    
    result = db.execute(stmt)
    for row in result:
        employee_comp_map[row.competency_id] = row.proficiency_level
    
    # Analyze each required competency
    competency_gaps = []
    total_gap = 0
    acquired_count = 0
    exceeds_count = 0
    
    for link in career_path.competency_links:
        competency = link.competency
        required_level = link.required_level
        current_level = employee_comp_map.get(competency.id, 0)  # 0 if not acquired
        gap = required_level - current_level
        
        competency_gaps.append({
            "id": competency.id,
            "name": competency.name,
            "required_level": required_level,
            "current_level": current_level if current_level > 0 else None,
            "gap": gap
        })
        
        total_gap += gap
        if current_level > 0:
            acquired_count += 1
        if gap < 0:  # Employee exceeds requirement
            exceeds_count += 1
    
    total_competencies = len(career_path.competency_links)
    not_acquired_count = total_competencies - acquired_count
    avg_gap = total_gap / total_competencies if total_competencies > 0 else 0
    
    # Calculate readiness percentage (0-100%)
    # Formula: competencies where current >= required / total competencies
    ready_count = sum(1 for gap_data in competency_gaps if gap_data["gap"] <= 0)
    readiness_percentage = (ready_count / total_competencies * 100) if total_competencies > 0 else 0
    
    return {
        "employee_id": employee.id,
        "employee_name": employee.user.full_name,
        "career_path_id": career_path.id,
        "career_path_name": career_path.role_name,
        "career_level": career_path.career_level,
        "competency_gaps": competency_gaps,
        "summary": {
            "total_competencies": total_competencies,
            "acquired_competencies": acquired_count,
            "not_acquired_competencies": not_acquired_count,
            "competencies_exceeding_requirement": exceeds_count,
            "average_gap": round(avg_gap, 2),
            "readiness_percentage": round(readiness_percentage, 2),
            "ready_for_role": readiness_percentage >= 80  # 80% threshold
        }
    }
