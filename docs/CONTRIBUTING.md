# Contributing Guide - VNPT Talent Hub

## 🎯 Quy tắc Đóng góp

Cảm ơn bạn đã quan tâm đến việc đóng góp cho VNPT Talent Hub! Tài liệu này cung cấp hướng dẫn về cách thức đóng góp hiệu quả.

## 📋 Mục lục
1. [Code of Conduct](#code-of-conduct)
2. [Getting Started](#getting-started)
3. [Development Workflow](#development-workflow)
4. [Coding Standards](#coding-standards)
5. [Commit Messages](#commit-messages)
6. [Pull Request Process](#pull-request-process)
7. [Testing](#testing)

## Code of Conduct

- Tôn trọng mọi thành viên trong team
- Đưa ra feedback mang tính xây dựng
- Tập trung vào vấn đề, không công kích cá nhân
- Chấp nhận các quan điểm khác nhau

## Getting Started

### 1. Fork và Clone Repository
```bash
# Fork repository trên GitHub
# Clone về máy local
git clone https://github.com/your-username/vnpt-talent-hub.git
cd vnpt-talent-hub
```

### 2. Setup Development Environment
```bash
# Tạo virtual environment
python -m venv venv
source venv/bin/activate  # Linux/Mac
venv\Scripts\activate     # Windows

# Cài đặt dependencies
pip install -r requirements.txt
pip install -r requirements-dev.txt  # Development dependencies
```

### 3. Tạo SSH Tunnel
```bash
ssh -L 5432:localhost:5432 admin@one.vnptacademy.com.vn -p 2222 -N
```

### 4. Configure Environment
```bash
cp .env.example .env
# Chỉnh sửa .env với thông tin phù hợp
```

## Development Workflow

### Branch Naming Convention
```
feature/ten-tinh-nang    # Tính năng mới
bugfix/ten-loi           # Sửa lỗi
hotfix/ten-loi-gap       # Sửa lỗi khẩn cấp production
docs/ten-tai-lieu        # Cập nhật tài liệu
refactor/ten-phan        # Refactor code
test/ten-test            # Thêm/sửa tests
```

### Workflow Steps
```bash
# 1. Tạo branch mới từ main
git checkout main
git pull origin main
git checkout -b feature/ten-tinh-nang

# 2. Thực hiện thay đổi
# ... code code code ...

# 3. Commit thay đổi
git add .
git commit -m "feat: Thêm tính năng X"

# 4. Push lên remote
git push origin feature/ten-tinh-nang

# 5. Tạo Pull Request trên GitHub
```

## Coding Standards

### Python Style Guide
Tuân theo [PEP 8](https://peps.python.org/pep-0008/)

**Tools:**
```bash
# Format code
black .

# Sort imports
isort .

# Lint
flake8 .
pylint **/*.py

# Type checking
mypy .
```

### Code Organization
```python
# 1. Standard library imports
import os
import sys

# 2. Third-party imports
from sqlalchemy import Column, Integer
import pandas as pd

# 3. Local imports
from database import Base
from models import Competency
```

### Naming Conventions
```python
# Classes: PascalCase
class CompetencyGroup:
    pass

# Functions/Variables: snake_case
def get_competency_by_id(competency_id: int):
    return None

# Constants: UPPER_SNAKE_CASE
MAX_LEVEL = 5
DATABASE_URL = "postgresql://..."

# Private: _prefixed
def _internal_helper():
    pass
```

### Documentation
```python
def assess_competency(employee_id: int, competency_id: int, level: int) -> Assessment:
    """
    Đánh giá năng lực của nhân viên.
    
    Args:
        employee_id: ID của nhân viên
        competency_id: ID của năng lực cần đánh giá
        level: Cấp độ đánh giá (1-5)
        
    Returns:
        Assessment: Đối tượng đánh giá đã tạo
        
    Raises:
        ValueError: Nếu level không hợp lệ
        NotFoundError: Nếu employee hoặc competency không tồn tại
        
    Example:
        >>> assessment = assess_competency(1, 5, 3)
        >>> assessment.level
        3
    """
    pass
```

## Commit Messages

### Format
```
<type>(<scope>): <subject>

<body>

<footer>
```

### Types
- `feat`: Tính năng mới
- `fix`: Sửa lỗi
- `docs`: Thay đổi documentation
- `style`: Format, thiếu semicolon, etc (không ảnh hưởng code)
- `refactor`: Refactor code
- `test`: Thêm tests
- `chore`: Cập nhật build tasks, package manager, etc

### Examples
```bash
# Feature
git commit -m "feat(api): Thêm endpoint đánh giá năng lực"

# Bug fix
git commit -m "fix(database): Sửa lỗi connection timeout"

# Documentation
git commit -m "docs(readme): Cập nhật hướng dẫn cài đặt"

# With body
git commit -m "feat(assessment): Thêm 360-degree feedback

- Thêm bảng FeedbackRequest
- API endpoint để gửi request
- Email notification cho reviewers"
```

## Pull Request Process

### Checklist trước khi tạo PR
- [ ] Code đã được format (black, isort)
- [ ] Code đã pass lint (flake8, pylint)
- [ ] Tests đã được thêm/cập nhật
- [ ] Tests pass (pytest)
- [ ] Documentation đã được cập nhật
- [ ] CHANGELOG.md đã được cập nhật
- [ ] Branch đã được rebase với main

### PR Template
```markdown
## Mô tả
Mô tả ngắn gọn về thay đổi này

## Loại thay đổi
- [ ] Bug fix
- [ ] Tính năng mới
- [ ] Breaking change
- [ ] Documentation

## Checklist
- [ ] Code đã được test
- [ ] Documentation đã được cập nhật
- [ ] CHANGELOG đã được cập nhật

## Screenshots (nếu có)

## Related Issues
Closes #123
```

### Review Process
1. Ít nhất 1 reviewer approve
2. Tất cả comments đã được resolve
3. CI/CD pipeline pass
4. Không có conflicts với main

## Testing

### Running Tests
```bash
# Chạy tất cả tests
pytest

# Chạy với coverage
pytest --cov=. --cov-report=html

# Chạy specific test
pytest tests/test_models.py

# Chạy với verbose
pytest -v
```

### Writing Tests
```python
# tests/test_competency.py
import pytest
from models import Competency
from database import SessionLocal

@pytest.fixture
def db_session():
    """Fixture tạo database session cho testing."""
    session = SessionLocal()
    yield session
    session.close()

def test_create_competency(db_session):
    """Test tạo năng lực mới."""
    competency = Competency(
        name="Test Competency",
        code="TEST",
        definition="Test definition",
        group_id=1
    )
    db_session.add(competency)
    db_session.commit()
    
    assert competency.id is not None
    assert competency.name == "Test Competency"

def test_competency_validation():
    """Test validation của competency."""
    with pytest.raises(ValueError):
        Competency(name="", code="TEST")
```

## Database Migrations

### Tạo Migration
```bash
# Tạo migration mới
alembic revision --autogenerate -m "Thêm bảng Assessment"

# Review file migration được tạo
# Chỉnh sửa nếu cần thiết

# Apply migration
alembic upgrade head
```

### Migration Best Practices
- Luôn review auto-generated migrations
- Test migrations trên dev database trước
- Thêm downgrade logic
- Document breaking changes

## Questions?

Nếu có thắc mắc, hãy:
1. Kiểm tra [README.md](README.md)
2. Tìm trong [Issues](https://github.com/vnpt/talent-hub/issues)
3. Tạo issue mới với tag `question`
4. Liên hệ team lead

---

**Cảm ơn bạn đã đóng góp! 🎉**