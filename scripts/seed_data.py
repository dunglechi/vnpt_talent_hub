"""Seed script for Career Paths and their competency relationships

This script creates sample career path records and links them with existing competencies.
It is idempotent - safe to run multiple times without creating duplicates.

Usage:
    python scripts/seed_data.py
"""
from sqlalchemy import create_engine
from sqlalchemy.orm import Session
from app.core.database import SQLALCHEMY_DATABASE_URL
from app.models.career_path import CareerPath
from app.models.career_path_competency import CareerPathCompetency
from app.models.competency import Competency


def seed_career_paths(db: Session):
    """Create sample career path records with competency relationships and required levels"""
    
    # Define sample career paths with required proficiency levels
    sample_paths = [
        {
            "job_family": "Technical",
            "career_level": 1,
            "role_name": "Junior Developer",
            "description": "Entry-level software developer focusing on code implementation and learning",
            "competencies": [
                {"name": "1. Định hướng mục tiêu và kết quả (Goal and Result Orientation)", "required_level": 2},
                {"name": "2. Giao tiếp và thuyết trình (Communication and Presentation)", "required_level": 2},
            ]
        },
        {
            "job_family": "Technical",
            "career_level": 2,
            "role_name": "Senior Developer",
            "description": "Experienced developer with system design skills and mentoring capabilities",
            "competencies": [
                {"name": "1. Định hướng mục tiêu và kết quả (Goal and Result Orientation)", "required_level": 3},
                {"name": "2. Giao tiếp và thuyết trình (Communication and Presentation)", "required_level": 3},
                {"name": "3. Lan tỏa văn hóa VNPT (VNPT culture inspiration)", "required_level": 3},
            ]
        },
        {
            "job_family": "Technical",
            "career_level": 3,
            "role_name": "Tech Lead",
            "description": "Technical leader responsible for architecture decisions and team guidance",
            "competencies": [
                {"name": "1. Định hướng mục tiêu và kết quả (Goal and Result Orientation)", "required_level": 4},
                {"name": "2. Giao tiếp và thuyết trình (Communication and Presentation)", "required_level": 4},
                {"name": "3. Lan tỏa văn hóa VNPT (VNPT culture inspiration)", "required_level": 3},
                {"name": "4. Hợp tác (Collaboration)", "required_level": 4},
            ]
        },
        {
            "job_family": "Management",
            "career_level": 2,
            "role_name": "Engineering Manager",
            "description": "Manages engineering teams, handles resource allocation and people development",
            "competencies": [
                {"name": "1. Định hướng mục tiêu và kết quả (Goal and Result Orientation)", "required_level": 4},
                {"name": "2. Giao tiếp và thuyết trình (Communication and Presentation)", "required_level": 4},
                {"name": "3. Lan tỏa văn hóa VNPT (VNPT culture inspiration)", "required_level": 4},
                {"name": "4. Hợp tác (Collaboration)", "required_level": 4},
                {"name": "5. Phát triển bản thân (Self-development)", "required_level": 3},
            ]
        },
        {
            "job_family": "Management",
            "career_level": 3,
            "role_name": "Director of Engineering",
            "description": "Senior leadership role overseeing multiple engineering teams and strategic initiatives",
            "competencies": [
                {"name": "1. Định hướng mục tiêu và kết quả (Goal and Result Orientation)", "required_level": 5},
                {"name": "2. Giao tiếp và thuyết trình (Communication and Presentation)", "required_level": 5},
                {"name": "3. Lan tỏa văn hóa VNPT (VNPT culture inspiration)", "required_level": 5},
                {"name": "4. Hợp tác (Collaboration)", "required_level": 5},
                {"name": "5. Phát triển bản thân (Self-development)", "required_level": 4},
            ]
        }
    ]
    
    print("Starting career path seeding...")
    
    for path_data in sample_paths:
        # Check if path already exists (idempotency)
        existing = db.query(CareerPath).filter(
            CareerPath.job_family == path_data["job_family"],
            CareerPath.career_level == path_data["career_level"],
            CareerPath.role_name == path_data["role_name"]
        ).first()
        
        if existing:
            print(f"✓ Career path '{path_data['role_name']}' already exists, skipping...")
            continue
        
        # Create new career path
        career_path = CareerPath(
            job_family=path_data["job_family"],
            career_level=path_data["career_level"],
            role_name=path_data["role_name"],
            description=path_data["description"]
        )
        
        # Add career path first to get ID
        db.add(career_path)
        db.flush()  # Get ID without committing
        
        # Create association objects with required levels
        competency_count = 0
        for comp_data in path_data["competencies"]:
            competency = db.query(Competency).filter(
                Competency.name == comp_data["name"]
            ).first()
            
            if competency:
                # Create association object with required_level
                link = CareerPathCompetency(
                    career_path_id=career_path.id,
                    competency_id=competency.id,
                    required_level=comp_data["required_level"]
                )
                db.add(link)
                competency_count += 1
            else:
                print(f"  ⚠ Competency '{comp_data['name']}' not found in database")
        
        print(f"✓ Created career path: {path_data['role_name']} with {competency_count} competencies")
    
    db.commit()
    print("\n✅ Career path seeding completed successfully!")


def main():
    """Main entry point for seeding script"""
    print("=" * 60)
    print("Career Path Seeding Script")
    print("=" * 60)
    
    # Create database engine and session
    engine = create_engine(SQLALCHEMY_DATABASE_URL)
    db = Session(engine)
    
    try:
        # Check if competencies exist
        comp_count = db.query(Competency).count()
        if comp_count == 0:
            print("⚠ WARNING: No competencies found in database!")
            print("Please import competency data first before running this script.")
            return
        
        print(f"Found {comp_count} competencies in database\n")
        
        # Run seeding
        seed_career_paths(db)
        
    except Exception as e:
        print(f"\n❌ Error during seeding: {e}")
        db.rollback()
        raise
    finally:
        db.close()
        print("\nDatabase connection closed.")


if __name__ == "__main__":
    main()
