# TODO - VNPT Talent Hub

## 🎯 Phase 1: Backend API (Ưu tiên cao)

### API Development
- [ ] Cài đặt FastAPI framework
- [ ] Tạo router structure:
  - [ ] `/api/competencies` - CRUD năng lực
  - [ ] `/api/job-families` - CRUD họ công việc
  - [ ] `/api/employees` - CRUD nhân viên
  - [ ] `/api/assessments` - Đánh giá năng lực
- [ ] Implement Pydantic schemas cho validation
- [ ] Exception handling và error responses
- [ ] Logging system
- [ ] API Documentation (Swagger UI)

### Authentication & Authorization
- [ ] JWT-based authentication
- [ ] Role-based access control (Admin, Manager, Employee)
- [ ] Password hashing (bcrypt)
- [ ] Refresh token mechanism
- [ ] User management endpoints

### Database Enhancements
- [ ] Thêm bảng Users và Roles
- [ ] Thêm bảng Assessments (đánh giá)
- [ ] Thêm bảng AssessmentResults
- [ ] Indexes cho performance
- [ ] Database migration với Alembic
- [ ] Backup strategy

### Testing
- [ ] Unit tests cho models
- [ ] Integration tests cho APIs
- [ ] Test coverage > 80%
- [ ] Load testing

## 🎨 Phase 2: Frontend (Ưu tiên trung)

### Setup
- [ ] Setup Next.js 14 project
- [ ] Configure Tailwind CSS
- [ ] Setup TypeScript
- [ ] Configure API client (axios/fetch)

### Pages & Components
- [ ] Landing page
- [ ] Authentication pages (Login/Register)
- [ ] Dashboard:
  - [ ] Overview statistics
  - [ ] Recent assessments
  - [ ] Competency gaps
- [ ] Competency Management:
  - [ ] List view
  - [ ] Detail view
  - [ ] Create/Edit form
- [ ] Employee Management:
  - [ ] Employee list
  - [ ] Employee profile
  - [ ] Competency matrix
- [ ] Assessment Module:
  - [ ] Self-assessment form
  - [ ] Manager assessment form
  - [ ] 360-degree feedback
- [ ] Reports & Analytics:
  - [ ] Individual reports
  - [ ] Team reports
  - [ ] Export to PDF/Excel

### UI/UX
- [ ] Responsive design (mobile, tablet, desktop)
- [ ] Dark mode support
- [ ] Accessibility (WCAG 2.1)
- [ ] Multi-language (Vietnamese, English)

## 🚀 Phase 3: Advanced Features (Ưu tiên thấp)

### AI & Analytics
- [ ] Năng lực prediction với ML
- [ ] Gợi ý lộ trình phát triển cá nhân
- [ ] Matching nhân viên với vị trí
- [ ] Competency gap analysis
- [ ] Trend analysis và forecasting

### Integration
- [ ] LDAP/Active Directory integration
- [ ] LMS integration (Moodle, etc.)
- [ ] HRMS integration
- [ ] Email notifications (SendGrid/AWS SES)
- [ ] Calendar integration (Google/Outlook)

### Advanced Reports
- [ ] Custom report builder
- [ ] Scheduled reports
- [ ] Dashboard templates
- [ ] Data visualization (Chart.js/D3.js)
- [ ] Export formats (PDF, Excel, CSV)

### Mobile App
- [ ] React Native app
- [ ] Offline mode
- [ ] Push notifications
- [ ] QR code scanning

## 🔧 DevOps & Infrastructure

### Deployment
- [ ] Dockerize application
- [ ] Docker Compose setup
- [ ] CI/CD pipeline (GitHub Actions)
- [ ] Staging environment
- [ ] Production deployment guide

### Monitoring
- [ ] Application monitoring (Sentry/New Relic)
- [ ] Database monitoring
- [ ] Server monitoring
- [ ] Alert system
- [ ] Performance metrics

### Security
- [ ] Security audit
- [ ] Penetration testing
- [ ] SQL injection prevention
- [ ] XSS protection
- [ ] CSRF protection
- [ ] Rate limiting
- [ ] SSL/TLS certificate

### Backup & Recovery
- [ ] Automated database backups
- [ ] Disaster recovery plan
- [ ] Data retention policy

## 📚 Documentation

- [ ] API documentation (OpenAPI/Swagger)
- [ ] User manual (Vietnamese)
- [ ] Admin guide
- [ ] Developer guide
- [ ] Architecture diagram
- [ ] Database schema diagram
- [ ] Video tutorials

## 🐛 Known Issues

- [ ] SSH tunnel cần được tạo thủ công trước khi chạy app
- [ ] Import script chưa handle duplicate data
- [ ] Chưa có validation cho CSV format

## 💡 Ideas & Suggestions

- Gamification: Badge, achievements cho nhân viên hoàn thành đánh giá
- Social features: Nhân viên có thể tag mentor, chia sẻ thành tích
- Career path visualization
- Skills marketplace nội bộ
- Competency-based training recommendations

---

**Ghi chú**: 
- ✅ = Hoàn thành
- 🚧 = Đang thực hiện
- ❌ = Bị block
- 📝 = Cần thảo luận