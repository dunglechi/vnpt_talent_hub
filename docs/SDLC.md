# SDLC - Software Development Life Cycle

## 📋 Tổng quan

Tài liệu này mô tả quy trình phát triển phần mềm (SDLC) cho VNPT Talent Hub, đảm bảo chất lượng và hiệu quả trong mọi giai đoạn từ lập kế hoạch đến vận hành.

---

## 🎯 Mô hình SDLC: Agile + DevOps

VNPT Talent Hub sử dụng **Agile Scrum** kết hợp **DevOps practices**:

```
┌─────────────────────────────────────────────────────────────┐
│                    CONTINUOUS CYCLE                          │
│                                                              │
│  Plan → Design → Develop → Test → Deploy → Operate → Plan  │
│    ↑                                                    ↓    │
│    └────────────────── Feedback ──────────────────────┘    │
└─────────────────────────────────────────────────────────────┘
```

### Tại sao chọn Agile?
- ✅ Linh hoạt với yêu cầu thay đổi
- ✅ Phản hồi nhanh từ stakeholders
- ✅ Releases thường xuyên, giá trị sớm
- ✅ Phù hợp với đặc thành HR management system

---

## 📊 Phase 1: Planning (Lập kế hoạch)

### 1.1 Stakeholder Analysis

| Stakeholder | Role | Needs |
|------------|------|-------|
| **HR Manager** | Product Owner | Framework năng lực, báo cáo tổng hợp |
| **Department Manager** | Primary User | Đánh giá team, phát triển nhân sự |
| **Employee** | End User | Xem năng lực, tự đánh giá, mục tiêu |
| **IT Admin** | System Admin | Vận hành, bảo trì, monitoring |
| **VNPT Leadership** | Sponsor | ROI, KPIs, compliance |

### 1.2 Requirements Gathering

#### Functional Requirements
```
FR-001: Quản lý framework năng lực (CORE/LEAD/FUNC)
FR-002: Đánh giá năng lực nhân viên (5 levels)
FR-003: Lập kế hoạch phát triển cá nhân (IDP)
FR-004: Báo cáo skills gap analysis
FR-005: Dashboard tổng quan năng lực tổ chức
FR-006: Quản lý job family và career path
FR-007: Export/Import dữ liệu (Excel, CSV)
FR-008: Notifications và reminders
FR-009: Multi-language support (VN/EN)
FR-010: Role-based access control (RBAC)
```

#### Non-Functional Requirements
```
NFR-001: Performance - Response time < 200ms (95th percentile)
NFR-002: Scalability - Support 10,000+ employees
NFR-003: Availability - 99.9% uptime (8.76h downtime/year)
NFR-004: Security - GDPR, Vietnam Cybersecurity Law compliance
NFR-005: Usability - Mobile-responsive, accessibility (WCAG 2.1)
NFR-006: Maintainability - Modular architecture, documented code
NFR-007: Data Integrity - ACID transactions, backup/restore
NFR-008: Auditability - Complete audit log for all changes
```

### 1.3 Sprint Planning (2-week sprints)

```
Sprint 0 (Foundation):
  - Database design ✅
  - Data import ✅
  - Documentation ✅

Sprint 1: Core API Development
  - FastAPI setup
  - Authentication & Authorization (JWT)
  - Competency CRUD endpoints
  - Job structure endpoints

Sprint 2: Assessment Features
  - Assessment creation & editing
  - Approval workflow
  - Skills gap calculation
  - Notification system

Sprint 3: Reporting & Analytics
  - Dashboard widgets
  - Skills gap reports
  - Competency matrix views
  - Export functionality

Sprint 4: Frontend Development
  - Next.js setup
  - Authentication UI
  - Competency management UI
  - Employee profile pages

Sprint 5: Advanced Features
  - Individual Development Plan (IDP)
  - Career path visualization
  - Batch operations
  - Advanced search & filters

Sprint 6: Testing & Refinement
  - E2E testing
  - Performance optimization
  - Security hardening
  - UAT with stakeholders

Sprint 7: Deployment & Launch
  - Production deployment
  - Training materials
  - User documentation
  - Go-live support
```

---

## 🎨 Phase 2: Design

### 2.1 System Architecture

```
┌──────────────────────────────────────────────────────────┐
│                    PRESENTATION LAYER                     │
│  ┌────────────┐  ┌────────────┐  ┌────────────┐        │
│  │   Web UI   │  │ Mobile App │  │Admin Panel │        │
│  │ (Next.js)  │  │(React Native)│ │  (React)  │        │
│  └────────────┘  └────────────┘  └────────────┘        │
└──────────────────────────────────────────────────────────┘
                        ↓ HTTPS/REST
┌──────────────────────────────────────────────────────────┐
│                   APPLICATION LAYER                       │
│  ┌──────────────────────────────────────────────────┐   │
│  │         API Gateway (FastAPI + Nginx)            │   │
│  └──────────────────────────────────────────────────┘   │
│  ┌──────────────┐ ┌──────────────┐ ┌──────────────┐    │
│  │Competency    │ │Assessment    │ │Employee      │    │
│  │Service       │ │Service       │ │Service       │    │
│  └──────────────┘ └──────────────┘ └──────────────┘    │
└──────────────────────────────────────────────────────────┘
                        ↓ ORM
┌──────────────────────────────────────────────────────────┐
│                      DATA LAYER                           │
│  ┌────────────────────────────────────────────────┐     │
│  │        PostgreSQL 14 (Primary + Replicas)      │     │
│  └────────────────────────────────────────────────┘     │
│  ┌────────────────────────────────────────────────┐     │
│  │        Redis (Cache + Session Store)           │     │
│  └────────────────────────────────────────────────┘     │
└──────────────────────────────────────────────────────────┘
```

### 2.2 Database Design

**Current Schema** (v1.0):
- ✅ CompetencyGroup, Competency, CompetencyLevel
- ✅ JobBlock, JobFamily, JobSubFamily
- ✅ Employee

**Future Extensions** (v1.1+):
```sql
-- Assessment & Development
CREATE TABLE assessments (
    id SERIAL PRIMARY KEY,
    employee_id INT REFERENCES employees(id),
    competency_id INT REFERENCES competencies(id),
    assessor_id INT REFERENCES employees(id),
    assessed_level INT CHECK (assessed_level BETWEEN 1 AND 5),
    target_level INT CHECK (target_level BETWEEN 1 AND 5),
    evidence TEXT,
    notes TEXT,
    status VARCHAR(20), -- draft, submitted, approved
    assessment_date TIMESTAMP,
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW()
);

CREATE TABLE development_plans (
    id SERIAL PRIMARY KEY,
    employee_id INT REFERENCES employees(id),
    competency_id INT REFERENCES competencies(id),
    current_level INT,
    target_level INT,
    actions TEXT,
    resources TEXT,
    target_date DATE,
    status VARCHAR(20), -- planned, in-progress, completed
    created_at TIMESTAMP DEFAULT NOW()
);

-- Audit & History
CREATE TABLE audit_logs (
    id SERIAL PRIMARY KEY,
    user_id INT REFERENCES employees(id),
    action VARCHAR(50),
    entity_type VARCHAR(50),
    entity_id INT,
    old_values JSONB,
    new_values JSONB,
    ip_address VARCHAR(45),
    user_agent TEXT,
    created_at TIMESTAMP DEFAULT NOW()
);

-- Notifications
CREATE TABLE notifications (
    id SERIAL PRIMARY KEY,
    user_id INT REFERENCES employees(id),
    type VARCHAR(50), -- assessment_due, plan_overdue, etc.
    title VARCHAR(200),
    message TEXT,
    is_read BOOLEAN DEFAULT FALSE,
    link TEXT,
    created_at TIMESTAMP DEFAULT NOW()
);
```

### 2.3 API Design

**RESTful Endpoints**:

```
Authentication:
POST   /api/v1/auth/login
POST   /api/v1/auth/logout
POST   /api/v1/auth/refresh
GET    /api/v1/auth/me

Competencies:
GET    /api/v1/competencies
GET    /api/v1/competencies/{id}
POST   /api/v1/competencies
PUT    /api/v1/competencies/{id}
DELETE /api/v1/competencies/{id}
GET    /api/v1/competencies/{id}/levels

Assessments:
GET    /api/v1/assessments
POST   /api/v1/assessments
GET    /api/v1/assessments/{id}
PUT    /api/v1/assessments/{id}
POST   /api/v1/assessments/{id}/approve
POST   /api/v1/assessments/{id}/reject
GET    /api/v1/employees/{id}/assessments

Reports:
GET    /api/v1/reports/skills-gap
GET    /api/v1/reports/competency-matrix
GET    /api/v1/reports/team-summary
POST   /api/v1/reports/export

Employees:
GET    /api/v1/employees
GET    /api/v1/employees/{id}
GET    /api/v1/employees/{id}/profile
GET    /api/v1/employees/{id}/development-plan
```

### 2.4 UI/UX Design Principles

```
1. SIMPLICITY
   - Clean, minimal interface
   - Max 3 clicks to any feature
   - Progressive disclosure

2. CONSISTENCY
   - Uniform color scheme (VNPT branding)
   - Consistent button styles
   - Predictable navigation

3. FEEDBACK
   - Loading indicators
   - Success/error messages
   - Progress tracking

4. ACCESSIBILITY
   - WCAG 2.1 Level AA compliance
   - Keyboard navigation
   - Screen reader support
   - High contrast mode

5. MOBILE-FIRST
   - Responsive design
   - Touch-friendly (min 44x44px buttons)
   - Offline capability (future)
```

---

## 💻 Phase 3: Development

### 3.1 Development Environment Setup

```bash
# 1. Clone repository
git clone https://github.com/vnpt/talent-hub.git
cd vnpt-talent-hub

# 2. Backend setup
python -m venv venv
source venv/bin/activate  # or venv\Scripts\activate (Windows)
pip install -r requirements.txt
cp .env.example .env

# 3. Database setup
python scripts/ssh_tunnel.py  # In separate terminal
python scripts/create_database.py
python scripts/create_tables.py
python scripts/import_data.py

# 4. Frontend setup (future)
cd frontend
npm install
cp .env.example .env.local
npm run dev

# 5. Run tests
pytest tests/
```

### 3.2 Coding Standards

#### Python (Backend)
```python
# PEP 8 compliance
# Type hints required
# Docstrings for all public functions

from typing import List, Optional
from app.models import Competency
from app.core.database import SessionLocal

def get_competencies_by_group(
    group_code: str,
    include_levels: bool = True
) -> List[Competency]:
    """
    Retrieve competencies by group code.
    
    Args:
        group_code: Group code (CORE, LEAD, FUNC)
        include_levels: Include proficiency levels
        
    Returns:
        List of Competency objects
        
    Raises:
        ValueError: If group_code is invalid
    """
    db = SessionLocal()
    try:
        query = db.query(Competency).filter_by(group_code=group_code)
        if include_levels:
            query = query.options(joinedload(Competency.levels))
        return query.all()
    finally:
        db.close()
```

#### TypeScript (Frontend - Future)
```typescript
// Strict mode enabled
// ESLint + Prettier
// Functional components with hooks

interface Employee {
  id: number;
  name: string;
  email: string;
  jobTitle: string;
  department: string;
}

const EmployeeCard: React.FC<{ employee: Employee }> = ({ employee }) => {
  return (
    <div className="card">
      <h3>{employee.name}</h3>
      <p>{employee.jobTitle}</p>
      <p>{employee.email}</p>
    </div>
  );
};
```

### 3.3 Git Workflow

```
main (production)
  ↑
  merge ← release/v1.x
            ↑
            merge ← develop (integration)
                      ↑
                      merge ← feature/feature-name
                      merge ← bugfix/bug-description
                      merge ← hotfix/critical-fix
```

**Branch Naming Convention**:
- `feature/TH-123-add-assessment-api` (feature)
- `bugfix/TH-456-fix-login-error` (bug fix)
- `hotfix/TH-789-security-patch` (critical fix)
- `release/v1.1.0` (release preparation)

**Commit Message Format**:
```
<type>(<scope>): <subject>

<body>

<footer>
```

Examples:
```
feat(api): add assessment approval endpoint

Implement POST /api/v1/assessments/{id}/approve
with role-based authorization checks.

Closes TH-123

---

fix(auth): resolve JWT token expiration issue

Token was expiring too quickly due to incorrect
timezone calculation.

Fixes TH-456

---

docs(readme): update installation instructions

Added steps for SSH tunnel setup and
environment configuration.
```

### 3.4 Code Review Process

**Checklist**:
- [ ] Code follows style guide
- [ ] Unit tests written and passing
- [ ] Documentation updated
- [ ] No security vulnerabilities (Bandit, safety)
- [ ] Performance considerations addressed
- [ ] Database migrations included (if applicable)
- [ ] API documentation updated (if applicable)
- [ ] Manual testing completed
- [ ] Peer review approval (min 1 reviewer)

**Review Levels**:
1. **Junior Dev**: 2 reviewers required
2. **Mid-level Dev**: 1 reviewer required
3. **Senior Dev**: 1 reviewer required (security changes: 2)
4. **Tech Lead**: Self-merge allowed (non-critical)

---

## 🧪 Phase 4: Testing

### 4.1 Testing Strategy

```
┌─────────────────────────────────────────────────┐
│            Testing Pyramid                       │
│                                                  │
│              ┌────────┐                         │
│              │  E2E   │  10% - Critical flows   │
│              └────────┘                         │
│           ┌──────────────┐                      │
│           │ Integration  │  30% - API, DB      │
│           └──────────────┘                      │
│        ┌────────────────────┐                   │
│        │   Unit Tests       │  60% - Logic     │
│        └────────────────────┘                   │
└─────────────────────────────────────────────────┘
```

### 4.2 Unit Testing

```python
# tests/test_competency_service.py
import pytest
from app.models import Competency, CompetencyGroup
from app.services.competency_service import CompetencyService

def test_create_competency(db_session):
    """Test competency creation"""
    service = CompetencyService(db_session)
    
    group = CompetencyGroup(code="CORE", name="Core")
    db_session.add(group)
    db_session.commit()
    
    competency = service.create_competency(
        name="Communication",
        code="COMM",
        definition="Effective communication skills",
        group_id=group.id
    )
    
    assert competency.id is not None
    assert competency.name == "Communication"
    assert competency.group_id == group.id

def test_get_competencies_by_group(db_session):
    """Test retrieving competencies by group"""
    service = CompetencyService(db_session)
    
    # Setup test data
    # ...
    
    competencies = service.get_by_group("CORE")
    
    assert len(competencies) == 10
    assert all(c.group.code == "CORE" for c in competencies)

# Run: pytest tests/ -v --cov=app --cov-report=html
```

### 4.3 Integration Testing

```python
# tests/integration/test_api.py
from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)

def test_login():
    """Test authentication endpoint"""
    response = client.post(
        "/api/v1/auth/login",
        json={"email": "test@vnpt.vn", "password": "password123"}
    )
    
    assert response.status_code == 200
    data = response.json()
    assert "access_token" in data
    assert "refresh_token" in data

def test_get_competencies_authenticated():
    """Test competency list with authentication"""
    # Login first
    login_response = client.post(
        "/api/v1/auth/login",
        json={"email": "admin@vnpt.vn", "password": "admin123"}
    )
    token = login_response.json()["access_token"]
    
    # Get competencies
    response = client.get(
        "/api/v1/competencies",
        headers={"Authorization": f"Bearer {token}"}
    )
    
    assert response.status_code == 200
    data = response.json()
    assert "data" in data
    assert len(data["data"]) > 0
```

### 4.4 E2E Testing (Playwright/Cypress)

```typescript
// tests/e2e/assessment.spec.ts
import { test, expect } from '@playwright/test';

test('Manager can create assessment for employee', async ({ page }) => {
  // Login as manager
  await page.goto('/login');
  await page.fill('[name="email"]', 'manager@vnpt.vn');
  await page.fill('[name="password"]', 'password123');
  await page.click('button[type="submit"]');
  
  // Navigate to employee
  await page.goto('/employees/123');
  await page.click('text=Create Assessment');
  
  // Fill assessment form
  await page.selectOption('[name="competency"]', 'Communication');
  await page.selectOption('[name="level"]', '3');
  await page.fill('[name="notes"]', 'Good progress in team meetings');
  await page.click('button:has-text("Submit")');
  
  // Verify success
  await expect(page.locator('.success-message')).toBeVisible();
  await expect(page.locator('text=Assessment created')).toBeVisible();
});
```

### 4.5 Performance Testing

```python
# tests/performance/load_test.py
from locust import HttpUser, task, between

class TalentHubUser(HttpUser):
    wait_time = between(1, 3)
    
    def on_start(self):
        """Login before tests"""
        response = self.client.post("/api/v1/auth/login", json={
            "email": "test@vnpt.vn",
            "password": "password123"
        })
        self.token = response.json()["access_token"]
        self.headers = {"Authorization": f"Bearer {self.token}"}
    
    @task(3)
    def view_competencies(self):
        """Most common operation"""
        self.client.get("/api/v1/competencies", headers=self.headers)
    
    @task(2)
    def view_employee_profile(self):
        """Second most common"""
        self.client.get("/api/v1/employees/123/profile", headers=self.headers)
    
    @task(1)
    def create_assessment(self):
        """Less frequent operation"""
        self.client.post("/api/v1/assessments", json={
            "employee_id": 123,
            "competency_id": 5,
            "assessed_level": 3,
            "notes": "Test assessment"
        }, headers=self.headers)

# Run: locust -f tests/performance/load_test.py --host=https://talenthub.vnpt.vn
# Target: 100 concurrent users, response time < 200ms (p95)
```

### 4.6 Security Testing

**Automated Scans**:
```bash
# Dependency vulnerabilities
pip install safety
safety check

# Static code analysis
pip install bandit
bandit -r app/ -f json -o security-report.json

# SQL injection, XSS testing
pip install sqlmap
# Configure and run against staging environment
```

**Manual Testing**:
- [ ] Authentication bypass attempts
- [ ] Authorization checks (privilege escalation)
- [ ] Input validation (SQL injection, XSS)
- [ ] Session management
- [ ] CSRF protection
- [ ] Rate limiting
- [ ] API security (mass assignment, etc.)

---

## 🚀 Phase 5: Deployment

### 5.1 Deployment Pipeline

```
┌──────────┐     ┌──────────┐     ┌──────────┐     ┌──────────┐
│  Commit  │────▶│   Test   │────▶│  Build   │────▶│  Deploy  │
│  to Git  │     │ (CI/CD)  │     │  Docker  │     │ Staging  │
└──────────┘     └──────────┘     └──────────┘     └──────────┘
                                                          │
                                                          ▼
                                                    ┌──────────┐
                                                    │ Approval │
                                                    └──────────┘
                                                          │
                                                          ▼
                                                    ┌──────────┐
                                                    │  Deploy  │
                                                    │Production│
                                                    └──────────┘
```

### 5.2 CI/CD Configuration (GitHub Actions)

```yaml
# .github/workflows/ci-cd.yml
name: CI/CD Pipeline

on:
  push:
    branches: [main, develop]
  pull_request:
    branches: [main, develop]

jobs:
  test:
    runs-on: ubuntu-latest
    
    services:
      postgres:
        image: postgres:14
        env:
          POSTGRES_PASSWORD: postgres
        options: >-
          --health-cmd pg_isready
          --health-interval 10s
          --health-timeout 5s
          --health-retries 5
    
    steps:
    - uses: actions/checkout@v3
    
    - name: Set up Python
      uses: actions/setup-python@v4
      with:
        python-version: '3.11'
    
    - name: Install dependencies
      run: |
        pip install -r requirements.txt
        pip install pytest pytest-cov
    
    - name: Run tests
      run: |
        pytest tests/ --cov=app --cov-report=xml
    
    - name: Upload coverage
      uses: codecov/codecov-action@v3
  
  build:
    needs: test
    runs-on: ubuntu-latest
    if: github.ref == 'refs/heads/main'
    
    steps:
    - uses: actions/checkout@v3
    
    - name: Build Docker image
      run: |
        docker build -t vnpt-talent-hub:${{ github.sha }} .
        docker tag vnpt-talent-hub:${{ github.sha }} vnpt-talent-hub:latest
    
    - name: Push to registry
      run: |
        docker push vnpt-talent-hub:${{ github.sha }}
        docker push vnpt-talent-hub:latest
  
  deploy-staging:
    needs: build
    runs-on: ubuntu-latest
    environment: staging
    
    steps:
    - name: Deploy to staging
      run: |
        ssh deploy@staging.vnpt.vn "
          docker pull vnpt-talent-hub:${{ github.sha }}
          docker-compose -f docker-compose.staging.yml up -d
        "
  
  deploy-production:
    needs: deploy-staging
    runs-on: ubuntu-latest
    environment: production
    if: github.ref == 'refs/heads/main'
    
    steps:
    - name: Deploy to production
      run: |
        ssh deploy@talenhub.vnpt.vn "
          docker pull vnpt-talent-hub:${{ github.sha }}
          docker-compose -f docker-compose.prod.yml up -d
        "
```

### 5.3 Deployment Checklist

**Pre-Deployment**:
- [ ] All tests passing (unit, integration, E2E)
- [ ] Code review approved
- [ ] Security scan completed (no critical issues)
- [ ] Performance benchmarks met
- [ ] Database migrations prepared
- [ ] Rollback plan documented
- [ ] Stakeholders notified
- [ ] Documentation updated

**Deployment**:
- [ ] Backup current production database
- [ ] Deploy to staging first
- [ ] Run smoke tests on staging
- [ ] Get approval from stakeholders
- [ ] Deploy to production (blue-green or canary)
- [ ] Run health checks
- [ ] Monitor error rates and performance

**Post-Deployment**:
- [ ] Verify critical flows working
- [ ] Check monitoring dashboards
- [ ] Verify database migrations applied
- [ ] Update deployment log
- [ ] Notify users of new features
- [ ] Archive deployment artifacts

### 5.4 Environment Configuration

| Environment | Purpose | URL | Database |
|------------|---------|-----|----------|
| **Development** | Local dev | localhost:8000 | Local PostgreSQL |
| **Staging** | Testing | staging.vnpt.vn | Staging DB |
| **Production** | Live system | talenhub.vnpt.vn | Production DB |
| **DR** | Disaster Recovery | dr.vnpt.vn | Replica DB |

---

## 🔧 Phase 6: Operations & Maintenance

### 6.1 Monitoring & Alerting

**Metrics to Monitor**:
```
Application Metrics:
- Request rate (req/sec)
- Response time (p50, p95, p99)
- Error rate (%)
- Active users (concurrent)

Database Metrics:
- Connection pool usage
- Query performance (slow queries)
- Table size growth
- Replication lag

Infrastructure Metrics:
- CPU usage (%)
- Memory usage (%)
- Disk I/O
- Network traffic

Business Metrics:
- Active users (DAU/MAU)
- Assessments created per day
- Average time to complete assessment
- Feature adoption rate
```

**Alerting Rules**:
```
Critical (Immediate response):
- Service down (> 1 minute)
- Error rate > 5%
- Database connection failures
- Disk usage > 90%

Warning (Response within 1 hour):
- Response time > 500ms (p95)
- Memory usage > 80%
- Failed login attempts > 100/hour
- Slow queries > 10 per minute

Info (Monitor):
- Deployment completed
- Scheduled backup completed
- Database migration applied
```

### 6.2 Backup & Recovery

**Backup Strategy**:
```
Daily Full Backup:
- Time: 2:00 AM (low traffic)
- Retention: 30 days
- Location: S3 + offsite storage

Hourly Incremental Backup:
- Retention: 7 days
- Transaction logs

Monthly Archive:
- Retention: 5 years (compliance)
- Cold storage
```

**Recovery Plan**:
```
RTO (Recovery Time Objective): 1 hour
RPO (Recovery Point Objective): 1 hour

Disaster Recovery Steps:
1. Activate DR environment (15 minutes)
2. Restore latest backup (30 minutes)
3. Apply transaction logs (10 minutes)
4. Verify data integrity (5 minutes)
5. Switch DNS to DR (5 minutes)
6. Monitor and stabilize (5 minutes)
```

### 6.3 Incident Management

**Severity Levels**:

| Level | Definition | Response Time | Example |
|-------|-----------|---------------|---------|
| **P0** | Complete outage | 15 minutes | Database down |
| **P1** | Critical feature broken | 1 hour | Login not working |
| **P2** | Major feature impaired | 4 hours | Reports slow |
| **P3** | Minor issue | 24 hours | UI glitch |
| **P4** | Cosmetic issue | 7 days | Typo in label |

**Incident Response Process**:
```
1. DETECTION
   - Monitoring alert or user report
   - Create incident ticket
   
2. TRIAGE
   - Assess severity (P0-P4)
   - Assign incident commander
   - Notify stakeholders
   
3. INVESTIGATION
   - Check logs, metrics
   - Identify root cause
   - Document findings
   
4. RESOLUTION
   - Apply fix (or rollback)
   - Verify fix in production
   - Update stakeholders
   
5. POST-MORTEM
   - Write incident report
   - Identify improvements
   - Update runbooks
   - Schedule follow-up tasks
```

### 6.4 Change Management

**Change Request Process**:
```
1. Submit Change Request (CR)
   - Description of change
   - Business justification
   - Risk assessment
   - Rollback plan
   
2. Review & Approval
   - Technical review (Tech Lead)
   - Security review (if needed)
   - Management approval (for major changes)
   
3. Schedule Change
   - Planned maintenance window
   - Notify users (if downtime)
   
4. Implement Change
   - Follow deployment checklist
   - Monitor closely
   
5. Post-Implementation Review
   - Verify success
   - Update documentation
   - Close CR ticket
```

**Maintenance Windows**:
- **Routine**: Every Tuesday 2:00-4:00 AM
- **Emergency**: As needed (with approval)
- **Major Release**: Quarterly, scheduled 1 month in advance

---

## 📈 Phase 7: Continuous Improvement

### 7.1 Metrics & KPIs

**Development Metrics**:
```
Velocity:
- Story points completed per sprint
- Feature completion rate

Quality:
- Code coverage (target: 80%+)
- Bug density (bugs per KLOC)
- Defect escape rate
- Technical debt ratio

Performance:
- Lead time (idea to production)
- Deployment frequency
- Mean time to recovery (MTTR)
- Change failure rate
```

**Product Metrics**:
```
Adoption:
- Active users (DAU/MAU)
- Feature adoption rate
- User retention rate

Satisfaction:
- Net Promoter Score (NPS)
- Customer Satisfaction Score (CSAT)
- User feedback rating

Business Impact:
- Time saved per assessment
- Skills gap identification rate
- Employee development plan completion
- ROI calculation
```

### 7.2 Retrospectives

**Sprint Retrospective** (Every 2 weeks):
```
Format: Start-Stop-Continue

What went well? (Continue)
- Fast bug resolution
- Good collaboration

What didn't go well? (Stop/Improve)
- Unclear requirements
- Too many meetings

Action Items:
1. [Owner] Task with due date
2. [Owner] Task with due date
```

**Release Retrospective** (After each major release):
```
Topics:
- Release process effectiveness
- Quality of delivered features
- Stakeholder satisfaction
- Lessons learned
- Process improvements
```

### 7.3 Technical Debt Management

**Debt Tracking**:
```
Track technical debt in backlog:
- Label: "tech-debt"
- Priority: Low/Medium/High
- Estimated effort
- Impact if not fixed

Allocate capacity:
- 20% of each sprint for tech debt
- Dedicated "tech debt sprint" quarterly
```

**Common Technical Debt Items**:
- Refactoring poorly structured code
- Upgrading dependencies
- Improving test coverage
- Performance optimization
- Documentation updates
- Security patches

### 7.4 Training & Knowledge Sharing

**Internal Training**:
- Weekly tech talks (30 minutes)
- Monthly knowledge sharing sessions
- Code review sessions
- Pair programming

**Documentation**:
- Architecture Decision Records (ADRs)
- Runbooks for operations
- API documentation (Swagger)
- User guides and tutorials

---

## 📋 Templates & Checklists

### User Story Template
```
Title: [As a <role>, I want <feature> so that <benefit>]

Description:
As a Manager,
I want to view skills gap for my team members,
So that I can create targeted development plans.

Acceptance Criteria:
- [ ] Can filter team members by job family
- [ ] Can see competency scores vs. target
- [ ] Can export gap analysis to Excel
- [ ] Gap is color-coded (red/yellow/green)

Technical Notes:
- Use existing Assessment API
- Calculate gap = target_level - assessed_level
- Cache results for 1 hour

Estimation: 5 story points
Priority: High
Sprint: Sprint 3
```

### Definition of Done
```
Code:
- [ ] Code written and follows style guide
- [ ] Code reviewed and approved
- [ ] Unit tests written (80%+ coverage)
- [ ] Integration tests written (if applicable)
- [ ] No linting errors or warnings

Documentation:
- [ ] Code comments for complex logic
- [ ] API documentation updated (if API changed)
- [ ] README updated (if setup changed)
- [ ] CHANGELOG updated

Testing:
- [ ] All tests passing
- [ ] Manual testing completed
- [ ] Security review completed (if needed)
- [ ] Performance benchmarks met

Deployment:
- [ ] Deployed to staging
- [ ] Smoke tests passed on staging
- [ ] Approved for production deployment
```

---

## 🔗 Tools & Resources

### Development Tools
| Tool | Purpose | Link |
|------|---------|------|
| VS Code | IDE | https://code.visualstudio.com/ |
| PyCharm | Python IDE | https://www.jetbrains.com/pycharm/ |
| Git | Version control | https://git-scm.com/ |
| Docker | Containerization | https://www.docker.com/ |
| Postman | API testing | https://www.postman.com/ |

### Testing Tools
| Tool | Purpose |
|------|---------|
| pytest | Python unit testing |
| coverage.py | Code coverage |
| Locust | Load testing |
| Playwright | E2E testing |
| Bandit | Security scanning |

### DevOps Tools
| Tool | Purpose |
|------|---------|
| GitHub Actions | CI/CD |
| Docker Compose | Container orchestration |
| Nginx | Web server / Load balancer |
| Supervisor | Process management |
| Prometheus | Monitoring |
| Grafana | Visualization |

---

## 📞 Contacts & Escalation

| Role | Contact | Availability |
|------|---------|--------------|
| **Tech Lead** | techlead@vnpt.vn | 24/7 (P0/P1) |
| **DevOps** | devops@vnpt.vn | 24/7 |
| **Security** | security@vnpt.vn | Business hours |
| **Product Owner** | po@vnpt.vn | Business hours |
| **Support** | support@vnpt.vn | 8AM-6PM Mon-Fri |

**Escalation Path**:
1. On-call Engineer (P0/P1)
2. Tech Lead (if not resolved in 30 min)
3. Engineering Manager (if not resolved in 2 hours)
4. CTO (for critical business impact)

---

## 📝 Document Control

**Version History**:
| Version | Date | Author | Changes |
|---------|------|--------|---------|
| 1.0 | 2025-11-22 | VNPT IT Team | Initial SDLC document |

**Review Schedule**: Quarterly  
**Next Review**: 2026-02-22  
**Document Owner**: Tech Lead  
**Approver**: Engineering Manager

---

**Questions?** Contact: tech@vnpt.vn  
**Feedback?** Create issue: https://github.com/vnpt/talent-hub/issues
