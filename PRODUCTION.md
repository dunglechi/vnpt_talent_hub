# 🚀 Production Deployment Guide - VNPT Talent Hub

**Version**: 1.4.0  
**Last Updated**: January 2025  
**Status**: Production Ready

---

## 📋 Table of Contents

1. [Prerequisites](#prerequisites)
2. [Quick Start](#quick-start)
3. [Detailed Setup](#detailed-setup)
4. [Configuration](#configuration)
5. [Deployment](#deployment)
6. [Monitoring](#monitoring)
7. [Backup & Restore](#backup--restore)
8. [Troubleshooting](#troubleshooting)
9. [Scaling](#scaling)
10. [Security Checklist](#security-checklist)

---

## Prerequisites

### Server Requirements

**Minimum (Small deployment)**:
- 2 CPU cores
- 4 GB RAM
- 20 GB SSD storage
- Ubuntu 20.04 LTS or later

**Recommended (Production)**:
- 4 CPU cores
- 8 GB RAM
- 50 GB SSD storage
- Ubuntu 22.04 LTS

### Software Requirements

- Docker 20.10+
- Docker Compose 2.0+
- Git
- Certbot (for SSL)
- Domain name with DNS configured

### Network Requirements

- Ports 80 (HTTP) and 443 (HTTPS) open
- Port 22 (SSH) for management
- Static IP address or domain name

---

## Quick Start

### 1. Automated Deployment

```bash
# On your production server (Ubuntu)
sudo su -
cd /opt
git clone https://github.com/dunglechi/vnpt_talent_hub.git
cd vnpt_talent_hub
chmod +x deploy.sh
./deploy.sh
```

The script will:
- ✅ Install Docker and dependencies
- ✅ Configure environment variables
- ✅ Set up SSL certificates (Let's Encrypt)
- ✅ Build and start all services
- ✅ Run database migrations
- ✅ Create admin user

### 2. Verify Deployment

```bash
# Check services status
docker-compose ps

# Check logs
docker-compose logs -f

# Test API
curl https://your-domain.com/health
```

---

## Detailed Setup

### Step 1: Prepare Server

```bash
# Update system
sudo apt update && sudo apt upgrade -y

# Install Docker
curl -fsSL https://get.docker.com -o get-docker.sh
sudo sh get-docker.sh
sudo usermod -aG docker $USER

# Install Docker Compose
sudo curl -L "https://github.com/docker/compose/releases/latest/download/docker-compose-$(uname -s)-$(uname -m)" -o /usr/local/bin/docker-compose
sudo chmod +x /usr/local/bin/docker-compose

# Verify installation
docker --version
docker-compose --version
```

### Step 2: Clone Repository

```bash
sudo mkdir -p /opt
cd /opt
sudo git clone https://github.com/dunglechi/vnpt_talent_hub.git
cd vnpt_talent_hub
```

### Step 3: Configure Environment

```bash
# Copy production environment template
cp .env.production .env

# Edit environment variables
nano .env
```

**Required configurations**:

```bash
# Database
DB_PASSWORD=your_strong_password_here

# Redis
REDIS_PASSWORD=your_redis_password_here

# Security (generate with: openssl rand -hex 32)
SECRET_KEY=your_secret_key_here

# Email (SMTP)
SMTP_HOST=smtp.gmail.com
SMTP_PORT=587
SMTP_USERNAME=your-email@gmail.com
SMTP_PASSWORD=your-app-password
SMTP_FROM_EMAIL=noreply@your-domain.com

# Application
FRONTEND_URL=https://your-domain.com
DOMAIN_NAME=your-domain.com
```

### Step 4: SSL Certificate

**Option A: Let's Encrypt (Recommended)**

```bash
# Install Certbot
sudo apt install certbot python3-certbot-nginx -y

# Get certificate
sudo certbot certonly --standalone \
  -d your-domain.com \
  -d www.your-domain.com \
  --email admin@your-domain.com \
  --agree-tos \
  --non-interactive

# Copy certificates
sudo mkdir -p nginx/ssl
sudo cp /etc/letsencrypt/live/your-domain.com/fullchain.pem nginx/ssl/
sudo cp /etc/letsencrypt/live/your-domain.com/privkey.pem nginx/ssl/

# Set up auto-renewal
echo "0 0,12 * * * root certbot renew --quiet && cp /etc/letsencrypt/live/your-domain.com/*.pem /opt/vnpt_talent_hub/nginx/ssl/ && cd /opt/vnpt_talent_hub && docker-compose restart nginx" | sudo tee -a /etc/crontab
```

**Option B: Self-signed (Development/Testing)**

```bash
mkdir -p nginx/ssl
openssl req -x509 -nodes -days 365 -newkey rsa:2048 \
  -keyout nginx/ssl/privkey.pem \
  -out nginx/ssl/fullchain.pem \
  -subj "/CN=your-domain.com"
```

### Step 5: Build and Deploy

```bash
# Build containers
docker-compose build --no-cache

# Start services
docker-compose up -d

# Check status
docker-compose ps

# View logs
docker-compose logs -f
```

### Step 6: Initialize Database

```bash
# Run migrations
docker-compose exec api alembic upgrade head

# Verify migrations
docker-compose exec api alembic current
```

### Step 7: Create Admin User

**Option A: Using Python script**

```bash
docker-compose exec api python -c "
from app.core.database import SessionLocal
from app.models.user import User, UserRole
from app.core.security import get_password_hash

db = SessionLocal()
admin = User(
    email='admin@vnpt.vn',
    hashed_password=get_password_hash('Admin123!@#'),
    full_name='System Administrator',
    role=UserRole.ADMIN,
    is_active=True,
    is_verified=True
)
db.add(admin)
db.commit()
print('Admin user created')
"
```

**Option B: Using API**

```bash
curl -X POST https://your-domain.com/api/v1/auth/register \
  -H "Content-Type: application/json" \
  -d '{
    "email": "admin@vnpt.vn",
    "password": "Admin123!@#",
    "full_name": "System Administrator"
  }'
```

---

## Configuration

### Environment Variables

See `.env.production` for all available variables.

**Critical variables**:

| Variable | Description | Example |
|----------|-------------|---------|
| `SECRET_KEY` | JWT signing key | `openssl rand -hex 32` |
| `DATABASE_URL` | PostgreSQL connection | `postgresql+psycopg2://...` |
| `REDIS_URL` | Redis connection | `redis://:password@redis:6379/0` |
| `SMTP_HOST` | Email server | `smtp.gmail.com` |
| `FRONTEND_URL` | Frontend URL | `https://your-domain.com` |

### Docker Compose Services

**Services running**:
- `db` - PostgreSQL 14
- `redis` - Redis 7
- `api` - FastAPI application (4 workers)
- `nginx` - Reverse proxy with SSL

**Ports exposed**:
- 80 (HTTP) → redirects to HTTPS
- 443 (HTTPS) → Nginx → API
- 5432 (PostgreSQL) - internal only
- 6379 (Redis) - internal only

---

## Monitoring

### Health Checks

```bash
# API health
curl https://your-domain.com/health

# Database health
docker-compose exec db pg_isready -U talent_admin

# Redis health
docker-compose exec redis redis-cli ping
```

### Logs

```bash
# All services
docker-compose logs -f

# Specific service
docker-compose logs -f api
docker-compose logs -f nginx
docker-compose logs -f db

# Last 100 lines
docker-compose logs --tail=100 api
```

### Resource Usage

```bash
# Container stats
docker stats

# Disk usage
docker system df

# Detailed container info
docker-compose ps
```

### Application Metrics

Access metrics via:
- API Docs: `https://your-domain.com/docs`
- Audit Logs: `https://your-domain.com/api/v1/audit-logs/stats/summary`

---

## Backup & Restore

### Automated Backups

```bash
# Set up daily backups (2 AM)
chmod +x scripts/backup_database.sh
echo "0 2 * * * /opt/vnpt_talent_hub/scripts/backup_database.sh" | sudo crontab -
```

### Manual Backup

```bash
# Backup database
./scripts/backup_database.sh

# Backups stored in: /var/backups/vnpt-talent-hub/
```

### Restore from Backup

```bash
# List available backups
ls -lh /var/backups/vnpt-talent-hub/

# Restore specific backup
./scripts/restore_database.sh /var/backups/vnpt-talent-hub/vnpt_talent_hub_20250130_020000.sql.gz
```

### Backup to Cloud

**AWS S3**:
```bash
# Install AWS CLI
apt install awscli -y
aws configure

# Add to backup script
aws s3 cp /var/backups/vnpt-talent-hub/*.sql.gz s3://your-bucket/backups/
```

**Google Cloud Storage**:
```bash
# Install gsutil
apt install google-cloud-sdk -y
gcloud auth login

# Add to backup script
gsutil cp /var/backups/vnpt-talent-hub/*.sql.gz gs://your-bucket/backups/
```

---

## Troubleshooting

### Common Issues

**1. Services won't start**

```bash
# Check logs
docker-compose logs

# Check disk space
df -h

# Restart services
docker-compose down
docker-compose up -d
```

**2. Database connection errors**

```bash
# Check database is running
docker-compose ps db

# Check database logs
docker-compose logs db

# Verify credentials in .env
cat .env | grep DB_

# Test connection
docker-compose exec db psql -U talent_admin -d vnpt_talent_hub_prod
```

**3. SSL certificate issues**

```bash
# Check certificate files
ls -l nginx/ssl/

# Renew certificate
sudo certbot renew

# Copy new certificates
sudo cp /etc/letsencrypt/live/your-domain.com/*.pem nginx/ssl/

# Restart nginx
docker-compose restart nginx
```

**4. Out of memory**

```bash
# Check memory usage
free -h
docker stats

# Reduce workers in docker-compose.yml
# Change: --workers 4 to --workers 2

# Restart
docker-compose down
docker-compose up -d
```

**5. Migration errors**

```bash
# Check current migration
docker-compose exec api alembic current

# Check migration history
docker-compose exec api alembic history

# Force migration to head
docker-compose exec api alembic upgrade head

# Rollback one version
docker-compose exec api alembic downgrade -1
```

### Debug Mode

```bash
# Enable debug logging
# Edit .env
LOG_LEVEL=DEBUG

# Restart API
docker-compose restart api

# Watch logs
docker-compose logs -f api
```

---

## Scaling

### Horizontal Scaling

**Option 1: Docker Compose Scale**

```bash
# Scale API workers
docker-compose up -d --scale api=3

# Update nginx upstream in nginx/nginx.conf
upstream api_backend {
    server api_1:8000;
    server api_2:8000;
    server api_3:8000;
}
```

**Option 2: Kubernetes (Advanced)**

See `kubernetes/` directory for K8s manifests (coming soon).

### Vertical Scaling

Edit `docker-compose.yml`:

```yaml
services:
  api:
    deploy:
      resources:
        limits:
          cpus: '2'
          memory: 4G
        reservations:
          cpus: '1'
          memory: 2G
```

### Database Optimization

```bash
# Tune PostgreSQL
# Edit postgresql.conf in container
docker-compose exec db bash
vi /var/lib/postgresql/data/postgresql.conf

# Recommended settings:
# max_connections = 200
# shared_buffers = 2GB
# effective_cache_size = 6GB
# work_mem = 16MB
```

---

## Security Checklist

### Pre-deployment

- [ ] Change all default passwords
- [ ] Generate strong `SECRET_KEY`
- [ ] Configure firewall (UFW)
- [ ] Set up SSL certificates
- [ ] Enable rate limiting
- [ ] Configure CORS properly
- [ ] Secure Redis with password
- [ ] Use non-root Docker user

### Post-deployment

- [ ] Verify HTTPS redirect works
- [ ] Test rate limiting
- [ ] Check security headers (use securityheaders.com)
- [ ] Enable automated backups
- [ ] Set up monitoring/alerting
- [ ] Document credentials securely
- [ ] Configure log retention
- [ ] Test disaster recovery

### Firewall Setup

```bash
# Install UFW
sudo apt install ufw -y

# Configure firewall
sudo ufw default deny incoming
sudo ufw default allow outgoing
sudo ufw allow ssh
sudo ufw allow 80/tcp
sudo ufw allow 443/tcp
sudo ufw enable

# Check status
sudo ufw status
```

### Security Headers (Already configured in Nginx)

- ✅ Strict-Transport-Security
- ✅ X-Frame-Options
- ✅ X-Content-Type-Options
- ✅ X-XSS-Protection
- ✅ Referrer-Policy

---

## Maintenance

### Update Application

```bash
cd /opt/vnpt_talent_hub

# Pull latest code
git pull origin main

# Rebuild and restart
docker-compose down
docker-compose build --no-cache
docker-compose up -d

# Run migrations
docker-compose exec api alembic upgrade head
```

### Update Dependencies

```bash
# Update base images
docker-compose pull

# Rebuild
docker-compose build --no-cache
docker-compose up -d
```

### Cleanup

```bash
# Remove unused Docker resources
docker system prune -a --volumes

# Clean old logs
find logs/ -name "*.log" -mtime +30 -delete
```

---

## Support & Resources

**Documentation**:
- API Docs: `/docs`
- Technical Docs: `/docs` directory
- GitHub: https://github.com/dunglechi/vnpt_talent_hub

**Monitoring Tools** (Optional):
- Sentry (error tracking)
- Prometheus + Grafana (metrics)
- ELK Stack (log aggregation)

**Getting Help**:
- GitHub Issues: https://github.com/dunglechi/vnpt_talent_hub/issues
- Email: admin@vnpt.vn

---

**Last Updated**: January 2025  
**Version**: 1.4.0  
**Status**: Production Ready 🚀
