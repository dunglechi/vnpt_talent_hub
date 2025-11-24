"""
Tests for Competencies API filtering endpoints (Directive #16).
"""
import pytest
from app.models.competency import Competency, CompetencyGroup


@pytest.fixture
def seeded_db(db_session):
    """Seed the database with test data for competencies filtering tests."""
    # Create competency groups
    group_core = CompetencyGroup(id=1, code="CORE", name="Core Competencies")
    group_tech = CompetencyGroup(id=2, code="TECH", name="Technical Competencies")
    db_session.add_all([group_core, group_tech])
    db_session.flush()
    
    # Create competencies
    competencies_data = [
        {"name": "Leadership", "code": "CORE-01", "group_id": 1},
        {"name": "Communication", "code": "CORE-02", "group_id": 1},
        {"name": "Python Programming", "code": "TECH-01", "group_id": 2},
        {"name": "System Design", "code": "TECH-02", "group_id": 2},
    ]
    
    for data in competencies_data:
        comp = Competency(
            name=data["name"],
            code=data["code"],
            group_id=data["group_id"],
            definition=f"Definition for {data['name']}"
        )
        db_session.add(comp)
    
    db_session.commit()
    return db_session


def test_filter_by_name(client, seeded_db):
    """Test filtering competencies by name (case-insensitive substring match)."""
    r = client.get("/api/v1/competencies?name=lead")
    assert r.status_code == 200
    data = r.json()
    assert "data" in data
    assert len(data["data"]) == 1
    assert "leadership" in data["data"][0]["name"].lower()
    assert data["meta"]["total"] == 1


def test_filter_by_group_code_and_name(client, seeded_db):
    """Test filtering by group_code and name combined."""
    r = client.get("/api/v1/competencies?group_code=CORE&name=lead")
    assert r.status_code == 200
    data = r.json()
    assert len(data["data"]) == 1
    assert data["data"][0]["group"]["code"] == "CORE"
    assert "leadership" in data["data"][0]["name"].lower()


def test_filter_no_match(client, seeded_db):
    """Test filter that matches no competencies."""
    r = client.get("/api/v1/competencies?name=zzz")
    assert r.status_code == 200
    data = r.json()
    assert len(data["data"]) == 0
    assert data["meta"]["total"] == 0
