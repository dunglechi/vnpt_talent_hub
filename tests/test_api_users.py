"""
Tests for Users API filtering endpoints (Directive #16).
"""
import pytest
from app.models.user import User, UserRole
from app.models.employee import Employee
from app.core.security import get_password_hash


@pytest.fixture
def seeded_db(db_session):
    """Seed the database with test data for users filtering tests."""
    # Create 5 diverse users with employees
    users_data = [
        {"email": "nguyen.a@vnpt.vn", "full_name": "Nguyen Van A", "department": "Engineering"},
        {"email": "tran.b@vnpt.vn", "full_name": "Tran Thi B", "department": "Marketing"},
        {"email": "le.c@vnpt.vn", "full_name": "Le Van C", "department": "Engineering"},
        {"email": "pham.d@other.com", "full_name": "Pham Thi D", "department": "Sales"},
        {"email": "hoang.e@vnpt.vn", "full_name": "Hoang Van E", "department": "HR"},
    ]
    
    for data in users_data:
        user = User(
            email=data["email"],
            hashed_password=get_password_hash("password123"),
            full_name=data["full_name"],
            role=UserRole.EMPLOYEE,
            is_active=True,
            is_verified=True
        )
        db_session.add(user)
        db_session.flush()
        
        employee = Employee(user_id=user.id, department=data["department"], job_title="Engineer")
        db_session.add(employee)
    
    db_session.commit()
    return db_session


def test_filter_by_name(client, seeded_db):
    """Test filtering users by name (case-insensitive substring match)."""
    r = client.get("/api/v1/users/?name=nguyen")
    assert r.status_code == 200
    data = r.json()
    assert len(data) >= 1
    assert any("nguyen" in user["full_name"].lower() for user in data)


def test_filter_by_email(client, seeded_db):
    """Test filtering users by email (case-insensitive substring match)."""
    r = client.get("/api/v1/users/?email=@vnpt.vn")
    assert r.status_code == 200
    data = r.json()
    assert len(data) >= 4  # 4 users with @vnpt.vn
    assert all("@vnpt.vn" in user["email"].lower() for user in data)


def test_filter_by_department(client, seeded_db):
    """Test filtering users by department via employee join."""
    r = client.get("/api/v1/users/?department=engineering")
    assert r.status_code == 200
    data = r.json()
    assert len(data) == 2  # 2 users in Engineering
    for user in data:
        assert user["employee"] is not None
        assert "engineering" in user["employee"]["department"].lower()


def test_filter_combined_name_department(client, seeded_db):
    """Test combining multiple filters (name + department)."""
    r = client.get("/api/v1/users/?name=nguyen&department=engineering")
    assert r.status_code == 200
    data = r.json()
    assert len(data) == 1
    assert "nguyen" in data[0]["full_name"].lower()
    assert "engineering" in data[0]["employee"]["department"].lower()


def test_filter_no_results(client, seeded_db):
    """Test filter that matches no users."""
    r = client.get("/api/v1/users/?name=zzz")
    assert r.status_code == 200
    data = r.json()
    assert len(data) == 0


def test_pagination_with_filters(client, seeded_db):
    """Test that pagination works with filtering."""
    r = client.get("/api/v1/users/?email=@vnpt.vn&skip=0&limit=2")
    assert r.status_code == 200
    data = r.json()
    assert len(data) == 2  # Limited to 2 results
