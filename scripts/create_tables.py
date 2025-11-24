"""
Script to create all database tables from models
Run after create_database.py
"""

from app.core.database import engine, Base
from app.models import (
    CompetencyGroup, 
    Competency, 
    CompetencyLevel,
    JobBlock, 
    JobFamily, 
    JobSubFamily, 
    Employee
)

# Tạo tất cả các bảng
Base.metadata.create_all(bind=engine)
print("✓ Đã tạo tất cả các bảng thành công!")
print("\nBây giờ chạy: python scripts/import_data.py")
