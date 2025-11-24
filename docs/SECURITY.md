# Security Policy - VNPT Talent Hub

## 🔒 Tổng quan

Tài liệu này mô tả các chính sách bảo mật, quy trình xử lý lỗ hổng, và best practices cho VNPT Talent Hub.

## 🛡️ Security Architecture

### Defense in Depth
```
┌─────────────────────────────────────────┐
│ Layer 1: Network Security              │
│ - Firewall (UFW)                        │
│ - SSH Key Authentication                │
│ - Port Restrictions                     │
└─────────────────────────────────────────┘
         ↓
┌─────────────────────────────────────────┐
│ Layer 2: Transport Security             │
│ - SSL/TLS Encryption                    │
│ - HTTPS Only                            │
│ - Secure Headers                        │
└─────────────────────────────────────────┘
         ↓
┌─────────────────────────────────────────┐
│ Layer 3: Application Security           │
│ - JWT Authentication                    │
│ - Role-Based Access Control             │
│ - Input Validation                      │
│ - SQL Injection Prevention              │
│ - XSS Protection                        │
└─────────────────────────────────────────┘
         ↓
┌─────────────────────────────────────────┐
│ Layer 4: Data Security                  │
│ - Encrypted at Rest                     │
│ - Encrypted in Transit                  │
│ - Data Masking                          │
│ - Audit Logs                            │
└─────────────────────────────────────────┘
```

## 🔐 Authentication & Authorization

### Password Policy
- **Minimum Length**: 12 characters
- **Complexity**: 
  - Ít nhất 1 chữ hoa
  - Ít nhất 1 chữ thường
  - Ít nhất 1 số
  - Ít nhất 1 ký tự đặc biệt
- **Expiry**: 90 ngày
- **History**: Không được trùng 5 mật khẩu gần nhất
- **Lockout**: 5 lần thử sai → khóa 30 phút

### JWT Token Security
```python
# Token Configuration
JWT_SECRET_KEY = "use-strong-random-key-here"  # 256-bit
JWT_ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30
REFRESH_TOKEN_EXPIRE_DAYS = 7

# Security Headers
{
    "typ": "JWT",
    "alg": "HS256"
}
```

### Role-Based Access Control (RBAC)

| Role | Permissions |
|------|-------------|
| **Admin** | Full system access, user management, configuration |
| **HR Manager** | View all employees, assign assessments, generate reports |
| **Manager** | View team members, assess team competencies |
| **Employee** | View own profile, self-assessment, view own reports |
| **Viewer** | Read-only access to public information |

## 🚨 Vulnerability Management

### Reporting Security Issues

**DO NOT** create public GitHub issues for security vulnerabilities!

**Email**: security@vnpt.vn  
**PGP Key**: [Link to PGP key]

**Include**:
- Vulnerability description
- Steps to reproduce
- Potential impact
- Suggested fix (if any)

### Response Timeline
- **Critical**: Response within 24 hours, fix within 7 days
- **High**: Response within 72 hours, fix within 30 days
- **Medium**: Response within 1 week, fix within 90 days
- **Low**: Response within 2 weeks, fix in next release

### Severity Classification

**Critical (CVSS 9.0-10.0)**
- Remote code execution
- Authentication bypass
- SQL injection with data access
- Exposure of sensitive credentials

**High (CVSS 7.0-8.9)**
- Privilege escalation
- Information disclosure (sensitive data)
- XSS in administrative interface

**Medium (CVSS 4.0-6.9)**
- CSRF vulnerabilities
- Information disclosure (non-sensitive)
- Denial of Service

**Low (CVSS 0.1-3.9)**
- Minor information leakage
- UI/UX security issues

## 🔍 Security Best Practices

### For Developers

#### 1. Input Validation
```python
from pydantic import BaseModel, validator

class EmployeeCreate(BaseModel):
    name: str
    email: EmailStr
    
    @validator('name')
    def name_must_be_valid(cls, v):
        if not v or len(v) < 2:
            raise ValueError('Name must be at least 2 characters')
        if not v.replace(' ', '').isalnum():
            raise ValueError('Name contains invalid characters')
        return v.strip()
```

#### 2. SQL Injection Prevention
```python
# ✅ GOOD - Using ORM
employees = session.query(Employee).filter(
    Employee.email == user_input
).all()

# ❌ BAD - Raw SQL with string formatting
query = f"SELECT * FROM employees WHERE email = '{user_input}'"
```

#### 3. XSS Prevention
```python
# Backend - Sanitize output
from markupsafe import escape

@app.get("/api/employees/{id}")
def get_employee(id: int):
    employee = get_employee_by_id(id)
    return {
        "name": escape(employee.name),
        "email": escape(employee.email)
    }
```

#### 4. CSRF Protection
```python
# FastAPI CSRF
from fastapi_csrf_protect import CsrfProtect

@app.post("/api/assessments")
async def create_assessment(
    csrf_protect: CsrfProtect = Depends()
):
    await csrf_protect.validate_csrf(request)
    # ... process request
```

#### 5. Rate Limiting
```python
from slowapi import Limiter
from slowapi.util import get_remote_address

limiter = Limiter(key_func=get_remote_address)

@app.post("/api/auth/login")
@limiter.limit("5/minute")
async def login(request: Request):
    # ... login logic
```

### For System Admins

#### 1. SSH Hardening
```bash
# /etc/ssh/sshd_config
PermitRootLogin no
PasswordAuthentication no
PubkeyAuthentication yes
Port 2222
AllowUsers vnpttlh admin
```

#### 2. Database Security
```bash
# PostgreSQL pg_hba.conf
# Only allow local connections
host    vnpt_talent_hub    vnpt_user    127.0.0.1/32    md5
hostssl vnpt_talent_hub    vnpt_user    127.0.0.1/32    md5
```

#### 3. File Permissions
```bash
# Application files
sudo chown -R vnpttlh:vnpttlh /opt/vnpt-talent-hub
sudo chmod 750 /opt/vnpt-talent-hub
sudo chmod 640 /opt/vnpt-talent-hub/.env

# Log files
sudo chmod 640 /var/log/vnpt-talent-hub/*.log
```

#### 4. Fail2ban Configuration
```ini
# /etc/fail2ban/jail.local
[vnpt-talent-hub]
enabled = true
port = http,https
filter = vnpt-talent-hub
logpath = /var/log/nginx/talent-hub-error.log
maxretry = 5
bantime = 3600
```

## 📝 Data Privacy & Compliance

### GDPR Compliance
- ✅ Right to access personal data
- ✅ Right to rectification
- ✅ Right to erasure ("right to be forgotten")
- ✅ Right to data portability
- ✅ Data encryption at rest and in transit
- ✅ Audit logs for data access
- ✅ Data retention policy

### Vietnamese Cybersecurity Law
- ✅ Data stored on Vietnamese territory (if required)
- ✅ User consent for data collection
- ✅ Data breach notification within 72 hours
- ✅ Privacy policy in Vietnamese

### Data Classification

| Level | Examples | Protection |
|-------|----------|------------|
| **Public** | Job families, competency definitions | None |
| **Internal** | Employee names, job titles | Access control |
| **Confidential** | Assessment results, salaries | Encryption + Access control |
| **Restricted** | Passwords, tokens | Hashing + Encryption |

### Data Retention Policy
- **Active Employees**: Retained indefinitely
- **Former Employees**: 7 years after termination
- **Assessment Data**: 5 years
- **Audit Logs**: 2 years
- **Backup Data**: 30 days

## 🔐 Encryption

### Data at Rest
```python
# Sensitive fields encryption
from cryptography.fernet import Fernet

# Generate key (store securely in environment variable)
ENCRYPTION_KEY = os.getenv("ENCRYPTION_KEY")
cipher = Fernet(ENCRYPTION_KEY)

def encrypt_data(data: str) -> str:
    return cipher.encrypt(data.encode()).decode()

def decrypt_data(encrypted_data: str) -> str:
    return cipher.decrypt(encrypted_data.encode()).decode()
```

### Data in Transit
- **TLS 1.2+** for all API communications
- **HTTPS Only** - HTTP redirects to HTTPS
- **SSL Certificate** from trusted CA (Let's Encrypt)

### Password Hashing
```python
from passlib.context import CryptContext

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

def hash_password(password: str) -> str:
    return pwd_context.hash(password)

def verify_password(plain_password: str, hashed_password: str) -> bool:
    return pwd_context.verify(plain_password, hashed_password)
```

## 📊 Security Monitoring & Logging

### Audit Logs
Log tất cả các hành động quan trọng:
```python
# Example log entry
{
    "timestamp": "2025-11-22T10:30:00Z",
    "user_id": 123,
    "action": "update_assessment",
    "resource": "assessment/456",
    "ip_address": "192.168.1.100",
    "user_agent": "Mozilla/5.0...",
    "result": "success"
}
```

### Security Events to Monitor
- Failed login attempts
- Privilege escalation attempts
- Bulk data exports
- Configuration changes
- Database schema changes
- Unusual API usage patterns

### Alerting
```bash
# Example: Alert on multiple failed logins
if [ failed_login_count > 10 ]; then
    send_alert("Multiple failed login attempts from IP: $ip_address")
fi
```

## 🛡️ Incident Response Plan

### 1. Detection
- Monitor security logs
- Review alerts
- User reports

### 2. Containment
- Isolate affected systems
- Block malicious IPs
- Revoke compromised credentials

### 3. Investigation
- Analyze logs
- Determine scope of breach
- Identify root cause

### 4. Eradication
- Remove malware/backdoors
- Patch vulnerabilities
- Update security controls

### 5. Recovery
- Restore from backups
- Verify system integrity
- Resume normal operations

### 6. Post-Incident
- Document lessons learned
- Update security policies
- Conduct training

## 📋 Security Checklist

### Weekly
- [ ] Review access logs
- [ ] Check for failed login attempts
- [ ] Monitor system resource usage
- [ ] Verify backup completion

### Monthly
- [ ] Review user permissions
- [ ] Update dependencies
- [ ] Security scan (vulnerability scanner)
- [ ] Review firewall rules

### Quarterly
- [ ] Penetration testing
- [ ] Security awareness training
- [ ] Review and update security policies
- [ ] Disaster recovery drill

### Annually
- [ ] Full security audit
- [ ] Compliance certification review
- [ ] Update incident response plan
- [ ] Third-party security assessment

## 📞 Security Contacts

**Security Team**: security@vnpt.vn  
**Incident Hotline**: +84-xxx-xxx-xxx (24/7)  
**PGP Key**: [Available on keyserver]

**Escalation Path**:
1. Security Officer
2. CTO
3. CEO
4. Board of Directors

---

**Version**: 1.0  
**Last Updated**: 2025-11-22  
**Next Review**: 2026-02-22