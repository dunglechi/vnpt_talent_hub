"""
Career Path database model
"""
from sqlalchemy import Column, Integer, String, Text
from sqlalchemy.orm import relationship
from sqlalchemy.ext.associationproxy import association_proxy
from app.core.database import Base


class CareerPath(Base):
    """
    Career Path model
    Represents a potential career progression path within the organization.
    """
    __tablename__ = "career_paths"

    id = Column(Integer, primary_key=True, index=True)
    job_family = Column(String, index=True, nullable=False)
    career_level = Column(Integer, nullable=False)
    role_name = Column(String, nullable=False)
    description = Column(Text, nullable=True)
    
    # Relationship to association object (for accessing required_level)
    competency_links = relationship(
        "CareerPathCompetency",
        back_populates="career_path",
        cascade="all, delete-orphan"
    )
    
    # Association proxy for convenient access to competencies
    competencies = association_proxy(
        "competency_links",
        "competency",
        creator=lambda comp: __import__('app.models.career_path_competency', fromlist=['CareerPathCompetency']).CareerPathCompetency(competency=comp)
    )
