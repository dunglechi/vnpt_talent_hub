"""Career Path - Competency Association Object"""
from sqlalchemy import Integer, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.core.database import Base


class CareerPathCompetency(Base):
    """Association object linking Career Paths to Competencies with required proficiency level."""
    __tablename__ = 'career_path_competencies'
    
    career_path_id: Mapped[int] = mapped_column(
        Integer, 
        ForeignKey('career_paths.id'), 
        primary_key=True
    )
    competency_id: Mapped[int] = mapped_column(
        Integer, 
        ForeignKey('competencies.id'), 
        primary_key=True
    )
    required_level: Mapped[int] = mapped_column(Integer, nullable=False)
    
    # Relationships to parent objects
    career_path: Mapped["CareerPath"] = relationship(back_populates="competency_links")
    competency: Mapped["Competency"] = relationship(back_populates="career_path_links")
