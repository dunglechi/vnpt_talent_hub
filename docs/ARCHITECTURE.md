# System Architecture - VNPT Talent Hub

## 📐 Tổng quan Kiến trúc

VNPT Talent Hub được thiết kế theo kiến trúc **3-tier** với các nguyên tắc **SOLID** và **Clean Architecture**.

```
┌─────────────────────────────────────────────────────────────┐
│                    PRESENTATION LAYER                        │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐      │
│  │  Web Client  │  │ Mobile App   │  │  Admin Panel │      │
│  │ (React/Next) │  │(React Native)│  │   (React)    │      │
│  └──────────────┘  └──────────────┘  └──────────────┘      │
└─────────────────────────────────────────────────────────────┘
                         ↓ HTTPS/REST API
┌─────────────────────────────────────────────────────────────┐
│                   APPLICATION LAYER                          │
│  ┌──────────────────────────────────────────────────────┐   │
│  │              API Gateway (FastAPI)                    │   │
│  ├──────────────────────────────────────────────────────┤   │
│  │  Authentication  │  Authorization  │  Rate Limiting  │   │
│  └──────────────────────────────────────────────────────┘   │
│  ┌──────────────┐ ┌──────────────┐ ┌──────────────┐        │
│  │  Competency  │ │  Assessment  │ │   Employee   │        │
│  │   Service    │ │   Service    │ │   Service    │        │
│  └──────────────┘ └──────────────┘ └──────────────┘        │
└─────────────────────────────────────────────────────────────┘
                         ↓ SQLAlchemy ORM
┌─────────────────────────────────────────────────────────────┐
│                      DATA LAYER                              │
│  ┌────────────────────────────────────────────────────┐     │
│  │          PostgreSQL Database (Primary)             │     │
│  │  ┌──────────┐  ┌──────────┐  ┌──────────┐         │     │
│  │  │ Core     │  │ Auth     │  │ Analytics│         │     │
│  │  │ Tables   │  │ Tables   │  │ Tables   │         │     │
│  │  └──────────┘  └──────────┘  └──────────┘         │     │
│  └────────────────────────────────────────────────────┘     │
│  ┌────────────────────────────────────────────────────┐     │
│  │          Redis Cache (Optional)                    │     │
│  └────────────────────────────────────────────────────┘     │
└─────────────────────────────────────────────────────────────┘
```

## 🏗️ Technology Stack

### Backend
| Component | Technology | Version | Rationale |
|-----------|-----------|---------|-----------|
| **Web Framework** | FastAPI | 0.100+ | High performance, async support, automatic API docs |
| **ORM** | SQLAlchemy | 2.0+ | Mature, flexible, type-safe queries |
| **Database** | PostgreSQL | 14+ | ACID compliance, JSON support, scalability |
| **Validation** | Pydantic | 2.0+ | Fast validation, type hints |
| **Auth** | JWT | PyJWT | Stateless, scalable authentication |
| **Migration** | Alembic | 1.12+ | Version control for database schema |

**Why FastAPI?**
- ✅ Native async/await support → Better performance
- ✅ Automatic OpenAPI (Swagger) documentation
- ✅ Built-in validation with Pydantic
- ✅ Type hints → Better IDE support
- ✅ Fast development, production-ready

**Why PostgreSQL?**
- ✅ ACID transactions → Data integrity
- ✅ JSONB support → Flexible schema
- ✅ Full-text search → Competency search
- ✅ Window functions → Complex analytics
- ✅ Proven scalability at VNPT scale

### Frontend (Future)
| Component | Technology | Version | Rationale |
|-----------|-----------|---------|-----------|
| **Framework** | Next.js | 14+ | SSR/SSG, React 18, App Router |
| **Language** | TypeScript | 5.0+ | Type safety, better DX |
| **Styling** | Tailwind CSS | 3.0+ | Utility-first, fast development |
| **State** | Zustand | 4.0+ | Lightweight, simple API |
| **Forms** | React Hook Form | 7.0+ | Performance, validation |
| **API Client** | Axios | 1.6+ | Interceptors, error handling |

### Infrastructure
| Component | Technology | Rationale |
|-----------|-----------|-----------|
| **Web Server** | Nginx | Reverse proxy, load balancing |
| **Process Manager** | Supervisor | Auto-restart, logging |
| **Container** | Docker | Consistent environments |
| **CI/CD** | GitHub Actions | Automation, testing |
| **Monitoring** | Prometheus + Grafana | Metrics, alerting |

## 📊 Database Schema Design

### Entity Relationship Diagram

```
┌─────────────────────────┐
│   CompetencyGroup       │
│─────────────────────────│
│ PK id                   │
│    name                 │
│    code (CORE/LEAD/FUNC)│
└─────────────────────────┘
         │ 1
         │
         │ M
┌─────────────────────────┐       ┌─────────────────────────┐
│   Competency            │ M   1 │   JobFamily             │
│─────────────────────────│───────│─────────────────────────│
│ PK id                   │       │ PK id                   │
│ FK group_id             │       │ FK block_id             │
│ FK job_family_id (opt)  │       │    name                 │
│    name                 │       └─────────────────────────┘
│    code                 │                │ 1
│    definition           │                │
└─────────────────────────┘                │ M
         │ 1                    ┌─────────────────────────┐
         │                      │   JobBlock              │
         │ M                    │─────────────────────────│
┌─────────────────────────┐     │ PK id                   │
│   CompetencyLevel       │     │    name                 │
│─────────────────────────│     └─────────────────────────┘
│ PK id                   │
│ FK competency_id        │     ┌─────────────────────────┐
│    level (1-5)          │     │   JobSubFamily          │
│    description          │     │─────────────────────────│
└─────────────────────────┘     │ PK id                   │
                                │ FK family_id            │
         ┌─────────────────────│    name                 │
         │ 1                   └─────────────────────────┘
         │                                │ 1
         │ M                              │
┌─────────────────────────┐               │ M
│   Assessment            │    ┌─────────────────────────┐
│─────────────────────────│    │   Employee              │
│ PK id                   │  1 │─────────────────────────│
│ FK employee_id          │────│ PK id                   │
│ FK competency_id        │  M │ FK job_sub_family_id    │
│ FK assessor_id          │    │    name                 │
│    assessed_level       │    │    email                │
│    target_level         │    └─────────────────────────┘
│    notes                │
│    assessment_date      │
└─────────────────────────┘
```

### Indexing Strategy

```sql
-- High-frequency queries
CREATE INDEX idx_competency_group ON competencies(group_id);
CREATE INDEX idx_competency_job_family ON competencies(job_family_id);
CREATE INDEX idx_employee_email ON employees(email);
CREATE INDEX idx_assessment_employee ON assessments(employee_id);
CREATE INDEX idx_assessment_date ON assessments(assessment_date DESC);

-- Composite indexes for common queries
CREATE INDEX idx_assessment_emp_comp ON assessments(employee_id, competency_id);
CREATE INDEX idx_employee_job ON employees(job_sub_family_id);
```

## 🔄 API Design Principles

### RESTful Conventions
```
GET    /api/v1/competencies           # List all
GET    /api/v1/competencies/{id}      # Get one
POST   /api/v1/competencies           # Create
PUT    /api/v1/competencies/{id}      # Update
DELETE /api/v1/competencies/{id}      # Delete
```

### Versioning
- **URL versioning**: `/api/v1/`, `/api/v2/`
- Major version changes when breaking compatibility
- Support N-1 version for 6 months

### Response Structure
```json
{
  "success": true,
  "data": { ... },
  "meta": {
    "timestamp": "2025-11-22T10:30:00Z",
    "version": "1.0"
  }
}
```

### Error Response
```json
{
  "success": false,
  "error": {
    "code": "VALIDATION_ERROR",
    "message": "Invalid input data",
    "details": {
      "email": ["Invalid email format"]
    }
  },
  "meta": {
    "timestamp": "2025-11-22T10:30:00Z"
  }
}
```

## 🔐 Security Architecture

### Authentication Flow
```
1. User → POST /auth/login {email, password}
2. API → Validate credentials
3. API → Generate JWT token
4. API → Return {access_token, refresh_token}
5. User → Include "Authorization: Bearer {token}" in requests
6. API → Validate token on each request
```

### JWT Token Structure
```json
{
  "header": {
    "alg": "HS256",
    "typ": "JWT"
  },
  "payload": {
    "sub": "user_id",
    "email": "user@vnpt.vn",
    "role": "employee",
    "exp": 1700000000,
    "iat": 1699999000
  }
}
```

## 📈 Scalability Strategy

### Horizontal Scaling
```
┌────────────┐
│   Nginx    │ Load Balancer
│            │
└────────────┘
      │
      ├──────────┬──────────┬──────────┐
      │          │          │          │
┌──────▼────┐ ┌──▼──────┐ ┌──▼──────┐ ┌──▼──────┐
│ FastAPI 1 │ │FastAPI 2│ │FastAPI 3│ │FastAPI N│
└───────────┘ └─────────┘ └─────────┘ └─────────┘
      │          │          │          │
      └──────────┴──────────┴──────────┘
                  │
      ┌───────────▼────────────┐
      │   PostgreSQL Primary   │
      │    (Read/Write)        │
      └────────────────────────┘
                  │
      ┌───────────┴────────────┐
      │                        │
┌─────▼──────┐          ┌──────▼─────┐
│  Replica 1 │          │ Replica 2  │
│ (Read-only)│          │(Read-only) │
└────────────┘          └────────────┘
```

### Caching Strategy
```python
# 1. Application-level cache (Redis)
@cache(ttl=3600)
def get_competency_list(group_code: str):
    return db.query(Competency).filter_by(group_code=group_code).all()

# 2. Database query cache
# PostgreSQL shared_buffers, effective_cache_size

# 3. HTTP caching headers
@app.get("/api/competencies")
async def list_competencies():
    return Response(
        headers={
            "Cache-Control": "public, max-age=3600",
            "ETag": generate_etag(data)
        }
    )
```

### Database Optimization
```python
# 1. Eager loading (N+1 problem solution)
competencies = db.query(Competency)\
    .options(joinedload(Competency.levels))\
    .options(joinedload(Competency.group))\
    .all()

# 2. Pagination
def paginate(query, page: int, per_page: int = 20):
    return query.offset((page - 1) * per_page).limit(per_page)

# 3. Partial updates
db.query(Employee).filter_by(id=emp_id).update(
    {"name": new_name},
    synchronize_session=False
)
```

## 🧪 Testing Strategy

### Testing Pyramid
```
        ┌───────┐
        │  E2E  │  10% - Critical user journeys
        └───────┘
      ┌───────────┐
      │Integration│  30% - API endpoints, DB
      └───────────┘
    ┌───────────────┐
    │  Unit Tests   │  60% - Business logic
    └───────────────┘
```

### Test Coverage Goals
- **Unit Tests**: 80%+ code coverage
- **Integration Tests**: All API endpoints
- **E2E Tests**: Critical user flows
- **Performance Tests**: Load testing for 100+ concurrent users

## 🔄 Deployment Pipeline

```
┌─────────────┐
│   Commit    │
│   to Git    │
└──────┬──────┘
       │
       ▼
┌─────────────┐
│  Run Tests  │ ← GitHub Actions
│  (pytest)   │
└──────┬──────┘
       │
       ▼
┌─────────────┐
│Build Docker │
│   Image     │
└──────┬──────┘
       │
       ▼
┌─────────────┐
│Deploy to    │
│  Staging    │
└──────┬──────┘
       │
       ▼
┌─────────────┐
│  Manual     │
│  Approval   │
└──────┬──────┘
       │
       ▼
┌─────────────┐
│Deploy to    │
│ Production  │
└─────────────┘
```

## 🎯 Design Patterns Used

### 1. Repository Pattern
```python
class CompetencyRepository:
    def __init__(self, db: Session):
        self.db = db
    
    def get_all(self) -> List[Competency]:
        return self.db.query(Competency).all()
    
    def get_by_id(self, id: int) -> Optional[Competency]:
        return self.db.query(Competency).filter_by(id=id).first()
```

### 2. Service Layer Pattern
```python
class CompetencyService:
    def __init__(self, repo: CompetencyRepository):
        self.repo = repo
    
    def create_competency(self, data: CompetencyCreate) -> Competency:
        # Business logic here
        competency = Competency(**data.dict())
        return self.repo.create(competency)
```

### 3. Dependency Injection
```python
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

@app.get("/api/competencies")
def list_competencies(db: Session = Depends(get_db)):
    return CompetencyService(db).get_all()
```

## 📊 Performance Targets

| Metric | Target | Current |
|--------|--------|---------|
| API Response Time (p95) | < 200ms | TBD |
| Database Query Time | < 50ms | ✅ Fast |
| Page Load Time | < 2s | N/A |
| Concurrent Users | 100+ | N/A |
| Uptime | 99.9% | TBD |

## 🔮 Future Architecture

### Phase 2: Microservices (Optional)
```
┌──────────────────┐  ┌──────────────────┐  ┌──────────────────┐
│  Competency      │  │   Assessment     │  │   Employee       │
│   Service        │  │    Service       │  │   Service        │
│  (FastAPI)       │  │   (FastAPI)      │  │   (FastAPI)      │
└────────┬─────────┘  └────────┬─────────┘  └────────┬─────────┘
         │                     │                      │
         └─────────────────────┴──────────────────────┘
                           │
                  ┌────────▼────────┐
                  │  API Gateway    │
                  │   (Kong/Nginx)  │
                  └─────────────────┘
```

### Phase 3: Event-Driven Architecture
```
┌──────────┐     ┌──────────────┐     ┌──────────┐
│  Service │────▶│ Message Bus  │────▶│ Service  │
│    A     │     │  (RabbitMQ)  │     │    B     │
└──────────┘     └──────────────┘     └──────────┘
```

## 📞 Architecture Review

**Architecture Team**: arch@vnpt.vn  
**Review Schedule**: Quarterly  
**Last Review**: 2025-11-22  
**Next Review**: 2026-02-22

---

**Document Version**: 1.0  
**Author**: VNPT IT Team  
**Status**: Living Document