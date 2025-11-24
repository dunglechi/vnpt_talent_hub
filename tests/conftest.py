"""
Shared pytest fixtures for all test modules.
"""
import os
import sys
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from app.main import app
from app.core.database import Base, get_db
from app.core.security import get_password_hash
# Import all models so they register with Base.metadata
from app.models.user import User, UserRole
from app.models.employee import Employee
from app.models.competency import Competency, CompetencyGroup
from app.models.career_path import CareerPath
from app.models.job import JobFamily
from app.models import career_path_competency, employee_competency  # Import modules to register tables

# Use file-based SQLite so tables persist across sessions
# Alternative: could use module-scoped engine but file is simpler
TEST_DATABASE_URL = "sqlite:///./test.db"
engine = create_engine(TEST_DATABASE_URL, connect_args={"check_same_thread": False})
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

@pytest.fixture(scope="function")
def db_session():
    """Provide a test database session for each test function."""
    # Create all tables before each test
    Base.metadata.create_all(bind=engine)
    
    session = TestingSessionLocal()
    try:
        yield session
    finally:
        # Rollback any uncommitted changes and close
        session.rollback()
        session.close()
        
        # Drop all tables after each test for isolation
        Base.metadata.drop_all(bind=engine)

@pytest.fixture(scope="function")
def client(db_session):
    """Provide a test client with overridden dependencies."""
    def override_get_db():
        try:
            yield db_session
        finally:
            pass
    
    def override_get_current_active_admin():
        # Mock admin user for authentication bypass
        return User(
            id=999, 
            email="testadmin@admin.com", 
            hashed_password="fake", 
            full_name="Test Admin",
            role=UserRole.ADMIN, 
            is_active=True,
            is_verified=True
        )
    
    from app.core.security import get_current_active_admin
    app.dependency_overrides[get_db] = override_get_db
    app.dependency_overrides[get_current_active_admin] = override_get_current_active_admin
    
    # Also override get_current_active_user for endpoints that use it
    from app.core.security import get_current_active_user
    app.dependency_overrides[get_current_active_user] = override_get_current_active_admin
    
    with TestClient(app) as test_client:
        yield test_client
    
    # Clear overrides after test
    app.dependency_overrides.clear()
