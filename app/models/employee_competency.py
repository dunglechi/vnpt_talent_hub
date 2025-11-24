"""
Employee Competency Association Table
Many-to-many relationship between Employee and Competency with proficiency level
"""

from sqlalchemy import Column, Integer, ForeignKey, Table
from app.core.database import Base

# Association table for Employee-Competency many-to-many relationship
employee_competencies = Table(
    'employee_competencies',
    Base.metadata,
    Column('employee_id', Integer, ForeignKey('employees.id'), primary_key=True),
    Column('competency_id', Integer, ForeignKey('competencies.id'), primary_key=True),
    Column('proficiency_level', Integer, nullable=False, comment='Proficiency level from 1 to 5')
)
