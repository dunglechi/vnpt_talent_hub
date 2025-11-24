"""
Database configuration and session management
"""

import os
from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from dotenv import load_dotenv

# Load biến môi trường từ file .env
load_dotenv()

# Lấy chuỗi kết nối từ file .env
SQLALCHEMY_DATABASE_URL = os.getenv("DATABASE_URL")

# Kiểm tra xem URL có tồn tại không
if not SQLALCHEMY_DATABASE_URL:
    raise ValueError("DATABASE_URL is not set in .env file")

# Tạo engine kết nối
engine = create_engine(SQLALCHEMY_DATABASE_URL)

# Tạo SessionLocal để dùng cho các giao dịch database
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Tạo Base class cho các models kế thừa
Base = declarative_base()

# Dependency để lấy database session
def get_db():
    """
    Dependency function to get database session.
    Usage in FastAPI:
        @app.get("/api/competencies")
        def list_competencies(db: Session = Depends(get_db)):
            return db.query(Competency).all()
    """
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
