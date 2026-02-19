# Project Specification: Task Management API

**Project**: Task Management System  
**Version**: 1.0.0  
**Author**: Development Team  
**Date**: 2026-02-18

## Overview

Build a RESTful API for managing tasks with support for user authentication, task CRUD operations, task categorization, and task filtering.

## User Stories

### Epic 1: User Management

#### US-1.1: User Registration
**As a** new user  
**I want to** register an account with email and password  
**So that** I can create and manage my tasks

**Acceptance Criteria**:
- User provides email, password, and full name
- Email must be unique and valid format
- Password must be 8+ characters with complexity requirements
- Confirmation email sent upon successful registration
- User account created in inactive state until email verified
- Returns JWT token upon successful registration

**Technical Notes**:
- Use bcrypt for password hashing
- Email validation regex pattern
- Store user in database with created_at timestamp

---

#### US-1.2: User Authentication
**As a** registered user  
**I want to** login with email and password  
**So that** I can access my tasks

**Acceptance Criteria**:
- User provides email and password
- System validates credentials
- Returns JWT token with 24-hour expiration
- Token includes user ID and email in payload
- Failed login tracked (max 5 attempts, then lockout)
- Returns 401 for invalid credentials

**Technical Notes**:
- JWT secret from environment variable
- Use refresh token pattern for extended sessions
- Rate limiting on login endpoint

---

### Epic 2: Task Management

#### US-2.1: Create Task
**As a** authenticated user  
**I want to** create a new task with title, description, and due date  
**So that** I can track my work

**Acceptance Criteria**:
- Authenticated users only (JWT required)
- Title is required (3-200 characters)
- Description is optional (max 2000 characters)
- Due date is optional (must be future date)
- Priority can be: low, medium, high (default: medium)
- Status defaults to 'pending'
- Task linked to authenticated user
- Returns created task with ID and timestamps

**Technical Notes**:
- Use UUID for task IDs
- Store created_at and updated_at timestamps
- Validate future dates for due_date

---

#### US-2.2: List Tasks
**As a** authenticated user  
**I want to** view all my tasks with filtering and pagination  
**So that** I can manage my workload

**Acceptance Criteria**:
- Returns only tasks owned by authenticated user
- Support pagination (default: 20 items per page)
- Filter by status: pending, in_progress, completed
- Filter by priority: low, medium, high
- Filter by due date range (from/to)
- Sort by: created_at, updated_at, due_date, priority (default: created_at desc)
- Returns total count for pagination

**Technical Notes**:
- Query optimization to prevent N+1
- Use database indexes for frequently filtered fields
- Validate pagination parameters (page >= 1, limit <= 100)

---

#### US-2.3: Update Task
**As a** authenticated user  
**I want to** update task details  
**So that** I can keep tasks current

**Acceptance Criteria**:
- Authenticated users only
- Can only update own tasks (authorization check)
- Can update: title, description, due_date, priority, status
- Cannot update: id, user_id, created_at
- updated_at timestamp automatically set
- Returns 404 if task not found
- Returns 403 if task belongs to different user
- Returns updated task

**Technical Notes**:
- Use PATCH for partial updates
- Validate all fields same as create
- Optimistic locking with version field

---

#### US-2.4: Delete Task
**As a** authenticated user  
**I want to** delete a task  
**So that** I can remove completed or cancelled tasks

**Acceptance Criteria**:
- Authenticated users only
- Can only delete own tasks
- Soft delete (mark as deleted, don't remove from DB)
- Returns 204 No Content on success
- Returns 404 if task not found
- Returns 403 if task belongs to different user

**Technical Notes**:
- Add deleted_at timestamp field
- Exclude deleted tasks from list queries
- Consider hard delete after 30 days (background job)

---

### Epic 3: Categories

#### US-3.1: Create Category
**As a** authenticated user  
**I want to** create categories for organizing tasks  
**So that** I can group related tasks

**Acceptance Criteria**:
- Category has name (required, 3-50 characters)
- Category has color code (optional, hex format)
- Category name unique per user
- User can create unlimited categories
- Returns created category with ID

**Technical Notes**:
- Composite unique index on (user_id, name)
- Default color if not provided

---

#### US-3.2: Assign Category to Task
**As a** authenticated user  
**I want to** assign one or more categories to a task  
**So that** I can organize tasks efficiently

**Acceptance Criteria**:
- Task can have multiple categories
- Category must exist and belong to user
- Cannot assign duplicate categories to same task
- Returns updated task with categories

**Technical Notes**:
- Many-to-many relationship (task_categories junction table)
- Validate category ownership before assignment

---

## Technical Requirements

### Technology Stack
- **Language**: Python 3.11+
- **Framework**: FastAPI
- **Database**: PostgreSQL 15+
- **ORM**: SQLAlchemy 2.0
- **Authentication**: JWT (PyJWT)
- **Testing**: pytest, pytest-asyncio
- **API Docs**: OpenAPI/Swagger (auto-generated by FastAPI)

### API Endpoints

```
POST   /api/v1/auth/register       - Register new user
POST   /api/v1/auth/login          - Login user
POST   /api/v1/auth/refresh        - Refresh JWT token

GET    /api/v1/tasks               - List tasks (with filters)
POST   /api/v1/tasks               - Create task
GET    /api/v1/tasks/{task_id}     - Get task details
PATCH  /api/v1/tasks/{task_id}     - Update task
DELETE /api/v1/tasks/{task_id}     - Delete task

GET    /api/v1/categories          - List categories
POST   /api/v1/categories          - Create category
DELETE /api/v1/categories/{cat_id} - Delete category

POST   /api/v1/tasks/{task_id}/categories/{cat_id}   - Assign category
DELETE /api/v1/tasks/{task_id}/categories/{cat_id}   - Remove category

GET    /health                     - Health check
```

### Database Schema

**users**:
- id (UUID, PK)
- email (VARCHAR, UNIQUE, NOT NULL)
- password_hash (VARCHAR, NOT NULL)
- full_name (VARCHAR, NOT NULL)
- is_active (BOOLEAN, DEFAULT FALSE)
- created_at (TIMESTAMP)
- updated_at (TIMESTAMP)

**tasks**:
- id (UUID, PK)
- user_id (UUID, FK → users.id)
- title (VARCHAR(200), NOT NULL)
- description (TEXT)
- status (ENUM: pending, in_progress, completed)
- priority (ENUM: low, medium, high)
- due_date (TIMESTAMP)
- created_at (TIMESTAMP)
- updated_at (TIMESTAMP)
- deleted_at (TIMESTAMP, NULL)
- version (INTEGER, for optimistic locking)

**categories**:
- id (UUID, PK)
- user_id (UUID, FK → users.id)
- name (VARCHAR(50), NOT NULL)
- color (VARCHAR(7))
- created_at (TIMESTAMP)
- UNIQUE(user_id, name)

**task_categories**:
- task_id (UUID, FK → tasks.id)
- category_id (UUID, FK → categories.id)
- PRIMARY KEY (task_id, category_id)

### Non-Functional Requirements

**Performance**:
- API response time < 200ms (p95)
- Support 1000 concurrent users
- Database query optimization (indexed fields)

**Security**:
- HTTPS only in production
- JWT tokens with short expiration
- Rate limiting: 100 requests/minute per user
- SQL injection prevention (parameterized queries)
- XSS prevention (input sanitization)

**Testing**:
- Unit test coverage > 80%
- Integration tests for all endpoints
- Load testing with realistic scenarios

**Observability**:
- Structured logging (JSON format)
- Request tracing with correlation IDs
- Metrics: request count, response time, error rate
- Health check endpoint

## Success Criteria

1. All user stories implemented with acceptance criteria met
2. Test coverage > 80%
3. API documentation complete and accurate
4. Performance benchmarks met
5. Security audit passed
6. Constitution compliance verified
