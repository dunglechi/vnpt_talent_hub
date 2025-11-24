# Database Migrations - Alembic

## Current Migrations

### 456fa548982a - Add Users Table (2025-11-22)
**Status**: ✅ Applied

Creates `users` table for authentication:
- id, email (unique), hashed_password
- full_name, role (admin/manager/user)
- is_active, is_verified, timestamps
- Indexes on id and email

**Apply**: `alembic upgrade head`  
**Rollback**: `alembic downgrade -1`

---

## Alembic Commands

```bash
# View current version
alembic current

# Create new migration
alembic revision --autogenerate -m "description"

# Apply migrations
alembic upgrade head

# Rollback last
alembic downgrade -1

# View history
alembic history
```

---

## Configuration

**Database URL**: `.env` → `DATABASE_URL`  
**Alembic Config**: `alembic.ini`  
**Migrations**: `alembic/versions/`

Current: `postgresql://postgres:***@localhost:1234/vnpt_talent_hub`
