git clone https://github.com/vnpt/talent-hub.git
git checkout -b feature/my-feature
git commit -m "Add feature"
git push origin feature/my-feature
# VNPT Talent Hub

**Version**: 1.4.0  
**Status**: 🟢 Production Ready (Backend)  
**Security**: Phase 2 Complete (100%)

Unified competency and career development platform for VNPT staff. It enables employees to manage their skill profiles, managers to understand team capabilities, and administrators to curate the competency, career path, and user datasets that power gap analysis and strategic workforce planning.

## 🎯 Core Features
- **Employee Management**: Profile & self-service competency updates
- **Manager Tools**: Team view & competency assignment for direct reports
- **Admin CRUD**: Users + Employees (combined), Competencies, Career Paths
- **Career Path Modeling**: Required proficiency levels per competency
- **Skill Gap Analysis**: Employee vs target career path readiness & metrics
- **🔒 Security Features**:
  - Email verification system (24-hour tokens)
  - Rate limiting (5 login attempts/min, 10 user creations/hr)
  - Refresh token workflow (7-day sessions with rotation)
  - Comprehensive audit logging (30+ event types)
- **Authentication**: Secure JWT tokens + role-based authorization
- **API Features**: Pagination, search & filtering on key endpoints
- **Database**: Alembic migrations for schema evolution

## 🛠️ Tech Stack
- **Backend**: Python 3.11+ | FastAPI | SQLAlchemy ORM 2.x
- **Database**: PostgreSQL 14+ (with JSONB support)
- **Validation**: Pydantic v2
- **Migrations**: Alembic
- **Security**: Passlib/bcrypt, JWT, HttpOnly cookies
- **Rate Limiting**: In-memory (dev) + Redis (production)
- **Email**: SMTP integration ready

## Setup & Installation
```bash
# 1. Clone repository


# 2. Create and activate virtual environment
python -m venv .venv
# Windows
.venv\Scripts\activate
# macOS/Linux
source .venv/bin/activate

# 3. Install dependencies
pip install -r requirements.txt

# 4. Environment configuration
cp .env.example .env
# Edit .env -> set DATABASE_URL=postgresql+psycopg2://user:password@host:port/dbname
```

## Configuration
Create a `.env` file from `.env.example` and set at minimum:
- `DATABASE_URL` PostgreSQL connection string
- Optionally add security / JWT settings if extended later

Example:
```
DATABASE_URL=postgresql+psycopg2://talent:talent@localhost:5432/talent_hub
```

## Running the Application
Start the API locally (development hot reload):
```bash
uvicorn app.main:app --reload --port 8000
```
Open interactive docs:
- Swagger UI: http://localhost:8000/docs
- ReDoc: http://localhost:8000/redoc

## Database Migrations
Alembic manages schema changes. Typical workflow:
```bash
# Apply latest migrations
alembic upgrade head

# (Optional) Create new migration after model changes
alembic revision --autogenerate -m "describe change"
alembic upgrade head
```
Ensure `alembic.ini` points to the same `DATABASE_URL` value or uses env var injection in `env.py`.

## Project Structure
```
app/                # Application package
  api/              # FastAPI routers (endpoints & authorization rules)
  core/             # Core infrastructure (db, security)
  models/           # SQLAlchemy ORM models
  schemas/          # Pydantic request/response schemas
  services/         # Business logic & transactional operations
alembic/            # Migration environment & version scripts
data/               # Seed/reference CSV datasets
scripts/            # Helper scripts (create DB, import data, tunneling)
docs/               # Extended architectural & process documentation
tests/              # (Future) Automated test suites
```

## High-Level Flows
1. Admin creates users (with automatic employee profile) and defines career paths & competencies.
2. Employees update their own competency proficiency levels.
3. Managers assign / adjust competencies for direct reports.
4. Gap Analysis endpoint compares an employee against a target career path for readiness.

## Security & Roles
- Employee: Self profile & gap analysis for self.
- Manager: Team overview, assign/remove team member competencies, view direct report gap analyses.
- Admin: Full CRUD over users, employees, competencies, groups, career paths.

## API Conventions
- JSON responses with consistent success/error semantics (HTTPException for validation/auth failures).
- Pagination via `skip` & `limit` (caps enforced to avoid large payloads).
- Case-insensitive partial filtering on selected list endpoints (`name`, `email`, `department`, `role_name`).

## Development Guidelines
- Service layer encapsulates business rules & validation.
- Eager loading (`joinedload`) prevents N+1 query patterns on relationship-heavy endpoints.
- Transactions grouped (user + employee creation) with `flush()` for ID prefetch.

## Future Enhancements
See `NEXT_STEPS.md` for categorized roadmap items (analytics, workflow, advanced capabilities, security hardening).

## License & Ownership
Proprietary – VNPT Corporation. © 2025 VNPT. All rights reserved.

## Maintainers
VNPT IT Team

## Quick Commands Reference
```bash
# Run server
uvicorn app.main:app --reload --port 8000

# Apply migrations
alembic upgrade head

# Generate new migration
alembic revision --autogenerate -m "add new model"
```

---
For deeper architectural and process details consult `docs/` (e.g. `ARCHITECTURE.md`, `SECURITY.md`).

