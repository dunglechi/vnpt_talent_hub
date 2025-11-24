"""
Competency-related database models
"""

from sqlalchemy import Column, Integer, String, Text, ForeignKey
from sqlalchemy.orm import relationship
from sqlalchemy.ext.associationproxy import association_proxy
from app.core.database import Base
from app.models.employee_competency import employee_competencies


class CompetencyGroup(Base):
    """
    Competency Group model
    Represents main categories: CORE, LEAD, FUNC
    """
    __tablename__ = "competency_groups"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, unique=True, index=True)
    code = Column(String, unique=True, index=True)

    # Relationships
    competencies = relationship("Competency", back_populates="group")


class Competency(Base):
    """
    Competency model
    Represents individual competencies with 5 proficiency levels
    """
    __tablename__ = "competencies"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String)
    code = Column(String, nullable=True)
    definition = Column(Text)
    group_id = Column(Integer, ForeignKey("competency_groups.id"))
    job_family_id = Column(Integer, ForeignKey("job_families.id"), nullable=True)

    # Relationships
    group = relationship("CompetencyGroup", back_populates="competencies")
    job_family = relationship("JobFamily", back_populates="competencies")
    levels = relationship("CompetencyLevel", back_populates="competency")
    
    # Many-to-many relationship with Employee through association table
    employees = relationship(
        "Employee",
        secondary=employee_competencies,
        back_populates="competencies"
    )
    
    # Relationship to association object (for accessing required_level)
    career_path_links = relationship(
        "CareerPathCompetency",
        back_populates="competency",
        cascade="all, delete-orphan"
    )
    
    # Association proxy for convenient access to career paths
    career_paths = association_proxy(
        "career_path_links",
        "career_path",
        creator=lambda path: __import__('app.models.career_path_competency', fromlist=['CareerPathCompetency']).CareerPathCompetency(career_path=path)
    )


class CompetencyLevel(Base):
    """
    Competency Level model
    Represents 5 proficiency levels (1-5) for each competency
    """
    __tablename__ = "competency_levels"

    id = Column(Integer, primary_key=True, index=True)
    level = Column(Integer)
    description = Column(Text)
    competency_id = Column(Integer, ForeignKey("competencies.id"))

    # Relationships
    competency = relationship("Competency", back_populates="levels")
