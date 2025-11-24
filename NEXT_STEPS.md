# NEXT_STEPS Roadmap

Prioritized future enhancements grouped by strategic category. These items consolidate improvement ideas surfaced across earlier directive reports (validation, performance, UX, security, extensibility) plus natural next milestones for a talent management platform.

## Reporting & Analytics
- Competency Distribution Dashboard: Aggregate counts per proficiency level, per department.
- Gap Analysis Portfolio: Multi-employee aggregation (average readiness %, top recurring gaps).
- Career Path Progress Tracking: Historical trend of gap closure per employee.
- Manager Team Heatmap: Visual matrix of competencies vs levels for direct reports.
- Export & Data Feeds: CSV/Excel export endpoints; scheduled data dump for BI tools.
- Time-Based Snapshots: Monthly snapshot table for longitudinal analytics.

## Workflow & Approvals
- Competency Change Approval: Manager/admin approval workflow for level increases beyond threshold.
- Career Path Advancement Requests: Employee submits readiness claim; manager review & approve.
- Bulk Assignment Actions: Managers assign multiple competencies or levels in one request.
- Notification Layer: Email / in-app notifications for approvals, gap readiness milestones.

## Advanced Features
- Recommendation Engine: Suggest next competencies based on target path & industry benchmarks.
- AI Skill Inference: Infer competencies from project/task metadata or uploaded CV.
- Learning Resource Linking: Map competencies to curated training materials or LMS courses.
- Career Path Versioning: Allow historical versions; track changes in required levels over time.
- Dynamic Level Formulas: Compute readiness using weighted importance per competency.
- Multi-Path Comparison: Compare employee profile against several potential career paths simultaneously.

## Data & Model Integrity
- Cascade Deletes via Migrations: Replace manual cascade with ondelete="CASCADE" in ForeignKey constraints.
- Referential Integrity Audits: Scheduled job verifying no orphaned links or invalid IDs.
- Soft Deletes: Introduce logical deletion flags for users/competencies to preserve historical analytics.
- Bulk Import Validation: Pre-commit dry-run mode for large competency/job family imports.

## Security & Compliance
- ✅ Password Complexity Enforcement: Uppercase, lowercase, digit, special character rules (COMPLETED - Directive #18)
- ✅ Token Expiration Reduction: Reduced from 30 to 15 minutes (COMPLETED - Directive #18)
- Email Verification Flow: Token-based verification to set `is_verified=True` (NEXT - Phase 2)
- Rate Limiting: Basic per-user and global throttling on write endpoints (NEXT - Phase 2)
- Audit Logging: Persist CRUD & authorization events to an immutable audit table (NEXT - Phase 2)
- Refresh Token Mechanism: Reduce user login frequency with refresh tokens (NEXT - Phase 2)
- Role-Based Scope Tokens: Limit access token scope (read-only vs admin actions).
- Data Scrubbing & PII Minimization: Ensure only necessary personal data retained.

## Performance & Scalability
- ✅ Query Optimization: Add targeted indexes for filtering fields (email, full_name, role_name, department) (COMPLETED - Directive #18)
- Caching Layer: Read-heavy endpoints (competencies, career paths) cached via Redis.
- Asynchronous Tasks: Offload heavy analytics computations to background workers (Celery/RQ).
- Pagination Metadata Enhancements: Include total pages and next/previous cursors.
- Read Replicas Support: Configure SQLAlchemy to route read queries to replicas when scaling.

## API & Developer Experience
- Bulk Endpoints: Batch create/update/delete for users and competencies.
- Consistent Error Schema: Unified error response (code, message, hint, doc_link).
- Tags & Grouping Enhancement: Refine OpenAPI tags (Auth, Admin, Manager, Employee Ops, Analytics).
- Versioned API: Introduce /api/v2 with refined responses and deprecations.
- SDK/Client Library: Provide Python/TypeScript client wrappers for faster integration.

## Maintainability & Quality
- Test Coverage Expansion: Add tests for filtering logic, gap analysis edge cases, auth failures.
- Contract Tests: Assert stability of key response schemas over time.
- Static Analysis & Linting: Integrate mypy, ruff, and consistent formatting (black) CI pipeline.
- CI/CD Pipeline: Automated test, build, migration check, security scan (Bandit) before deploy.

## Data Enrichment & HR Integration
- HRIS Synchronization: Scheduled sync to pull org hierarchy & employee metadata.
- External LMS Integration: Auto-mark competency progression based on course completions.
- Skill Decay Modeling: Reduce proficiency over time if not refreshed (optional feature toggle).

## Internationalization & UX
- Multi-language Support: Localize competency definitions & UI labels.
- Accessibility Review: Ensure endpoints & prospective UI components align with accessibility best practices.
- Enhanced Documentation Portal: Auto-generate endpoint usage examples & changelog diffs.

## Prioritization (Top 10 Immediate Candidates)
1. Email Verification & Password Complexity
2. Cascade Deletes Migration
3. Audit Logging & Consistent Error Schema
4. Bulk Operations (Users, Competencies)
5. Manager Team Heatmap Report
6. Recommendation Engine (MVP rule-based)
7. Gap Analysis Portfolio (multi-employee aggregation)
8. Test Coverage Expansion (filters, edge cases)
9. CI/CD Security & Static Analysis Integration
10. HRIS Synchronization (basic org import)

---
These roadmap items aim to transition the platform from foundational CRUD + analysis into a robust talent intelligence system with governance, scalability, and insight depth.
