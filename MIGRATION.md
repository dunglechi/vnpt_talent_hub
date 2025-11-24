# Migration Guide: Old Structure → New Structure

## 🔄 Restructuring Summary

### What Changed?

The project has been reorganized into a professional Python package structure:

```
OLD STRUCTURE:                   NEW STRUCTURE:
├── database.py              →   ├── app/
├── models.py                →   │   ├── core/
├── create_database.py       →   │   │   └── database.py
├── create_tables.py         →   │   └── models/
├── import_data.py           →   │       ├── competency.py
├── ssh_tunnel.py            →   │       ├── job.py
├── *.md                     →   │       └── employee.py
                             →   ├── scripts/
                             →   │   ├── create_database.py
                             →   │   ├── create_tables.py
                             →   │   ├── import_data.py
                             →   │   └── ssh_tunnel.py
                             →   ├── docs/
                             →   │   ├── *.md (all documentation)
                             →   └── config/ (future)
```

## 📦 Import Path Changes

### Old Imports (DON'T USE):
```python
from database import SessionLocal, Base, engine
from models import Competency, CompetencyGroup, Employee
```

### New Imports (USE THESE):
```python
from app.core.database import SessionLocal, Base, engine
from app.models import Competency, CompetencyGroup, Employee
# Or import specific models:
from app.models.competency import Competency, CompetencyGroup
from app.models.employee import Employee
```

## 🔧 Command Changes

### Old Commands:
```bash
python create_database.py
python create_tables.py
python import_data.py
python ssh_tunnel.py
```

### New Commands:
```bash
python scripts/create_database.py
python scripts/create_tables.py
python scripts/import_data.py
python scripts/ssh_tunnel.py
```

## ✅ Verification Steps

### 1. Test Imports
```bash
python -c "from app.core.database import SessionLocal; from app.models import Competency; print('✓ Imports OK')"
```

### 2. Test Database Connection
```bash
python -c "from app.core.database import SessionLocal; db = SessionLocal(); print('✓ Database OK')"
```

### 3. Test Scripts
```bash
# Should show help/success message
python scripts/ssh_tunnel.py
```

## 🗑️ Cleanup Old Files

After verifying everything works:

```bash
# Run cleanup script
python cleanup_old_files.py
```

This will remove:
- `database.py`
- `models.py`
- `create_database.py`
- `create_tables.py`
- `import_data.py`
- `ssh_tunnel.py`
- `__pycache__/` directories

## 📝 Update Your Code

If you have custom scripts using the old structure:

### Example: Old Script
```python
# old_script.py
from database import SessionLocal
from models import Competency

db = SessionLocal()
comps = db.query(Competency).all()
```

### Updated Script
```python
# new_script.py
from app.core.database import SessionLocal
from app.models import Competency

db = SessionLocal()
comps = db.query(Competency).all()
```

## 🚀 Benefits of New Structure

1. **Professional Organization**: Follows Python package best practices
2. **Scalability**: Easy to add new modules (api/, services/, etc.)
3. **Cleaner Root**: Documentation and scripts separated
4. **Better IDE Support**: Proper package structure improves autocomplete
5. **Easier Testing**: Test files can mirror app/ structure
6. **Future-Ready**: Ready for FastAPI, Alembic, testing frameworks

## 📚 New Documentation Structure

All documentation is now in `docs/`:

| File | Description |
|------|-------------|
| `docs/README.md` | Detailed project documentation |
| `docs/GETTING_STARTED.md` | Quick start guide |
| `docs/ARCHITECTURE.md` | System architecture |
| `docs/DEPLOYMENT.md` | Production deployment |
| `docs/SECURITY.md` | Security policies |
| `docs/FAQ.md` | Common questions |
| `docs/CONTRIBUTING.md` | Contribution guidelines |
| `docs/API_SPECS.md` | API documentation (future) |
| `docs/CHANGELOG.md` | Version history |
| `docs/TODO.md` | Project roadmap |

## ⚙️ IDE Configuration

### VS Code
Update `.vscode/settings.json`:
```json
{
  "python.analysis.extraPaths": ["${workspaceFolder}"],
  "python.autoComplete.extraPaths": ["${workspaceFolder}"]
}
```

### PyCharm
Mark `vnpt-talent-hub/` as Sources Root (right-click folder → Mark Directory as → Sources Root)

## 🔗 Related Files

- `README.md` - Updated with new structure
- `docs/GETTING_STARTED.md` - Updated examples
- `cleanup_old_files.py` - Script to remove old files

## 📞 Support

Questions about migration? Check:
- `docs/FAQ.md` - Common migration questions
- GitHub Issues - Report migration problems
- tech@vnpt.vn - Technical support

---

**Migration Date**: 2025-11-22  
**Version**: 1.0.0 → 1.1.0  
**Status**: ✅ Complete
