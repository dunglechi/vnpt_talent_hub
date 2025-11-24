"""
Job structure database models
"""

from sqlalchemy import Column, Integer, String, ForeignKey
from sqlalchemy.orm import relationship
from app.core.database import Base


class JobBlock(Base):
    """
    Job Block model
    Highest level in job hierarchy (e.g., Technology, Operations)
    """
    __tablename__ = "job_blocks"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, unique=True)

    # Relationships
    families = relationship("JobFamily", back_populates="block")


class JobFamily(Base):
    """
    Job Family model
    Second level in job hierarchy (e.g., Software Development, Network Engineering)
    """
    __tablename__ = "job_families"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String)
    block_id = Column(Integer, ForeignKey("job_blocks.id"))

    # Relationships
    block = relationship("JobBlock", back_populates="families")
    sub_families = relationship("JobSubFamily", back_populates="family")
    competencies = relationship("Competency", back_populates="job_family")


class JobSubFamily(Base):
    """
    Job Sub-Family model
    Third level in job hierarchy (e.g., Backend Developer, Frontend Developer)
    """
    __tablename__ = "job_sub_families"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String)
    family_id = Column(Integer, ForeignKey("job_families.id"))

    # Relationships
    family = relationship("JobFamily", back_populates="sub_families")
