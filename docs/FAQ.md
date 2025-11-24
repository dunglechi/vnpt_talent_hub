# FAQ - VNPT Talent Hub

## ❓ Câu hỏi Thường gặp

### 📚 Tổng quan

**Q: VNPT Talent Hub là gì?**  
A: VNPT Talent Hub là hệ thống quản lý năng lực nhân sự của VNPT, giúp đánh giá, theo dõi và phát triển năng lực của nhân viên dựa trên framework năng lực chuẩn hóa.

**Q: Hệ thống này dành cho ai?**  
A: 
- **HR Manager**: Xây dựng framework năng lực, theo dõi toàn bộ tổ chức
- **Manager**: Đánh giá năng lực team, lập kế hoạch đào tạo
- **Employee**: Xem năng lực hiện tại, tự đánh giá, đặt mục tiêu phát triển
- **Admin**: Quản trị hệ thống, quản lý users

**Q: Tôi cần quyền gì để truy cập?**  
A: Liên hệ HR Manager hoặc Admin để được cấp tài khoản. Mỗi nhân viên VNPT sẽ có account với role phù hợp.

---

## 🚀 Bắt đầu Nhanh

**Q: Làm sao để chạy project lần đầu tiên?**  
A: 
```bash
# 1. Clone repository
git clone <repo-url>
cd vnpt-talent-hub

# 2. Tạo virtual environment
python -m venv venv
venv\Scripts\activate  # Windows
source venv/bin/activate  # Linux/Mac

# 3. Cài dependencies
pip install -r requirements.txt

# 4. Thiết lập SSH tunnel
ssh -L 5432:localhost:5432 admin@one.vnptacademy.com.vn -p 2222 -N

# 5. Tạo database (chạy 1 lần)
python create_database.py
python create_tables.py

# 6. Import data (nếu database trống)
python import_data.py
```

**Q: Tôi có cần cài PostgreSQL trên máy không?**  
A: **Không cần**. Database chạy trên server remote `one.vnptacademy.com.vn`. Bạn chỉ cần thiết lập SSH tunnel để kết nối.

**Q: File .env là gì và làm sao tạo?**  
A: Tạo file `.env` ở root folder:
```
DATABASE_URL=postgresql://postgres:Cntt%402025@localhost:5432/vnpt_talent_hub
SECRET_KEY=your-secret-key-here
```

---

## 🔧 Cài đặt & Cấu hình

**Q: Tôi gặp lỗi "ModuleNotFoundError: No module named 'sqlalchemy'"?**  
A: Bạn chưa cài dependencies. Chạy:
```bash
pip install -r requirements.txt
```

**Q: Lỗi "connection refused" khi kết nối database?**  
A: Kiểm tra:
1. SSH tunnel có chạy không? `ssh -L 5432:localhost:5432 admin@one.vnptacademy.com.vn -p 2222 -N`
2. File `.env` có đúng DATABASE_URL không?
3. Password trong URL đã escape chưa? (@ → %40)

**Q: Làm sao kiểm tra SSH tunnel đang chạy?**  
A: 
```bash
# Windows
netstat -ano | findstr :5432

# Linux/Mac
lsof -i :5432
```
Nếu thấy LISTENING trên port 5432 → tunnel OK.

**Q: Tôi muốn chạy SSH tunnel ở background?**  
A: 
```bash
# Linux/Mac
ssh -f -L 5432:localhost:5432 admin@one.vnptacademy.com.vn -p 2222 -N

# Windows: Dùng PuTTY hoặc MobaXterm để save session
```

**Q: Làm sao xem các table trong database?**  
A: Kết nối bằng pgAdmin hoặc DBeaver:
- Host: `localhost`
- Port: `5432`
- Database: `vnpt_talent_hub`
- Username: `postgres`
- Password: `Cntt@2025`

---

## 📊 Dữ liệu & Import

**Q: Import data mất bao lâu?**  
A: Khoảng 10-30 giây tùy thuộc tốc độ mạng. Các bước:
1. Import job structure: ~5s
2. Import competency groups: ~1s
3. Import competencies: ~10-20s

**Q: Lỗi "csv file not found" khi import?**  
A: Kiểm tra folder `data/` có đủ các file CSV không:
- `job_families.csv`
- `competencies_core.csv`
- `competencies_leadership.csv`
- `competencies_functional_ops.csv`
- `competencies_functional_tech.csv`

**Q: Import data nhiều lần có bị duplicate không?**  
A: **Có**. Script hiện tại chưa check duplicate. Để reset database:
```python
# Xóa tất cả data
from database import SessionLocal, engine
from models import Base

Base.metadata.drop_all(bind=engine)  # Xóa tables
Base.metadata.create_all(bind=engine)  # Tạo lại
```

**Q: Làm sao thêm competency mới?**  
A: 
- **Cách 1**: Thêm vào CSV file và re-import
- **Cách 2**: Insert trực tiếp vào database
```python
from database import SessionLocal
from models import Competency

db = SessionLocal()
new_comp = Competency(
    name="Python Programming",
    code="PYTHON",
    definition="Ability to code in Python",
    group_id=1,
    job_family_id=5
)
db.add(new_comp)
db.commit()
```

**Q: Competency có bao nhiêu level?**  
A: **5 levels**:
1. **Level 1**: Basic/Beginner
2. **Level 2**: Intermediate
3. **Level 3**: Advanced
4. **Level 4**: Expert
5. **Level 5**: Master/Thought Leader

---

## 🐛 Troubleshooting

**Q: Lỗi "FATAL: password authentication failed"?**  
A: Nguyên nhân:
- Password sai trong `.env`
- Ký tự đặc biệt chưa escape (@ → %40, # → %23)
- User không có quyền truy cập database

Fix:
```bash
# Kiểm tra password
DATABASE_URL=postgresql://postgres:Cntt%402025@localhost:5432/vnpt_talent_hub
```

**Q: Lỗi "database vnpt_talent_hub does not exist"?**  
A: Database chưa được tạo. Chạy:
```bash
python create_database.py
```

**Q: Import script báo lỗi "KeyError: 'Tên Năng lực'"?**  
A: CSV file có cột tên khác. Script hỗ trợ nhiều tên cột:
- `Tên Năng lực`
- `Tên năng lực`
- `Tên`
- `Ten`

Kiểm tra header của CSV file.

**Q: Chạy script báo "AttributeError: 'Competency' object has no attribute 'name_en'"?**  
A: Model đã thay đổi. Cập nhật script hoặc thêm field vào model:
```python
# models.py
class Competency(Base):
    # ...
    name_en = Column(String(200), nullable=True)  # Optional English name
```

**Q: Query database rất chậm?**  
A: Kiểm tra:
1. Có đang dùng SSH tunnel không? (có thể chậm hơn direct connection)
2. Query có dùng JOIN nhiều không?
3. Index có đủ không?

Optimize:
```python
# Thêm index
from sqlalchemy import Index
Index('idx_competency_group', Competency.group_id)

# Dùng eager loading
competencies = db.query(Competency)\
    .options(joinedload(Competency.levels))\
    .all()
```

---

## 🔐 Bảo mật

**Q: Tôi có thể commit file .env lên Git không?**  
A: **KHÔNG**. File `.env` chứa credentials nhạy cảm. Đã được thêm vào `.gitignore`.

**Q: Làm sao bảo vệ database password?**  
A: 
- Dùng environment variables (`.env`)
- Không hardcode trong code
- Không commit credentials lên Git
- Thay đổi password định kỳ

**Q: SSH tunnel có an toàn không?**  
A: **Có**. SSH tunnel encrypt tất cả traffic giữa máy bạn và server. Tương đương với VPN.

---

## 🏗️ Development

**Q: Làm sao thêm table mới?**  
A: 
1. Định nghĩa model trong `models.py`:
```python
class Assessment(Base):
    __tablename__ = 'assessments'
    id = Column(Integer, primary_key=True)
    employee_id = Column(Integer, ForeignKey('employees.id'))
    # ...
```

2. Tạo table:
```python
python create_tables.py
```

**Q: Làm sao thay đổi cấu trúc table đã có?**  
A: Dùng **Alembic** (database migration tool):
```bash
# 1. Init Alembic
alembic init alembic

# 2. Tạo migration
alembic revision --autogenerate -m "Add column to competency"

# 3. Apply migration
alembic upgrade head
```

**Q: Có cần viết test không?**  
A: **Nên có**. Đặc biệt với business logic. Example:
```python
# test_competency.py
def test_create_competency():
    comp = Competency(name="Test", code="TEST")
    assert comp.name == "Test"
    assert comp.code == "TEST"
```

Chạy test:
```bash
pytest tests/
```

**Q: Làm sao debug query SQL?**  
A: Enable logging:
```python
# database.py
engine = create_engine(
    SQLALCHEMY_DATABASE_URL,
    echo=True  # Print all SQL queries
)
```

---

## 🚀 Deployment

**Q: Làm sao deploy lên production?**  
A: Xem chi tiết trong `DEPLOYMENT.md`. Tóm tắt:
1. Setup Ubuntu server
2. Cài PostgreSQL, Nginx, Supervisor
3. Clone code, cài dependencies
4. Configure environment
5. Run with Supervisor
6. Setup SSL với Let's Encrypt

**Q: Tôi có thể chạy với Docker không?**  
A: Chưa có Dockerfile, nhưng có thể tạo:
```dockerfile
FROM python:3.11
WORKDIR /app
COPY requirements.txt .
RUN pip install -r requirements.txt
COPY . .
CMD ["python", "main.py"]
```

**Q: Làm sao backup database?**  
A: 
```bash
# Backup
pg_dump -U postgres -h localhost -p 5432 vnpt_talent_hub > backup.sql

# Restore
psql -U postgres -h localhost -p 5432 vnpt_talent_hub < backup.sql
```

Hoặc dùng script tự động trong `DEPLOYMENT.md`.

---

## 📈 Performance

**Q: Hệ thống support bao nhiêu users?**  
A: Hiện tại chưa load test. Ước tính:
- Database: 10,000+ employees
- Concurrent users: 100+ (với optimization)
- Response time: < 200ms (API calls)

**Q: Làm sao tăng performance?**  
A: 
1. **Caching**: Dùng Redis cache cho queries thường dùng
2. **Indexing**: Thêm index trên các cột query nhiều
3. **Connection pooling**: SQLAlchemy pool_size=20
4. **Async**: Chuyển sang async SQLAlchemy
5. **CDN**: Serve static files từ CDN

**Q: Database connection pool là gì?**  
A: Tập hợp các connection đã mở sẵn để tái sử dụng, tránh overhead của việc tạo connection mới mỗi request.
```python
engine = create_engine(
    DATABASE_URL,
    pool_size=20,        # Max 20 connections
    max_overflow=10,     # Thêm 10 khi cần
    pool_timeout=30      # Timeout 30s
)
```

---

## 🔄 API (Future)

**Q: Khi nào có API?**  
A: Đang trong roadmap Phase 2. Dự kiến dùng FastAPI.

**Q: API sẽ có những endpoint nào?**  
A: Xem chi tiết trong `API_SPECS.md`. Ví dụ:
- `GET /api/competencies` - List competencies
- `GET /api/employees/{id}/skills` - Get employee skills
- `POST /api/assessments` - Create assessment

**Q: Authentication sẽ dùng gì?**  
A: **JWT tokens** (JSON Web Tokens). Flow:
1. Login → Nhận access_token
2. Gửi token trong header: `Authorization: Bearer {token}`
3. Server verify token

---

## 📞 Liên hệ & Hỗ trợ

**Q: Tôi cần trợ giúp, liên hệ ai?**  
A: 
- **Technical support**: tech@vnpt.vn
- **Bug report**: [GitHub Issues](https://github.com/vnpt/talent-hub/issues)
- **Feature request**: product@vnpt.vn
- **Security issues**: security@vnpt.vn

**Q: Có tài liệu chi tiết hơn không?**  
A: Có! Xem các file:
- `README.md` - Tổng quan dự án
- `ARCHITECTURE.md` - Kiến trúc hệ thống
- `API_SPECS.md` - API documentation (future)
- `DEPLOYMENT.md` - Hướng dẫn deploy
- `SECURITY.md` - Chính sách bảo mật
- `CONTRIBUTING.md` - Hướng dẫn đóng góp

**Q: Làm sao contribute code?**  
A: 
1. Fork repository
2. Tạo branch: `git checkout -b feature/my-feature`
3. Commit: `git commit -m "Add feature"`
4. Push: `git push origin feature/my-feature`
5. Tạo Pull Request

Chi tiết xem `CONTRIBUTING.md`.

---

## 🔍 Khác

**Q: VNPT có bao nhiêu competency group?**  
A: **3 groups**:
1. **CORE**: Năng lực cốt lõi (áp dụng cho tất cả nhân viên)
2. **LEAD**: Năng lực lãnh đạo (cho quản lý)
3. **FUNC**: Năng lực chuyên môn (theo job family)

**Q: Sự khác biệt giữa Job Family và Job Sub-Family?**  
A: 
- **Job Block**: Khối công việc (VD: Technology, Operations)
- **Job Family**: Nhóm công việc (VD: Software Development, Network Engineering)
- **Job Sub-Family**: Chuyên môn cụ thể (VD: Backend Developer, Frontend Developer)

Example:
```
Block: Technology
  ├─ Family: Software Development
  │   ├─ Sub-Family: Backend Developer
  │   ├─ Sub-Family: Frontend Developer
  │   └─ Sub-Family: Mobile Developer
  └─ Family: Network Engineering
      ├─ Sub-Family: Network Administrator
      └─ Sub-Family: Security Engineer
```

**Q: Functional competencies áp dụng như thế nào?**  
A: Mỗi Job Family có một set functional competencies riêng. VD:
- **Software Development**: Python, Java, System Design, Code Review
- **Network Engineering**: Cisco, Routing, Firewall, Network Monitoring

**Q: Có tool nào để visualize competency framework không?**  
A: Chưa có. Đang trong roadmap. Tạm thời có thể:
1. Query database export ra Excel
2. Dùng tools như draw.io để vẽ diagram
3. Dùng Python libraries (matplotlib, networkx) để generate graph

**Q: Hệ thống có mobile app không?**  
A: Chưa có. Trong roadmap Phase 3. Dự kiến dùng React Native.

---

## 📝 Cập nhật & Changelog

**Q: Làm sao biết version hiện tại?**  
A: Xem file `CHANGELOG.md` hoặc:
```python
from database import __version__
print(__version__)
```

**Q: Có tự động update không?**  
A: Không. Cần pull code mới từ Git và apply migrations:
```bash
git pull origin main
pip install -r requirements.txt
alembic upgrade head
```

**Q: Breaking changes được thông báo như thế nào?**  
A: 
- Ghi trong `CHANGELOG.md` với tag `[BREAKING]`
- Email thông báo đến tất cả developers
- Migration guide trong release notes

---

**Last Updated**: 2025-11-22  
**Version**: 1.0  
**Maintainer**: VNPT IT Team

💡 **Không tìm thấy câu trả lời?** Tạo issue trên GitHub hoặc email tech@vnpt.vn