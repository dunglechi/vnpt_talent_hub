# Getting Started - VNPT Talent Hub

## 🚀 5-Minute Quick Start

Hướng dẫn nhanh để bắt đầu sử dụng VNPT Talent Hub trong vòng 5 phút.

### Prerequisites
- Python 3.11 hoặc cao hơn
- Git
- Truy cập SSH đến server `one.vnptacademy.com.vn` (port 2222)
- Credentials đã được cấp (admin/Cntt@2025)

### Step 1: Clone Repository
```bash
git clone https://github.com/vnpt/talent-hub.git
cd vnpt-talent-hub
```

### Step 2: Setup Environment
```bash
# Windows
python -m venv venv
venv\Scripts\activate

# Linux/Mac
python3 -m venv venv
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt
```

### Step 3: Configure Environment
Tạo file `.env` ở root folder:
```bash
DATABASE_URL=postgresql://postgres:Cntt%402025@localhost:5432/vnpt_talent_hub
SECRET_KEY=your-secret-key-here-change-in-production
```

💡 **Lưu ý**: Password có ký tự `@` phải escape thành `%40` trong URL.

### Step 4: Setup SSH Tunnel
Mở terminal mới (giữ terminal này chạy):
```bash
ssh -L 5432:localhost:5432 admin@one.vnptacademy.com.vn -p 2222 -N
```
Nhập password: `Cntt@2025`

✅ **Kiểm tra tunnel**: Nếu không có lỗi → tunnel đã chạy!

### Step 5: Initialize Database
```bash
# Tạo database (chỉ chạy 1 lần)
python create_database.py

# Tạo tables
python create_tables.py

# Import data
python import_data.py
```

### Step 6: Verify Installation
```python
# Chạy trong Python interactive shell
python

>>> from database import SessionLocal
>>> from models import Competency
>>> db = SessionLocal()
>>> comps = db.query(Competency).all()
>>> print(f"Found {len(comps)} competencies")
Found 25 competencies
>>> exit()
```

🎉 **Chúc mừng!** Bạn đã setup thành công VNPT Talent Hub!

---

## 📊 Your First Query

### Query 1: List All Competency Groups
```python
from database import SessionLocal
from models import CompetencyGroup

db = SessionLocal()

# Get all groups
groups = db.query(CompetencyGroup).all()

for group in groups:
    print(f"ID: {group.id}, Code: {group.code}, Name: {group.name}")
    print(f"  - Competencies: {len(group.competencies)}")
```

**Expected Output**:
```
ID: 1, Code: CORE, Name: Core Competencies
  - Competencies: 10
ID: 2, Code: LEAD, Name: Leadership Competencies
  - Competencies: 5
ID: 3, Code: FUNC, Name: Functional Competencies
  - Competencies: 10
```

### Query 2: Get Competency with Levels
```python
from sqlalchemy.orm import joinedload

# Get competency with its levels (eager loading)
competency = db.query(Competency)\
    .options(joinedload(Competency.levels))\
    .filter(Competency.code == "TEAMWORK")\
    .first()

if competency:
    print(f"Competency: {competency.name}")
    print(f"Definition: {competency.definition}")
    print(f"\nProficiency Levels:")
    for level in competency.levels:
        print(f"  Level {level.level}: {level.description[:50]}...")
```

**Expected Output**:
```
Competency: Teamwork and Collaboration
Definition: Work effectively with others to achieve common goals

Proficiency Levels:
  Level 1: Basic understanding of teamwork principles...
  Level 2: Actively participates in team activities...
  Level 3: Facilitates team collaboration and resolves...
  Level 4: Leads cross-functional teams to achieve...
  Level 5: Builds high-performing teams and fosters...
```

### Query 3: Find Competencies by Job Family
```python
from models import JobFamily

# Find Software Development job family
job_family = db.query(JobFamily)\
    .filter(JobFamily.name.like("%Software%"))\
    .first()

if job_family:
    print(f"Job Family: {job_family.name}")
    print(f"Functional Competencies:")
    
    for comp in job_family.functional_competencies:
        print(f"  - {comp.name} ({comp.code})")
```

**Expected Output**:
```
Job Family: Software Development
Functional Competencies:
  - Python Programming (PYTHON)
  - System Design (SYS_DESIGN)
  - Database Management (DATABASE)
  - API Development (API_DEV)
```

---

## 🛠️ Common Workflows

### Workflow 1: Add New Employee
```python
from models import Employee, JobSubFamily

# 1. Find job sub-family
sub_family = db.query(JobSubFamily)\
    .filter(JobSubFamily.name == "Backend Developer")\
    .first()

# 2. Create employee
new_employee = Employee(
    name="Nguyen Van A",
    email="nguyenvana@vnpt.vn",
    job_sub_family_id=sub_family.id
)

db.add(new_employee)
db.commit()
db.refresh(new_employee)

print(f"Created employee: {new_employee.name} (ID: {new_employee.id})")
```

### Workflow 2: Create Assessment
```python
from models import Assessment
from datetime import datetime

# Note: Assessment model will be added in future
assessment = Assessment(
    employee_id=1,
    competency_id=5,
    assessed_level=3,
    target_level=4,
    notes="Good progress in teamwork skills",
    assessment_date=datetime.now()
)

db.add(assessment)
db.commit()
```

### Workflow 3: Get Employee Skills Gap
```python
# Find employee's competencies and compare with target level
def get_skills_gap(employee_id):
    assessments = db.query(Assessment)\
        .filter(Assessment.employee_id == employee_id)\
        .all()
    
    gaps = []
    for assess in assessments:
        if assess.assessed_level < assess.target_level:
            gap = {
                'competency': assess.competency.name,
                'current': assess.assessed_level,
                'target': assess.target_level,
                'gap': assess.target_level - assess.assessed_level
            }
            gaps.append(gap)
    
    return sorted(gaps, key=lambda x: x['gap'], reverse=True)

# Usage
gaps = get_skills_gap(employee_id=1)
print("Skills Gap Analysis:")
for gap in gaps:
    print(f"  {gap['competency']}: {gap['current']} → {gap['target']} (Gap: {gap['gap']})")
```

### Workflow 4: Bulk Import Employees
```python
import pandas as pd

# Read from Excel/CSV
df = pd.read_csv('employees.csv')

for _, row in df.iterrows():
    # Find job sub-family
    sub_family = db.query(JobSubFamily)\
        .filter(JobSubFamily.name == row['job_title'])\
        .first()
    
    if sub_family:
        employee = Employee(
            name=row['name'],
            email=row['email'],
            job_sub_family_id=sub_family.id
        )
        db.add(employee)

db.commit()
print(f"Imported {len(df)} employees")
```

---

## 🔍 Useful Queries

### Count Competencies by Group
```python
from sqlalchemy import func

results = db.query(
    CompetencyGroup.name,
    func.count(Competency.id).label('count')
)\
.join(Competency)\
.group_by(CompetencyGroup.name)\
.all()

for group_name, count in results:
    print(f"{group_name}: {count} competencies")
```

### Find All Employees in a Job Family
```python
from sqlalchemy.orm import aliased

# Get all employees in "Technology" block
results = db.query(Employee)\
    .join(JobSubFamily)\
    .join(JobFamily)\
    .join(JobBlock)\
    .filter(JobBlock.name == "Technology")\
    .all()

print(f"Found {len(results)} employees in Technology")
for emp in results:
    print(f"  - {emp.name}: {emp.job_sub_family.name}")
```

### Search Competencies by Keyword
```python
keyword = "communication"
results = db.query(Competency)\
    .filter(
        Competency.name.ilike(f"%{keyword}%") |
        Competency.definition.ilike(f"%{keyword}%")
    )\
    .all()

print(f"Found {len(results)} competencies matching '{keyword}':")
for comp in results:
    print(f"  - {comp.name}")
```

---

## 🐛 Troubleshooting

### Issue 1: "Connection refused"
**Problem**: Cannot connect to database  
**Solution**:
1. Check SSH tunnel is running:
   ```bash
   # Windows
   netstat -ano | findstr :5432
   
   # Linux/Mac
   lsof -i :5432
   ```
2. Restart SSH tunnel if needed
3. Verify `.env` file has correct DATABASE_URL

### Issue 2: "Module not found"
**Problem**: Import errors  
**Solution**:
```bash
# Activate virtual environment first
source venv/bin/activate  # or venv\Scripts\activate on Windows

# Reinstall dependencies
pip install -r requirements.txt
```

### Issue 3: "Database does not exist"
**Problem**: vnpt_talent_hub database not created  
**Solution**:
```bash
python create_database.py
```

### Issue 4: "Empty results"
**Problem**: No data returned from queries  
**Solution**:
```bash
# Import data
python import_data.py
```

---

## 📚 Next Steps

### Learn More
1. **Read Architecture**: Understand system design in `ARCHITECTURE.md`
2. **API Documentation**: Check `API_SPECS.md` for future API reference
3. **Security Policies**: Read `SECURITY.md` for best practices
4. **Deployment Guide**: See `DEPLOYMENT.md` for production setup

### Contribute
1. **Fork repository**
2. **Create feature branch**: `git checkout -b feature/my-feature`
3. **Make changes**
4. **Write tests**
5. **Submit Pull Request**

See `CONTRIBUTING.md` for detailed guidelines.

### Get Help
- **Documentation**: Check `FAQ.md` for common questions
- **Issues**: Create GitHub issue for bugs
- **Email**: tech@vnpt.vn for support
- **Security**: security@vnpt.vn for vulnerabilities

---

## 💡 Tips & Best Practices

### 1. Always Use Context Manager
```python
from database import SessionLocal

# ✅ Good: Auto-closes session
def get_competencies():
    db = SessionLocal()
    try:
        return db.query(Competency).all()
    finally:
        db.close()

# ❌ Bad: Forgets to close
def get_competencies():
    db = SessionLocal()
    return db.query(Competency).all()  # Session leak!
```

### 2. Use Eager Loading for Relationships
```python
# ❌ Bad: N+1 query problem
competencies = db.query(Competency).all()
for comp in competencies:
    print(comp.levels)  # Each iteration hits database!

# ✅ Good: Single query
from sqlalchemy.orm import joinedload
competencies = db.query(Competency)\
    .options(joinedload(Competency.levels))\
    .all()
```

### 3. Filter vs Filter_by
```python
# filter_by: Simple equality, uses keyword arguments
db.query(Competency).filter_by(code="TEAMWORK").first()

# filter: More powerful, uses column expressions
db.query(Competency).filter(Competency.code == "TEAMWORK").first()
db.query(Competency).filter(Competency.name.like("%Team%")).all()
```

### 4. Commit Carefully
```python
try:
    # Multiple operations
    db.add(employee1)
    db.add(employee2)
    db.commit()  # Commit once at the end
except Exception as e:
    db.rollback()  # Rollback on error
    print(f"Error: {e}")
finally:
    db.close()
```

### 5. Use Environment Variables
```python
# ❌ Bad: Hardcoded
DATABASE_URL = "postgresql://postgres:password@localhost/db"

# ✅ Good: From environment
import os
DATABASE_URL = os.getenv("DATABASE_URL")
if not DATABASE_URL:
    raise ValueError("DATABASE_URL not set")
```

---

## 🎯 Learning Path

### Beginner (Week 1)
- ✅ Complete quick start
- ✅ Run basic queries
- ✅ Understand database schema
- ✅ Read `models.py`

### Intermediate (Week 2-3)
- ✅ Write complex queries (joins, aggregations)
- ✅ Create workflows (add employees, assessments)
- ✅ Handle errors properly
- ✅ Read `ARCHITECTURE.md`

### Advanced (Week 4+)
- ✅ Optimize query performance
- ✅ Write migrations with Alembic
- ✅ Implement API endpoints (future)
- ✅ Deploy to production

---

## 📖 Code Examples Repository

All code examples from this guide are available in `examples/` folder:
- `examples/basic_queries.py`
- `examples/workflows.py`
- `examples/advanced_queries.py`
- `examples/performance_tips.py`

Run examples:
```bash
python examples/basic_queries.py
```

---

## 🔗 Quick Links

| Resource | Link |
|----------|------|
| 📘 Documentation | `README.md` |
| 🏗️ Architecture | `ARCHITECTURE.md` |
| 🔐 Security | `SECURITY.md` |
| 🚀 Deployment | `DEPLOYMENT.md` |
| ❓ FAQ | `FAQ.md` |
| 🤝 Contributing | `CONTRIBUTING.md` |
| 📝 Changelog | `CHANGELOG.md` |
| 📋 API Specs | `API_SPECS.md` |

---

**Version**: 1.0  
**Last Updated**: 2025-11-22  
**Maintainer**: VNPT IT Team

🚀 **Happy Coding!** Nếu gặp vấn đề, check `FAQ.md` hoặc tạo GitHub issue.