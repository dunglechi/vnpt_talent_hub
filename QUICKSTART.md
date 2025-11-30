# 🚀 Quick Start - Production Deployment

## Deployment trong 5 phút

### Prerequisites
- Ubuntu 20.04+ server với quyền sudo
- Domain name đã trỏ về server
- Port 80, 443 mở

### 1. One-Command Deployment

```bash
# Chạy trên server Ubuntu
sudo su -
cd /opt
git clone https://github.com/dunglechi/vnpt_talent_hub.git
cd vnpt_talent_hub
chmod +x deploy.sh
./deploy.sh
```

Script sẽ tự động:
- ✅ Cài Docker & Docker Compose
- ✅ Setup SSL certificate (Let's Encrypt)
- ✅ Build containers
- ✅ Run migrations
- ✅ Create admin user

### 2. Verify Deployment

```bash
# Check services
docker-compose ps

# Test API
curl https://your-domain.com/health
```

### 3. Access Application

- **API Docs**: https://your-domain.com/docs
- **API**: https://your-domain.com/api/v1
- **Health**: https://your-domain.com/health

### 4. Admin Login

```bash
# Default credentials (change immediately!)
Email: admin@vnpt.vn
Password: Admin123!@#
```

---

## Configuration Files

| File | Description |
|------|-------------|
| `.env.production` | Environment variables template |
| `docker-compose.yml` | Services configuration |
| `Dockerfile` | API container build |
| `nginx/nginx.conf` | Reverse proxy + SSL |
| `deploy.sh` | Automated deployment script |

---

## Useful Commands

### Service Management
```bash
# Start
docker-compose up -d

# Stop
docker-compose down

# Restart
docker-compose restart

# Logs
docker-compose logs -f
```

### Database
```bash
# Backup
./scripts/backup_database.sh

# Restore
./scripts/restore_database.sh <backup-file>

# Migrations
docker-compose exec api alembic upgrade head
```

### Updates
```bash
cd /opt/vnpt_talent_hub
git pull origin main
docker-compose down
docker-compose up -d --build
```

---

## Architecture

```
Internet
   ↓
Nginx (SSL/TLS)
   ↓
FastAPI (4 workers)
   ↓
PostgreSQL + Redis
```

**Services**:
- `nginx`: Reverse proxy with SSL
- `api`: FastAPI application
- `db`: PostgreSQL database
- `redis`: Cache & rate limiting

---

## Security Features

- ✅ HTTPS/SSL (Let's Encrypt)
- ✅ Rate limiting (Nginx + API)
- ✅ Security headers (HSTS, XSS, etc.)
- ✅ HttpOnly cookies
- ✅ Password hashing (bcrypt)
- ✅ JWT tokens (15min expiry)
- ✅ Audit logging
- ✅ Non-root Docker user

---

## Support

**Documentation**: See `PRODUCTION.md` for detailed guide

**Issues**: https://github.com/dunglechi/vnpt_talent_hub/issues

---

**Status**: 🟢 Production Ready  
**Version**: 1.4.0  
**Security**: Phase 2 Complete
