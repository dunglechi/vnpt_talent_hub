"""add_performance_indexes_for_filtering

Revision ID: d89c08ecc206
Revises: 813b74e37740
Create Date: 2025-11-23 14:23:48.311315

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'd89c08ecc206'
down_revision: Union[str, Sequence[str], None] = '813b74e37740'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """
    Add performance indexes for filtering operations.
    
    These indexes improve query performance for:
    - User filtering by full_name, email
    - Employee filtering by department
    - Competency filtering by name
    - Career path filtering by role_name
    """
    # Index for users table - full_name filtering
    op.create_index(
        'idx_users_full_name',
        'users',
        ['full_name'],
        unique=False
    )
    
    # Index for users table - email filtering (already unique, but explicit index improves performance)
    op.create_index(
        'idx_users_email',
        'users',
        ['email'],
        unique=False
    )
    
    # Index for employees table - department filtering
    op.create_index(
        'idx_employees_department',
        'employees',
        ['department'],
        unique=False
    )
    
    # Index for competencies table - name filtering
    op.create_index(
        'idx_competencies_name',
        'competencies',
        ['name'],
        unique=False
    )
    
    # Index for career_paths table - role_name filtering
    op.create_index(
        'idx_career_paths_role_name',
        'career_paths',
        ['role_name'],
        unique=False
    )
    
    # Composite index for common combined filters (name + department on users)
    op.create_index(
        'idx_users_name_dept',
        'users',
        ['full_name', 'email'],
        unique=False
    )


def downgrade() -> None:
    """Remove performance indexes."""
    # Drop indexes in reverse order
    op.drop_index('idx_users_name_dept', table_name='users')
    op.drop_index('idx_career_paths_role_name', table_name='career_paths')
    op.drop_index('idx_competencies_name', table_name='competencies')
    op.drop_index('idx_employees_department', table_name='employees')
    op.drop_index('idx_users_email', table_name='users')
    op.drop_index('idx_users_full_name', table_name='users')
