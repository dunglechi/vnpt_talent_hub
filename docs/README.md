# VNPT Talent Hub - Hệ thống Quản lý Khung Năng lực Nhân sự

## 📋 Tổng quan Dự án

**VNPT Talent Hub** là hệ thống quản lý khung năng lực nhân sự của VNPT, giúp đánh giá, phát triển và theo dõi năng lực của nhân viên theo các chuẩn mực được định nghĩa.

### Thông tin Server
- **Domain**: one.vnptacademy.com.vn
- **OS**: Ubuntu 22.04.5 LTS
- **Database**: PostgreSQL 14.19
- **SSH Port**: 2222
- **Credentials**: admin / Cntt@2025

## 🏗️ Kiến trúc Hệ thống

### Backend
- **Ngôn ngữ**: Python 3.14
- **ORM**: SQLAlchemy
- **Database Driver**: psycopg2-binary
- **Kết nối**: SSH Tunnel qua port 2222

### Database Schema

```
┌─────────────────────┐
│ CompetencyGroup     │
│ - id                │
│ - name              │
│ - code (CORE/LEAD/  │
│   FUNC)             │
└─────────────────────┘
         │
         ├──────────────────────┐
         │                      │
┌────────▼────────┐    ┌───────▼────────┐
│ Competency      │    │ JobBlock       │
│ - id            │    │ - id           │
│ - name          │    │ - name         │
│ - code          │    └────────┬───────┘
│ - definition    │             │
│ - group_id (FK) │    ┌────────▼────────┐
│ - job_family_id │    │ JobFamily       │
│   (FK)          │◄───┤ - id            │
└────────┬────────┘    │ - name          │
         │             │ - block_id (FK) │
┌────────▼────────┐    └────────┬────────┘
│CompetencyLevel  │             │
│ - id            │    ┌────────▼────────┐
│ - level (1-5)   │    │ JobSubFamily    │
│ - description   │    │ - id            │
│ - competency_id │    │ - name          │
│   (FK)          │    │ - family_id (FK)│
└─────────────────┘    └────────┬────────┘
                                │
                       ┌────────▼────────┐
                       │ Employee        │
                       │ - id            │
                       │ - name          │
                       │ - email         │
                       │ - job_sub_      │
                       │   family_id(FK) │
                       └─────────────────┘
```

## 📊 Dữ liệu Đã Import

### 1. Cấu trúc Công việc
- **Job Blocks**: Các khối công việc chính
- **Job Families**: Họ công việc theo từng khối
- **Job Sub-families**: Họ công việc con chi tiết

### 2. Nhóm Năng lực
- **CORE** - Năng lực Chung (10 năng lực)
- **LEAD** - Năng lực Lãnh đạo (5 năng lực)
- **FUNC** - Năng lực Chuyên môn (theo họ công việc)

### 3. Chi tiết Năng lực
Mỗi năng lực bao gồm:
- Tên và định nghĩa
- 5 cấp độ thành thạo (Level 1-5)
- Mô tả hành vi cụ thể cho từng cấp độ
- Liên kết với họ công việc (đối với năng lực chuyên môn)

## 🚀 Cài đặt và Triển khai

### Yêu cầu Hệ thống
```bash
Python >= 3.10
PostgreSQL >= 14
SSH Client
```

### Cài đặt Dependencies
```bash
pip install -r requirements.txt
```

**File requirements.txt**:
```
sqlalchemy==2.0.44
psycopg2-binary==2.9.11
pandas==2.3.3
python-dotenv==1.2.1
```

### Cấu hình Kết nối

1. **Tạo SSH Tunnel** (Terminal 1):
```bash
ssh -L 5432:localhost:5432 admin@one.vnptacademy.com.vn -p 2222 -N
# Nhập password: Cntt@2025
```

2. **Cấu hình .env**:
```env
DATABASE_URL=postgresql://postgres:Cntt%402025@localhost:5432/vnpt_talent_hub
```

### Khởi tạo Database

```bash
# Bước 1: Tạo database
python create_database.py

# Bước 2: Tạo bảng
python create_tables.py

# Bước 3: Import dữ liệu
python import_data.py
```

## 📁 Cấu trúc Thư mục

```
vnpt-talent-hub/
├── data/                              # Dữ liệu CSV
│   ├── job_families.csv
│   ├── competencies_core.csv
│   ├── competencies_leadership.csv
│   ├── competencies_functional_ops.csv
│   └── competencies_functional_tech.csv
├── database.py                        # Cấu hình database
├── models.py                          # SQLAlchemy models
├── create_database.py                 # Script tạo database
├── create_tables.py                   # Script tạo bảng
├── import_data.py                     # Script import dữ liệu
├── ssh_tunnel.py                      # Utility tạo SSH tunnel
├── .env                               # Cấu hình môi trường
├── requirements.txt                   # Python dependencies
└── README.md                          # File này
```

## 🔧 Các Scripts Chính

### 1. `database.py`
Quản lý kết nối database, tạo engine và session.

### 2. `models.py`
Định nghĩa 7 bảng chính:
- CompetencyGroup
- Competency
- CompetencyLevel
- JobBlock
- JobFamily
- JobSubFamily
- Employee

### 3. `create_database.py`
Tạo database `vnpt_talent_hub` nếu chưa tồn tại.

### 4. `create_tables.py`
Tạo tất cả bảng theo schema đã định nghĩa.

### 5. `import_data.py`
Import dữ liệu từ CSV với logic:
- Xử lý cấu trúc công việc (Block → Family → SubFamily)
- Tạo nhóm năng lực (CORE, LEAD, FUNC)
- Import năng lực và cấp độ
- Liên kết năng lực chuyên môn với họ công việc

### 6. `ssh_tunnel.py`
Utility hỗ trợ tạo SSH tunnel tự động.

## ⚙️ Vận hành

### Kết nối Database
```python
from database import SessionLocal

# Tạo session
session = SessionLocal()

# Truy vấn
from models import Competency
competencies = session.query(Competency).all()

# Đóng session
session.close()
```

### Truy vấn Mẫu

**1. Lấy tất cả năng lực chung**:
```python
core_group = session.query(CompetencyGroup).filter_by(code='CORE').first()
core_competencies = core_group.competencies
```

**2. Lấy năng lực theo cấp độ**:
```python
competency = session.query(Competency).filter_by(name='Định hướng mục tiêu và kết quả').first()
levels = competency.levels  # Tất cả 5 cấp độ
```

**3. Lấy năng lực chuyên môn của một họ công việc**:
```python
job_family = session.query(JobFamily).filter_by(name='Kỹ thuật viên').first()
functional_competencies = job_family.competencies
```

## 🔒 Bảo mật

- ✅ Password được mã hóa trong URL (@ → %40)
- ✅ Kết nối qua SSH Tunnel
- ✅ File .env không được commit (thêm vào .gitignore)
- ✅ Chỉ mở port 2222, các port khác đóng

## 📈 Roadmap

### Phase 1: Backend API (Hiện tại)
- [x] Thiết kế database schema
- [x] Import dữ liệu cơ bản
- [ ] RESTful API với FastAPI
- [ ] Authentication & Authorization
- [ ] API Documentation (Swagger)

### Phase 2: Frontend
- [ ] React/Next.js Dashboard
- [ ] Quản lý nhân viên
- [ ] Đánh giá năng lực
- [ ] Báo cáo và thống kê

### Phase 3: Tính năng Nâng cao
- [ ] Gợi ý lộ trình phát triển
- [ ] So sánh năng lực theo vị trí
- [ ] Export báo cáo PDF/Excel
- [ ] Tích hợp LMS

## 🐛 Troubleshooting

### 1. Không kết nối được database
```bash
# Kiểm tra SSH tunnel đang chạy
netstat -an | findstr "5432"

# Nếu không có, tạo lại tunnel
ssh -L 5432:localhost:5432 admin@one.vnptacademy.com.vn -p 2222 -N
```

### 2. Lỗi import dữ liệu
```bash
# Xóa dữ liệu cũ và import lại
python create_tables.py  # Tạo lại bảng
python import_data.py     # Import lại
```

### 3. Lỗi password authentication
- Kiểm tra password trong .env đã escape ký tự @ thành %40
- Đảm bảo user postgres có password đúng trên server

## 📞 Liên hệ

**Quản lý Dự án**: VNPT IT Team  
**Server Admin**: admin@one.vnptacademy.com.vn  
**Support**: Port 2222 SSH

---

**Phiên bản**: 1.0.0  
**Cập nhật**: 22/11/2025