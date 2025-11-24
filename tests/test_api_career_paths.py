"""
Tests for Career Paths API filtering endpoints (Directive #16).
"""
import pytest
from app.models.career_path import CareerPath


@pytest.fixture
def seeded_db(db_session):
    """Seed the database with test data for career paths filtering tests."""
    career_paths_data = [
        {"job_family": "Engineering", "career_level": 1, "role_name": "Junior Engineer"},
        {"job_family": "Engineering", "career_level": 2, "role_name": "Senior Engineer"},
        {"job_family": "Management", "career_level": 3, "role_name": "Director"},
        {"job_family": "Management", "career_level": 4, "role_name": "VP"},
    ]
    
    for data in career_paths_data:
        cp = CareerPath(
            job_family=data["job_family"],
            career_level=data["career_level"],
            role_name=data["role_name"],
            description=f"Description for {data['role_name']}"
        )
        db_session.add(cp)
    
    db_session.commit()
    return db_session


def test_filter_role_name_match(client, seeded_db):
    """Test filtering career paths by role_name (case-insensitive substring match)."""
    r = client.get("/api/v1/career-paths?role_name=director")
    assert r.status_code == 200
    data = r.json()
    # Career paths endpoint returns a list, not {"data": [...]"}
    assert isinstance(data, list)
    assert len(data) == 1
    assert "director" in data[0]["role_name"].lower()


def test_filter_role_name_no_match(client, seeded_db):
    """Test filter that matches no career paths."""
    r = client.get("/api/v1/career-paths?role_name=zzz")
    assert r.status_code == 200
    data = r.json()
    assert len(data) == 0
