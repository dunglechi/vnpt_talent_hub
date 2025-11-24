"""Career Path Service Layer
Business logic for career path operations
"""
from typing import List, Optional
from sqlalchemy.orm import Session, joinedload
from fastapi import HTTPException
from app.models.career_path import CareerPath
from app.models.career_path_competency import CareerPathCompetency
from app.models.competency import Competency
from app.schemas.career_path import (
    CareerPath as CareerPathSchema, 
    CareerPathCompetencyLink,
    CareerPathCreate,
    CareerPathUpdate
)


def get_all_career_paths(
    db: Session,
    skip: int = 0,
    limit: int = 100,
    role_name: Optional[str] = None
) -> List[CareerPathSchema]:
    """Return paginated list of career paths with optional role name filtering.

    Args:
        db: Session
        skip: Offset
        limit: Page size (capped at 100)
        role_name: Optional case-insensitive substring match on role_name
    """
    if limit > 100:
        limit = 100

    query = db.query(CareerPath).options(
        joinedload(CareerPath.competency_links).joinedload(CareerPathCompetency.competency)
    )

    if role_name:
        query = query.filter(CareerPath.role_name.ilike(f"%{role_name}%"))

    career_paths = query.offset(skip).limit(limit).all()
    return [_transform_to_schema(cp) for cp in career_paths]


def get_career_path_by_id(db: Session, path_id: int) -> Optional[CareerPathSchema]:
    """Return a single career path by its ID with eager-loaded competencies and required levels, or None if not found."""
    career_path = (
        db.query(CareerPath)
        .options(
            joinedload(CareerPath.competency_links).joinedload(CareerPathCompetency.competency)
        )
        .filter(CareerPath.id == path_id)
        .first()
    )
    
    if not career_path:
        return None
    
    return _transform_to_schema(career_path)


def _transform_to_schema(career_path: CareerPath) -> CareerPathSchema:
    """Transform CareerPath ORM object to Pydantic schema with CareerPathCompetencyLink objects."""
    competencies_with_levels = []
    
    for link in career_path.competency_links:
        comp = link.competency
        competencies_with_levels.append(
            CareerPathCompetencyLink(
                id=comp.id,
                name=comp.name,
                code=comp.code,
                definition=comp.definition,
                group_id=comp.group_id,
                job_family_id=comp.job_family_id,
                required_level=link.required_level
            )
        )
    
    return CareerPathSchema(
        id=career_path.id,
        job_family=career_path.job_family,
        career_level=career_path.career_level,
        role_name=career_path.role_name,
        description=career_path.description,
        competencies=competencies_with_levels
    )


# ===== CRUD Operations (Admin Only) =====

def create_career_path(db: Session, path_data: CareerPathCreate) -> CareerPath:
    """
    Create a new career path with associated competency links.
    
    Args:
        db: Database session
        path_data: CareerPathCreate schema with competencies list
        
    Returns:
        Created CareerPath ORM object with competency_links loaded
        
    Raises:
        HTTPException(400): If any competency_id doesn't exist
    """
    # Validate all competency IDs exist
    if path_data.competencies:
        competency_ids = [link.competency_id for link in path_data.competencies]
        existing_competencies = db.query(Competency.id).filter(
            Competency.id.in_(competency_ids)
        ).all()
        existing_ids = {comp.id for comp in existing_competencies}
        
        missing_ids = set(competency_ids) - existing_ids
        if missing_ids:
            raise HTTPException(
                status_code=400,
                detail=f"Competency IDs not found: {sorted(missing_ids)}"
            )
    
    # Create CareerPath
    career_path = CareerPath(
        job_family=path_data.job_family,
        career_level=path_data.career_level,
        role_name=path_data.role_name,
        description=path_data.description
    )
    db.add(career_path)
    db.flush()  # Get the ID without committing
    
    # Create competency links
    for link_data in path_data.competencies:
        link = CareerPathCompetency(
            career_path_id=career_path.id,
            competency_id=link_data.competency_id,
            required_level=link_data.required_level
        )
        db.add(link)
    
    db.commit()
    db.refresh(career_path)
    
    # Eager load competency_links for response
    db.refresh(career_path, ["competency_links"])
    
    return career_path


def update_career_path(db: Session, path_id: int, path_data: CareerPathUpdate) -> Optional[CareerPath]:
    """
    Update an existing career path with partial updates support.
    
    If competencies list is provided, it replaces all existing links (delete + create).
    This "replace" strategy is simpler and safer than patching.
    
    Args:
        db: Database session
        path_id: Career path ID
        path_data: CareerPathUpdate schema with optional fields
        
    Returns:
        Updated CareerPath ORM object, or None if not found
        
    Raises:
        HTTPException(400): If any competency_id doesn't exist
    """
    # Get existing career path
    career_path = db.query(CareerPath).filter(CareerPath.id == path_id).first()
    
    if not career_path:
        return None
    
    # Update basic fields (partial update)
    update_data = path_data.model_dump(exclude_unset=True, exclude={"competencies"})
    for field, value in update_data.items():
        setattr(career_path, field, value)
    
    # Handle competencies replacement if provided
    if path_data.competencies is not None:
        # Validate all competency IDs exist
        if path_data.competencies:
            competency_ids = [link.competency_id for link in path_data.competencies]
            existing_competencies = db.query(Competency.id).filter(
                Competency.id.in_(competency_ids)
            ).all()
            existing_ids = {comp.id for comp in existing_competencies}
            
            missing_ids = set(competency_ids) - existing_ids
            if missing_ids:
                raise HTTPException(
                    status_code=400,
                    detail=f"Competency IDs not found: {sorted(missing_ids)}"
                )
        
        # Delete all existing links (cascade will handle this cleanly)
        db.query(CareerPathCompetency).filter(
            CareerPathCompetency.career_path_id == path_id
        ).delete()
        
        # Create new links
        for link_data in path_data.competencies:
            link = CareerPathCompetency(
                career_path_id=path_id,
                competency_id=link_data.competency_id,
                required_level=link_data.required_level
            )
            db.add(link)
    
    db.commit()
    db.refresh(career_path)
    
    # Eager load competency_links for response
    db.refresh(career_path, ["competency_links"])
    
    return career_path


def delete_career_path(db: Session, path_id: int) -> bool:
    """
    Delete a career path and its associated competency links.
    
    The cascade="all, delete-orphan" configuration in the CareerPath model
    will automatically delete associated CareerPathCompetency records.
    
    Args:
        db: Database session
        path_id: Career path ID
        
    Returns:
        True if deleted successfully
        
    Raises:
        HTTPException(404): If career path not found
    """
    career_path = db.query(CareerPath).filter(CareerPath.id == path_id).first()
    
    if not career_path:
        raise HTTPException(
            status_code=404,
            detail=f"Career path with id {path_id} not found"
        )
    
    db.delete(career_path)
    db.commit()
    
    return True
