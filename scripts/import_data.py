"""
Script to import data from CSV files into database
"""

import os
import pandas as pd
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from app.core.database import Base, SessionLocal
from app.models import (
    JobBlock, 
    JobFamily, 
    JobSubFamily, 
    CompetencyGroup, 
    Competency, 
    CompetencyLevel
)
from dotenv import load_dotenv

# Load environment variables
load_dotenv()
DATABASE_URL = os.getenv("DATABASE_URL")

# Create database engine and session
engine = create_engine(DATABASE_URL)
Session = sessionmaker(autocommit=False, autoflush=False, bind=engine)
session = Session()

def import_job_structure():
    """Import job structure (Blocks → Families → Sub-Families) from CSV"""
    try:
        # Read job_families.csv
        df = pd.read_csv("data/job_families.csv")

        # Process JobBlock
        for block_name in df['Khối'].dropna().unique():
            block_name = block_name.strip()
            block = session.query(JobBlock).filter_by(name=block_name).first()
            if not block:
                block = JobBlock(name=block_name)
                session.add(block)
                session.commit()

        # Process JobFamily
        for _, row in df.iterrows():
            block_name = row['Khối'].strip()
            family_name = row['Họ công việc'].strip()

            block = session.query(JobBlock).filter_by(name=block_name).first()
            family = session.query(JobFamily).filter_by(name=family_name, block_id=block.id).first()
            if not family:
                family = JobFamily(name=family_name, block_id=block.id)
                session.add(family)
                session.commit()

            # Process JobSubFamily
            if pd.notna(row['Họ công việc con']):
                sub_family_name = row['Họ công việc con'].strip()
                sub_family = session.query(JobSubFamily).filter_by(name=sub_family_name, family_id=family.id).first()
                if not sub_family:
                    sub_family = JobSubFamily(name=sub_family_name, family_id=family.id)
                    session.add(sub_family)
                    session.commit()

        print("✓ Imported job structure successfully.")
    except Exception as e:
        session.rollback()
        print(f"✗ Error importing job structure: {e}")

def import_competency_groups():
    """Create 3 competency groups: CORE, LEAD, FUNC"""
    try:
        groups = [
            {"code": "CORE", "name": "Năng lực Chung"},
            {"code": "LEAD", "name": "Năng lực Lãnh đạo"},
            {"code": "FUNC", "name": "Năng lực Chuyên môn"}
        ]
        for group in groups:
            existing_group = session.query(CompetencyGroup).filter_by(code=group['code']).first()
            if not existing_group:
                new_group = CompetencyGroup(code=group['code'], name=group['name'])
                session.add(new_group)
                session.commit()

        print("✓ Imported competency groups successfully.")
    except Exception as e:
        session.rollback()
        print(f"✗ Error importing competency groups: {e}")

def import_competency_file(filepath, group_code, map_job_family=False):
    """
    Import competencies from CSV file
    
    Args:
        filepath: Path to CSV file
        group_code: CORE, LEAD, or FUNC
        map_job_family: If True, map competency to job family
    """
    try:
        df = pd.read_csv(filepath)
        group = session.query(CompetencyGroup).filter_by(code=group_code).first()

        for _, row in df.iterrows():
            # Kiểm tra nhiều tên cột có thể có
            name_col = None
            for possible_name in ['Tên Năng lực', 'Tên năng lực', 'Tên', 'Ten']:
                if possible_name in row.index:
                    name_col = possible_name
                    break
            
            if name_col is None or pd.isna(row[name_col]):
                continue

            competency_name = row[name_col].strip()
            competency = session.query(Competency).filter_by(name=competency_name, group_id=group.id).first()
            if not competency:
                competency = Competency(
                    name=competency_name,
                    definition=row['Định nghĩa'].strip(),
                    group_id=group.id
                )

                if map_job_family and 'Họ công việc' in row:
                    job_family_name = row['Họ công việc'].strip()
                    job_family = session.query(JobFamily).filter_by(name=job_family_name).first()
                    if job_family:
                        competency.job_family_id = job_family.id

                session.add(competency)
                session.commit()

            # Import 5 proficiency levels
            for level in range(1, 6):
                level_col = f'Cấp độ {level}'
                if level_col in row and pd.notna(row[level_col]):
                    level_description = row[level_col].strip()
                    existing_level = session.query(CompetencyLevel).filter_by(competency_id=competency.id, level=level).first()
                    if not existing_level:
                        new_level = CompetencyLevel(
                            competency_id=competency.id,
                            level=level,
                            description=level_description
                        )
                        session.add(new_level)
                        session.commit()

        print(f"✓ Imported competencies from {filepath} successfully.")
    except Exception as e:
        session.rollback()
        print(f"✗ Error importing competencies from {filepath}: {e}")

def main():
    """Main import function - runs all imports in sequence"""
    print("=" * 60)
    print("Starting data import...")
    print("=" * 60)
    
    # Step 1: Import job structure
    print("\n[1/5] Importing job structure...")
    import_job_structure()
    
    # Step 2: Import competency groups
    print("\n[2/5] Importing competency groups...")
    import_competency_groups()

    # Step 3: Import core competencies
    print("\n[3/5] Importing core competencies...")
    import_competency_file("data/competencies_core.csv", "CORE")
    
    # Step 4: Import leadership competencies
    print("\n[4/5] Importing leadership competencies...")
    import_competency_file("data/competencies_leadership.csv", "LEAD")
    
    # Step 5: Import functional competencies
    print("\n[5/5] Importing functional competencies...")
    import_competency_file("data/competencies_functional_ops.csv", "FUNC", map_job_family=True)
    import_competency_file("data/competencies_functional_tech.csv", "FUNC", map_job_family=True)
    
    print("\n" + "=" * 60)
    print("✓ Data import completed successfully!")
    print("=" * 60)

if __name__ == "__main__":
    main()
