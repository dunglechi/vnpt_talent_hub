"""
Competency Service Layer
Business logic for competency and competency group CRUD operations
"""

from typing import Optional, List, Tuple
from sqlalchemy.orm import Session, joinedload
from sqlalchemy import select
from fastapi import HTTPException, status

from app.models.competency import Competency, CompetencyGroup
from app.models.employee_competency import employee_competencies
from app.schemas.competency import (
    CompetencyCreate, 
    CompetencyUpdate,
    CompetencyGroupCreate,
    CompetencyGroupUpdate
)


# ==================== Competency CRUD ====================

def create_competency(db: Session, competency_data: CompetencyCreate) -> Competency:
    """
    Create a new competency.
    
    Args:
        db: Database session
        competency_data: Competency creation data
    
    Returns:
        Created Competency object
    
    Raises:
        HTTPException: If group_id or job_family_id is invalid
    """
    # Validate group exists
    group = db.query(CompetencyGroup).filter(
        CompetencyGroup.id == competency_data.group_id
    ).first()
    
    if not group:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Competency group with ID {competency_data.group_id} not found"
        )
    
    # Create competency
    competency = Competency(
        name=competency_data.name,
        code=competency_data.code,
        definition=competency_data.definition,
        group_id=competency_data.group_id,
        job_family_id=competency_data.job_family_id
    )
    
    db.add(competency)
    db.commit()
    db.refresh(competency)
    
    return competency


def update_competency(
    db: Session, 
    competency_id: int, 
    competency_data: CompetencyUpdate
) -> Optional[Competency]:
    """
    Update an existing competency.
    
    Args:
        db: Database session
        competency_id: ID of competency to update
        competency_data: Competency update data (partial)
    
    Returns:
        Updated Competency object, or None if not found
    
    Raises:
        HTTPException: If referenced group_id is invalid
    """
    competency = db.query(Competency).filter(Competency.id == competency_id).first()
    
    if not competency:
        return None
    
    # Validate group_id if provided
    if competency_data.group_id is not None:
        group = db.query(CompetencyGroup).filter(
            CompetencyGroup.id == competency_data.group_id
        ).first()
        
        if not group:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Competency group with ID {competency_data.group_id} not found"
            )
    
    # Update fields (only non-None values)
    update_data = competency_data.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(competency, field, value)
    
    db.commit()
    db.refresh(competency)
    
    return competency


def delete_competency(db: Session, competency_id: int) -> bool:
    """
    Delete a competency if not in use.
    
    Args:
        db: Database session
        competency_id: ID of competency to delete
    
    Returns:
        True if deleted successfully
    
    Raises:
        HTTPException: If competency is in use by employees or career paths,
                      or if competency not found
    """
    competency = db.query(Competency).filter(Competency.id == competency_id).first()
    
    if not competency:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Competency with ID {competency_id} not found"
        )
    
    # Check if competency is used by any employees
    stmt = select(employee_competencies.c.employee_id).where(
        employee_competencies.c.competency_id == competency_id
    ).limit(1)
    
    employee_usage = db.execute(stmt).first()
    
    if employee_usage:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Cannot delete competency '{competency.name}'. "
                   f"It is currently assigned to one or more employees. "
                   f"Remove all employee associations before deleting."
        )
    
    # Check if competency is used in any career paths
    if len(competency.career_path_links) > 0:
        career_path_names = [link.career_path.role_name for link in competency.career_path_links]
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Cannot delete competency '{competency.name}'. "
                   f"It is required by career paths: {', '.join(career_path_names[:3])}. "
                   f"Remove from all career paths before deleting."
        )
    
    # Safe to delete
    db.delete(competency)
    db.commit()
    
    return True


# ==================== CompetencyGroup CRUD ====================

def create_competency_group(
    db: Session, 
    group_data: CompetencyGroupCreate
) -> CompetencyGroup:
    """
    Create a new competency group.
    
    Args:
        db: Database session
        group_data: Competency group creation data
    
    Returns:
        Created CompetencyGroup object
    
    Raises:
        HTTPException: If group with same name or code already exists
    """
    # Check for duplicate name or code
    existing = db.query(CompetencyGroup).filter(
        (CompetencyGroup.name == group_data.name) | 
        (CompetencyGroup.code == group_data.code)
    ).first()
    
    if existing:
        if existing.name == group_data.name:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Competency group with name '{group_data.name}' already exists"
            )
        else:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Competency group with code '{group_data.code}' already exists"
            )
    
    # Create group
    group = CompetencyGroup(
        name=group_data.name,
        code=group_data.code
    )
    
    db.add(group)
    db.commit()
    db.refresh(group)
    
    return group


def update_competency_group(
    db: Session,
    group_id: int,
    group_data: CompetencyGroupUpdate
) -> Optional[CompetencyGroup]:
    """
    Update an existing competency group.
    
    Args:
        db: Database session
        group_id: ID of competency group to update
        group_data: Competency group update data (partial)
    
    Returns:
        Updated CompetencyGroup object, or None if not found
    
    Raises:
        HTTPException: If updated name or code conflicts with existing group
    """
    group = db.query(CompetencyGroup).filter(CompetencyGroup.id == group_id).first()
    
    if not group:
        return None
    
    # Check for conflicts if name or code is being updated
    update_data = group_data.model_dump(exclude_unset=True)
    
    if 'name' in update_data or 'code' in update_data:
        query = db.query(CompetencyGroup).filter(CompetencyGroup.id != group_id)
        
        if 'name' in update_data:
            query = query.filter(CompetencyGroup.name == update_data['name'])
        if 'code' in update_data:
            query = query.filter(CompetencyGroup.code == update_data['code'])
        
        conflict = query.first()
        
        if conflict:
            if 'name' in update_data and conflict.name == update_data['name']:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail=f"Competency group with name '{update_data['name']}' already exists"
                )
            if 'code' in update_data and conflict.code == update_data['code']:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail=f"Competency group with code '{update_data['code']}' already exists"
                )
    
    # Update fields
    for field, value in update_data.items():
        setattr(group, field, value)
    
    db.commit()
    db.refresh(group)
    
    return group


def delete_competency_group(db: Session, group_id: int) -> bool:
    """
    Delete a competency group if not in use.
    
    Args:
        db: Database session
        group_id: ID of competency group to delete
    
    Returns:
        True if deleted successfully
    
    Raises:
        HTTPException: If group has associated competencies or if not found
    """
    group = db.query(CompetencyGroup).filter(CompetencyGroup.id == group_id).first()
    
    if not group:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Competency group with ID {group_id} not found"
        )
    
    # Check if group has any competencies
    competency_count = db.query(Competency).filter(
        Competency.group_id == group_id
    ).count()
    
    if competency_count > 0:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Cannot delete competency group '{group.name}'. "
                   f"It has {competency_count} associated competencies. "
                   f"Delete or reassign all competencies before deleting the group."
        )
    
    # Safe to delete
    db.delete(group)
    db.commit()
    
    return True


# ==================== Listing / Retrieval Helpers ====================

def get_competencies(
    db: Session,
    skip: int = 0,
    limit: int = 100,
    group_code: Optional[str] = None,
    name: Optional[str] = None,
    include_levels: bool = True
) -> Tuple[List[Competency], int]:
    """Return a filtered, paginated list of competencies plus total count.

    Filtering rules:
    - group_code: Exact match against CompetencyGroup.code (case-insensitive)
    - name: Case-insensitive substring match on Competency.name
    - include_levels: Eager load level relationship when True

    Args:
        db: Database session
        skip: Number of records to skip (offset)
        limit: Max number of records to return (capped at 1000)
        group_code: Optional group code filter (CORE/LEAD/FUNC)
        name: Optional substring filter on competency name
        include_levels: Whether to eager load competency levels

    Returns:
        (competencies, total_count)
    """
    if limit > 1000:
        limit = 1000

    query = db.query(Competency)

    if group_code:
        query = query.join(CompetencyGroup).filter(CompetencyGroup.code == group_code.upper())

    if name:
        query = query.filter(Competency.name.ilike(f"%{name}%"))

    # Eager loading
    if include_levels:
        query = query.options(joinedload(Competency.levels))
    query = query.options(joinedload(Competency.group))
    query = query.options(joinedload(Competency.job_family))

    total = query.count()
    items = query.offset(skip).limit(limit).all()
    return items, total
