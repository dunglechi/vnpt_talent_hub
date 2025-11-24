"""
Employee database model
"""

from sqlalchemy import Column, Integer, String, ForeignKey
from sqlalchemy.orm import relationship
from app.core.database import Base
from app.models.employee_competency import employee_competencies

class Employee(Base):
    """
    Employee model
    Represents VNPT employees, linking to the User model.
    """
    __tablename__ = "employees"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), unique=True, nullable=False, index=True)
    department = Column(String, nullable=True)
    job_title = Column(String, nullable=True)
    
    # Self-referential relationship for manager-employee structure
    manager_id = Column(Integer, ForeignKey("employees.id"), nullable=True)

    # Relationships
    user = relationship("User", back_populates="employee")
    manager = relationship("Employee", remote_side=[id], back_populates="reports")
    reports = relationship("Employee", back_populates="manager")
    
    # Many-to-many relationship with Competency through association table
    competencies = relationship(
        "Competency",
        secondary=employee_competencies,
        back_populates="employees",
        lazy="selectin"
    )

