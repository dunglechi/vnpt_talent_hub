# Deployment Guide - VNPT Talent Hub

## 📦 Yêu cầu Hệ thống

### Production Server
- **OS**: Ubuntu 22.04 LTS hoặc cao hơn
- **CPU**: 4 vCPU trở lên
- **RAM**: 8GB trở lên
- **Disk**: 100GB SSD
- **Network**: Port 80, 443, 2222 (SSH), 5432 (PostgreSQL - internal only)

### Software Requirements
```bash
Python >= 3.10
PostgreSQL >= 14
Nginx >= 1.18
Supervisor (for process management)
SSL Certificate (Let's Encrypt)
```

## 🚀 Deployment Steps

### 1. Chuẩn bị Server

```bash
# Update system
sudo apt update && sudo apt upgrade -y

# Install dependencies
sudo apt install -y python3-pip python3-venv postgresql postgresql-contrib nginx supervisor

# Create application user
sudo adduser --system --group --home /opt/vnpt-talent-hub vnpttlh
```

### 2. Setup PostgreSQL

```bash
# Switch to postgres user
sudo -u postgres psql

# Create database and user
CREATE DATABASE vnpt_talent_hub;
CREATE USER vnpt_user WITH PASSWORD 'secure_password_here';
GRANT ALL PRIVILEGES ON DATABASE vnpt_talent_hub TO vnpt_user;
ALTER DATABASE vnpt_talent_hub OWNER TO vnpt_user;
\q

# Configure PostgreSQL for remote access (if needed)
sudo nano /etc/postgresql/14/main/postgresql.conf
# Set: listen_addresses = 'localhost'

sudo nano /etc/postgresql/14/main/pg_hba.conf
# Add: host vnpt_talent_hub vnpt_user 127.0.0.1/32 md5

# Restart PostgreSQL
sudo systemctl restart postgresql
```

### 3. Deploy Application

```bash
# Clone repository
cd /opt/vnpt-talent-hub
sudo -u vnpttlh git clone https://github.com/vnpt/talent-hub.git .

# Create virtual environment
sudo -u vnpttlh python3 -m venv venv
sudo -u vnpttlh venv/bin/pip install --upgrade pip
sudo -u vnpttlh venv/bin/pip install -r requirements.txt

# Setup environment variables
sudo -u vnpttlh nano .env
```

**.env file**:
```env
DATABASE_URL=postgresql://vnpt_user:secure_password_here@localhost:5432/vnpt_talent_hub
SECRET_KEY=your-secret-key-here-generate-with-openssl
ENVIRONMENT=production
DEBUG=false
ALLOWED_HOSTS=one.vnptacademy.com.vn,www.vnptacademy.com.vn
```

### 4. Initialize Database

```bash
# Create tables
sudo -u vnpttlh venv/bin/python create_database.py
sudo -u vnpttlh venv/bin/python create_tables.py

# Import initial data
sudo -u vnpttlh venv/bin/python import_data.py
```

### 5. Setup Supervisor (Process Manager)

```bash
# Create supervisor config
sudo nano /etc/supervisor/conf.d/vnpt-talent-hub.conf
```

**vnpt-talent-hub.conf**:
```ini
[program:vnpt-talent-hub]
command=/opt/vnpt-talent-hub/venv/bin/uvicorn app.main:app --host 127.0.0.1 --port 8000 --workers 4
directory=/opt/vnpt-talent-hub
user=vnpttlh
autostart=true
autorestart=true
redirect_stderr=true
stdout_logfile=/var/log/vnpt-talent-hub/app.log
stdout_logfile_maxbytes=50MB
stdout_logfile_backups=10
environment=PATH="/opt/vnpt-talent-hub/venv/bin"
```

```bash
# Create log directory
sudo mkdir -p /var/log/vnpt-talent-hub
sudo chown vnpttlh:vnpttlh /var/log/vnpt-talent-hub

# Update supervisor
sudo supervisorctl reread
sudo supervisorctl update
sudo supervisorctl start vnpt-talent-hub
```

### 6. Setup Nginx (Reverse Proxy)

```bash
sudo nano /etc/nginx/sites-available/vnpt-talent-hub
```

**vnpt-talent-hub nginx config**:
```nginx
upstream talent_hub {
    server 127.0.0.1:8000;
}

server {
    listen 80;
    server_name one.vnptacademy.com.vn www.vnptacademy.com.vn;
    
    # Redirect HTTP to HTTPS
    return 301 https://$server_name$request_uri;
}

server {
    listen 443 ssl http2;
    server_name one.vnptacademy.com.vn www.vnptacademy.com.vn;

    # SSL Configuration
    ssl_certificate /etc/letsencrypt/live/one.vnptacademy.com.vn/fullchain.pem;
    ssl_certificate_key /etc/letsencrypt/live/one.vnptacademy.com.vn/privkey.pem;
    ssl_protocols TLSv1.2 TLSv1.3;
    ssl_ciphers HIGH:!aNULL:!MD5;

    # Security Headers
    add_header Strict-Transport-Security "max-age=31536000; includeSubDomains" always;
    add_header X-Frame-Options "SAMEORIGIN" always;
    add_header X-Content-Type-Options "nosniff" always;
    add_header X-XSS-Protection "1; mode=block" always;

    # Logging
    access_log /var/log/nginx/talent-hub-access.log;
    error_log /var/log/nginx/talent-hub-error.log;

    # Max upload size
    client_max_body_size 10M;

    location / {
        proxy_pass http://talent_hub;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
        
        # Timeouts
        proxy_connect_timeout 60s;
        proxy_send_timeout 60s;
        proxy_read_timeout 60s;
    }

    # Static files (if any)
    location /static/ {
        alias /opt/vnpt-talent-hub/static/;
        expires 30d;
        add_header Cache-Control "public, immutable";
    }

    # API documentation
    location /docs {
        proxy_pass http://talent_hub/docs;
    }
}
```

```bash
# Enable site
sudo ln -s /etc/nginx/sites-available/vnpt-talent-hub /etc/nginx/sites-enabled/
sudo nginx -t
sudo systemctl restart nginx
```

### 7. Setup SSL Certificate (Let's Encrypt)

```bash
# Install certbot
sudo apt install -y certbot python3-certbot-nginx

# Get certificate
sudo certbot --nginx -d one.vnptacademy.com.vn -d www.vnptacademy.com.vn

# Auto-renewal (already set up by certbot)
sudo certbot renew --dry-run
```

## 🔄 Update & Maintenance

### Deploy New Version

```bash
# Backup database first
sudo -u postgres pg_dump vnpt_talent_hub > backup_$(date +%Y%m%d_%H%M%S).sql

# Pull latest code
cd /opt/vnpt-talent-hub
sudo -u vnpttlh git pull origin main

# Install new dependencies
sudo -u vnpttlh venv/bin/pip install -r requirements.txt

# Run migrations (if any)
sudo -u vnpttlh venv/bin/alembic upgrade head

# Restart application
sudo supervisorctl restart vnpt-talent-hub
```

### Rollback

```bash
# Revert to previous commit
sudo -u vnpttlh git reset --hard <previous-commit-hash>

# Restore database
sudo -u postgres psql vnpt_talent_hub < backup_file.sql

# Restart
sudo supervisorctl restart vnpt-talent-hub
```

## 💾 Backup Strategy

### Automated Daily Backups

```bash
# Create backup script
sudo nano /opt/vnpt-talent-hub/scripts/backup.sh
```

**backup.sh**:
```bash
#!/bin/bash
BACKUP_DIR="/var/backups/vnpt-talent-hub"
DATE=$(date +%Y%m%d_%H%M%S)
RETENTION_DAYS=30

# Create backup directory
mkdir -p $BACKUP_DIR

# Database backup
sudo -u postgres pg_dump vnpt_talent_hub | gzip > $BACKUP_DIR/db_$DATE.sql.gz

# Application files backup
tar -czf $BACKUP_DIR/app_$DATE.tar.gz -C /opt/vnpt-talent-hub \
    --exclude='venv' \
    --exclude='__pycache__' \
    --exclude='.git' \
    .

# Delete old backups
find $BACKUP_DIR -name "db_*.sql.gz" -mtime +$RETENTION_DAYS -delete
find $BACKUP_DIR -name "app_*.tar.gz" -mtime +$RETENTION_DAYS -delete

echo "Backup completed: $DATE"
```

```bash
# Make executable
sudo chmod +x /opt/vnpt-talent-hub/scripts/backup.sh

# Add to crontab
sudo crontab -e
# Add: 0 2 * * * /opt/vnpt-talent-hub/scripts/backup.sh >> /var/log/vnpt-talent-hub/backup.log 2>&1
```

### Restore from Backup

```bash
# Stop application
sudo supervisorctl stop vnpt-talent-hub

# Restore database
gunzip < /var/backups/vnpt-talent-hub/db_YYYYMMDD_HHMMSS.sql.gz | \
    sudo -u postgres psql vnpt_talent_hub

# Restore application files (if needed)
cd /opt/vnpt-talent-hub
sudo -u vnpttlh tar -xzf /var/backups/vnpt-talent-hub/app_YYYYMMDD_HHMMSS.tar.gz

# Start application
sudo supervisorctl start vnpt-talent-hub
```

## 📊 Monitoring

### Application Logs

```bash
# View application logs
sudo tail -f /var/log/vnpt-talent-hub/app.log

# View nginx access logs
sudo tail -f /var/log/nginx/talent-hub-access.log

# View nginx error logs
sudo tail -f /var/log/nginx/talent-hub-error.log

# View PostgreSQL logs
sudo tail -f /var/log/postgresql/postgresql-14-main.log
```

### Health Check

```bash
# Check application status
sudo supervisorctl status vnpt-talent-hub

# Check database
sudo -u postgres psql -c "SELECT version();"

# Check disk space
df -h

# Check memory
free -m

# Check CPU
top
```

### Setup Monitoring Tool (Optional)

```bash
# Install monitoring agents
# Example: New Relic, Datadog, or Prometheus
```

## 🔒 Security Checklist

- [x] Firewall configured (UFW)
- [x] SSH key-based authentication only
- [x] PostgreSQL accessible only from localhost
- [x] SSL/TLS enabled
- [x] Strong passwords for all accounts
- [x] Regular security updates
- [x] Application running as non-root user
- [x] File permissions properly set
- [x] Database backups automated
- [x] Fail2ban installed (optional)

```bash
# Setup UFW firewall
sudo ufw allow 22/tcp    # SSH
sudo ufw allow 80/tcp    # HTTP
sudo ufw allow 443/tcp   # HTTPS
sudo ufw allow 2222/tcp  # Custom SSH (if needed)
sudo ufw enable
```

## 🚨 Troubleshooting

### Application won't start

```bash
# Check logs
sudo supervisorctl tail -f vnpt-talent-hub

# Check if port is in use
sudo netstat -tlnp | grep 8000

# Restart
sudo supervisorctl restart vnpt-talent-hub
```

### Database connection issues

```bash
# Check PostgreSQL status
sudo systemctl status postgresql

# Test connection
psql -h localhost -U vnpt_user -d vnpt_talent_hub

# Check .env file
cat /opt/vnpt-talent-hub/.env
```

### Nginx errors

```bash
# Test nginx config
sudo nginx -t

# Check logs
sudo tail -f /var/log/nginx/error.log

# Restart nginx
sudo systemctl restart nginx
```

## 📞 Support

**Emergency Contacts**:
- System Admin: admin@vnpt.vn
- Database Admin: dba@vnpt.vn
- Development Team: dev@vnpt.vn

**On-call Schedule**: Check PROJECT_MANAGEMENT.md

---

**Last Updated**: 2025-11-22  
**Document Version**: 1.0