# API Specifications - VNPT Talent Hub

## Base URL
```
Production: https://one.vnptacademy.com.vn/api/v1
Development: http://localhost:8000/api/v1
```

## Authentication
Tất cả endpoints (trừ login/register) yêu cầu JWT token trong header:
```
Authorization: Bearer <token>
```

---

## 1. Authentication APIs

### POST `/auth/login`
Đăng nhập và nhận JWT token.

**Request Body:**
```json
{
  "email": "user@vnpt.vn",
  "password": "password123"
}
```

**Response (200):**
```json
{
  "access_token": "eyJ0eXAiOiJKV1QiLCJhbGc...",
  "refresh_token": "eyJ0eXAiOiJKV1QiLCJhbGc...",
  "token_type": "bearer",
  "expires_in": 3600,
  "user": {
    "id": 1,
    "name": "Nguyễn Văn A",
    "email": "user@vnpt.vn",
    "role": "employee"
  }
}
```

### POST `/auth/refresh`
Làm mới access token.

**Request Body:**
```json
{
  "refresh_token": "eyJ0eXAiOiJKV1QiLCJhbGc..."
}
```

### POST `/auth/logout`
Đăng xuất và vô hiệu hóa token.

---

## 2. Competency APIs

### GET `/competencies`
Lấy danh sách tất cả năng lực.

**Query Parameters:**
- `group_code`: Filter theo nhóm (CORE/LEAD/FUNC)
- `job_family_id`: Filter theo họ công việc
- `page`: Trang (default: 1)
- `limit`: Số lượng/trang (default: 20)

**Response (200):**
```json
{
  "data": [
    {
      "id": 1,
      "name": "Định hướng mục tiêu và kết quả",
      "code": "GOAL_RESULT",
      "definition": "Tư duy hướng tới việc...",
      "group": {
        "id": 1,
        "name": "Năng lực Chung",
        "code": "CORE"
      },
      "levels": [
        {
          "level": 1,
          "description": "Nắm rõ các nhiệm vụ..."
        }
      ]
    }
  ],
  "pagination": {
    "page": 1,
    "limit": 20,
    "total": 25,
    "pages": 2
  }
}
```

### GET `/competencies/{id}`
Lấy chi tiết một năng lực.

**Response (200):**
```json
{
  "id": 1,
  "name": "Định hướng mục tiêu và kết quả",
  "code": "GOAL_RESULT",
  "definition": "Tư duy hướng tới việc...",
  "group": {
    "id": 1,
    "name": "Năng lực Chung",
    "code": "CORE"
  },
  "job_family": {
    "id": 5,
    "name": "Kỹ thuật viên"
  },
  "levels": [
    {
      "level": 1,
      "description": "Nắm rõ các nhiệm vụ, yêu cầu..."
    },
    {
      "level": 2,
      "description": "Nắm được mục tiêu tháng, quý..."
    }
  ]
}
```

### POST `/competencies`
Tạo năng lực mới (Admin only).

**Request Body:**
```json
{
  "name": "Năng lực mới",
  "code": "NEW_COMP",
  "definition": "Định nghĩa năng lực",
  "group_id": 1,
  "job_family_id": 5,
  "levels": [
    {
      "level": 1,
      "description": "Mô tả cấp độ 1"
    }
  ]
}
```

### PUT `/competencies/{id}`
Cập nhật năng lực (Admin only).

### DELETE `/competencies/{id}`
Xóa năng lực (Admin only).

---

## 3. Employee APIs

### GET `/employees`
Lấy danh sách nhân viên.

**Query Parameters:**
- `job_sub_family_id`: Filter theo họ công việc con
- `search`: Tìm kiếm theo tên/email
- `page`, `limit`

**Response (200):**
```json
{
  "data": [
    {
      "id": 1,
      "name": "Nguyễn Văn A",
      "email": "nva@vnpt.vn",
      "job_sub_family": {
        "id": 1,
        "name": "Kỹ thuật viên mạng",
        "family": {
          "name": "Kỹ thuật viên",
          "block": {
            "name": "Vận hành nội bộ"
          }
        }
      },
      "competencies_assessed": 15,
      "avg_competency_level": 3.2
    }
  ]
}
```

### GET `/employees/{id}`
Lấy thông tin chi tiết nhân viên.

**Response (200):**
```json
{
  "id": 1,
  "name": "Nguyễn Văn A",
  "email": "nva@vnpt.vn",
  "job_sub_family": {...},
  "assessments": [
    {
      "id": 1,
      "competency": {
        "id": 1,
        "name": "Định hướng mục tiêu"
      },
      "current_level": 3,
      "target_level": 4,
      "assessed_date": "2025-11-20",
      "assessor": {
        "name": "Trần Thị B"
      }
    }
  ],
  "competency_gaps": [
    {
      "competency": "Lãnh đạo chuyển đổi",
      "gap": 2,
      "priority": "high"
    }
  ]
}
```

### POST `/employees`
Tạo nhân viên mới (Admin/HR only).

### PUT `/employees/{id}`
Cập nhật thông tin nhân viên.

### DELETE `/employees/{id}`
Xóa nhân viên (Admin only).

---

## 4. Assessment APIs

### POST `/assessments`
Tạo đánh giá năng lực mới.

**Request Body:**
```json
{
  "employee_id": 1,
  "competency_id": 1,
  "assessed_level": 3,
  "target_level": 4,
  "notes": "Nhân viên thể hiện tốt...",
  "assessment_type": "self|manager|360",
  "assessment_date": "2025-11-22"
}
```

**Response (201):**
```json
{
  "id": 123,
  "employee": {...},
  "competency": {...},
  "assessed_level": 3,
  "target_level": 4,
  "gap": 1,
  "notes": "Nhân viên thể hiện tốt...",
  "assessment_type": "manager",
  "assessed_by": {...},
  "assessment_date": "2025-11-22",
  "created_at": "2025-11-22T10:30:00Z"
}
```

### GET `/assessments`
Lấy danh sách đánh giá.

**Query Parameters:**
- `employee_id`: Filter theo nhân viên
- `competency_id`: Filter theo năng lực
- `assessment_type`: Filter theo loại đánh giá
- `from_date`, `to_date`: Filter theo thời gian

### GET `/assessments/{id}`
Lấy chi tiết một đánh giá.

### PUT `/assessments/{id}`
Cập nhật đánh giá.

### DELETE `/assessments/{id}`
Xóa đánh giá.

---

## 5. Job Structure APIs

### GET `/job-blocks`
Lấy danh sách khối công việc.

### GET `/job-families`
Lấy danh sách họ công việc.

**Query Parameters:**
- `block_id`: Filter theo khối

### GET `/job-sub-families`
Lấy danh sách họ công việc con.

**Query Parameters:**
- `family_id`: Filter theo họ công việc

---

## 6. Report APIs

### GET `/reports/employee/{id}`
Báo cáo năng lực cá nhân.

**Response (200):**
```json
{
  "employee": {...},
  "competency_summary": {
    "total_competencies": 20,
    "assessed_competencies": 15,
    "avg_level": 3.2,
    "competencies_by_group": {
      "CORE": {"avg": 3.5, "count": 10},
      "LEAD": {"avg": 2.8, "count": 5},
      "FUNC": {"avg": 3.0, "count": 5}
    }
  },
  "strengths": [
    {"competency": "Định hướng mục tiêu", "level": 5}
  ],
  "gaps": [
    {"competency": "Lãnh đạo chuyển đổi", "gap": 2}
  ],
  "development_plan": [...]
}
```

### GET `/reports/team`
Báo cáo năng lực team/phòng ban.

### GET `/reports/organization`
Báo cáo tổng thể tổ chức (Admin only).

### POST `/reports/export`
Export báo cáo ra PDF/Excel.

**Request Body:**
```json
{
  "report_type": "employee|team|organization",
  "format": "pdf|excel",
  "employee_id": 1,
  "date_range": {
    "from": "2025-01-01",
    "to": "2025-12-31"
  }
}
```

---

## Error Responses

### 400 Bad Request
```json
{
  "error": "ValidationError",
  "message": "Invalid input data",
  "details": {
    "email": ["Invalid email format"]
  }
}
```

### 401 Unauthorized
```json
{
  "error": "Unauthorized",
  "message": "Invalid or expired token"
}
```

### 403 Forbidden
```json
{
  "error": "Forbidden",
  "message": "You don't have permission to access this resource"
}
```

### 404 Not Found
```json
{
  "error": "NotFound",
  "message": "Resource not found"
}
```

### 500 Internal Server Error
```json
{
  "error": "InternalServerError",
  "message": "An unexpected error occurred"
}
```

---

## Rate Limiting
- **General endpoints**: 100 requests/minute
- **Authentication**: 5 requests/minute
- **Report generation**: 10 requests/hour

---

**Version**: 1.0  
**Last Updated**: 2025-11-22