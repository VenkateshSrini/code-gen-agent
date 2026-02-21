# Implementation Plan

## 1. Summary

Build a FastAPI-based Task Management API with JWT authentication, task CRUD, category management, and filtering backed by PostgreSQL and SQLAlchemy. The implementation will follow the layered service architecture (routes → services → repositories → models) with Redis-backed caching and rate limiting, and will be containerized for Docker/Kubernetes deployment while meeting the project's security, performance, and observability standards.

## 2. Technical Context

**Stack**: Python 3.14, FastAPI, SQLAlchemy 2.0, PostgreSQL 15+, PyJWT, bcrypt, Redis, pytest/pytest-asyncio  
**Architecture**: Monolithic FastAPI application with layered services architecture (API Routes → Services → Repositories → Models) and dependency injection  
**Database**: PostgreSQL 15+ with SQLAlchemy ORM; Redis for caching and rate limiting  
**Constraints**: p95 response time < 200ms, 1000 concurrent users, >80% test coverage, input validation and security controls by default  
**Deployment**: Dockerized app with Docker Compose (app + PostgreSQL + Redis) and Kubernetes-ready configuration (health checks, environment-based config)

## 3. Constitution Check

- [ ] Test-First Development: Write tests before implementation, ensure initial failures, and reach >80% coverage.
- [ ] Clean Code & Documentation: Use clear naming, full docstrings, and type hints throughout.
- [ ] API-First Design: Define request/response schemas and versioned endpoints before implementation.
- [ ] Security by Default: Validate input, enforce auth, handle secrets via env vars, and avoid unsafe output.
- [ ] Performance Consciousness: Optimize queries, index filters, and use caching for hot reads.
- [ ] Observability: Provide structured logging, correlation IDs, metrics, and health checks.
- [ ] Error Handling: Meaningful errors, proper exception use, and user-friendly messages.
- [ ] Code Organization: Maintain DDD layers, DI for services, and focused methods.

## 4. Project Structure

```
src/
├── main.py
├── api/
│   ├── v1/
│   │   ├── auth.py
│   │   ├── tasks.py
│   │   └── categories.py
│   └── dependencies.py
├── models/
│   ├── user.py
│   ├── task.py
│   ├── category.py
│   └── task_category.py
├── schemas/
│   ├── auth.py
│   ├── task.py
│   └── category.py
├── services/
│   ├── auth_service.py
│   ├── task_service.py
│   ├── category_service.py
│   └── email_service.py
├── repositories/
│   ├── user_repo.py
│   ├── task_repo.py
│   └── category_repo.py
├── core/
│   ├── config.py
│   ├── security.py
│   ├── logging.py
│   └── rate_limiter.py
├── db/
│   ├── session.py
│   └── migrations/
└── utils/
    ├── pagination.py
    ├── validators.py
    └── time.py

tests/
├── unit/
│   ├── test_auth_service.py
│   ├── test_task_service.py
│   └── test_category_service.py
├── integration/
│   ├── test_auth_routes.py
│   ├── test_task_routes.py
│   └── test_category_routes.py
└── contract/
    └── test_openapi_contracts.py
```

## 5. Data Model

### User
- **Fields**: id (UUID), email (str), password_hash (str), full_name (str), is_active (bool), created_at (datetime), updated_at (datetime)
- **Relationships**: User 1→N Tasks; User 1→N Categories
- **Validation**: Email format/uniqueness; password complexity; full_name required

### Task
- **Fields**: id (UUID), user_id (UUID), title (str), description (str | null), status (enum), priority (enum), due_date (datetime | null), created_at (datetime), updated_at (datetime), deleted_at (datetime | null), version (int)
- **Relationships**: Task N→1 User; Task N↔N Category (via task_categories)
- **Validation**: title length 3–200; description <= 2000; due_date in future; status/priority enums; optimistic locking on version

### Category
- **Fields**: id (UUID), user_id (UUID), name (str), color (str | null), created_at (datetime)
- **Relationships**: Category N→1 User; Category N↔N Task (via task_categories)
- **Validation**: name length 3–50; color hex if provided; unique (user_id, name)

### TaskCategory
- **Fields**: task_id (UUID), category_id (UUID)
- **Relationships**: Many-to-many join between Task and Category
- **Validation**: unique pair (task_id, category_id)

## 6. API Contracts

### US-1.1 Register
**POST** `/api/v1/auth/register`
- **Request**: `{ "email": "string", "password": "string", "full_name": "string" }`
- **Response 201**: `{ "access_token": "string", "refresh_token": "string", "token_type": "bearer", "user": {"id": "uuid", "email": "string", "full_name": "string", "is_active": false} }`
- **Errors**: 400 (validation), 409 (email exists)
- **Auth**: None

### US-1.2 Login
**POST** `/api/v1/auth/login`
- **Request**: `{ "email": "string", "password": "string" }`
- **Response 200**: `{ "access_token": "string", "refresh_token": "string", "token_type": "bearer", "expires_in": 3600 }`
- **Errors**: 401 (invalid), 423 (locked out), 429 (rate limit)
- **Auth**: None

### Refresh Token
**POST** `/api/v1/auth/refresh`
- **Request**: `{ "refresh_token": "string" }`
- **Response 200**: `{ "access_token": "string", "refresh_token": "string", "token_type": "bearer", "expires_in": 3600 }`
- **Errors**: 401 (invalid/expired)
- **Auth**: None

### US-2.1 Create Task
**POST** `/api/v1/tasks`
- **Request**: `{ "title": "string", "description": "string?", "due_date": "datetime?", "priority": "low|medium|high" }`
- **Response 201**: `{ "id": "uuid", "title": "string", "description": "string?", "due_date": "datetime?", "priority": "low|medium|high", "status": "pending", "created_at": "datetime", "updated_at": "datetime" }`
- **Errors**: 400 (validation), 401 (unauth)
- **Auth**: Bearer JWT

### US-2.2 List Tasks
**GET** `/api/v1/tasks`
- **Query**: `page`, `limit`, `status`, `priority`, `due_from`, `due_to`, `sort`
- **Response 200**: `{ "items": [Task], "total": 0, "page": 1, "limit": 20 }`
- **Errors**: 400 (invalid params), 401 (unauth)
- **Auth**: Bearer JWT

### US-2.3 Update Task
**PATCH** `/api/v1/tasks/{task_id}`
- **Request**: partial Task fields (title/description/due_date/priority/status) + `version`
- **Response 200**: updated Task
- **Errors**: 400 (validation), 401 (unauth), 403 (forbidden), 404 (not found), 409 (version conflict)
- **Auth**: Bearer JWT

### US-2.4 Delete Task
**DELETE** `/api/v1/tasks/{task_id}`
- **Response 204**: No Content
- **Errors**: 401 (unauth), 403 (forbidden), 404 (not found)
- **Auth**: Bearer JWT

### US-3.1 Create Category
**POST** `/api/v1/categories`
- **Request**: `{ "name": "string", "color": "#RRGGBB?" }`
- **Response 201**: `{ "id": "uuid", "name": "string", "color": "#RRGGBB", "created_at": "datetime" }`
- **Errors**: 400 (validation), 409 (duplicate)
- **Auth**: Bearer JWT

### List Categories
**GET** `/api/v1/categories`
- **Response 200**: `{ "items": [Category], "total": 0 }`
- **Errors**: 401 (unauth)
- **Auth**: Bearer JWT

### Delete Category
**DELETE** `/api/v1/categories/{cat_id}`
- **Response 204**: No Content
- **Errors**: 401 (unauth), 403 (forbidden), 404 (not found)
- **Auth**: Bearer JWT

### US-3.2 Assign Category
**POST** `/api/v1/tasks/{task_id}/categories/{cat_id}`
- **Response 200**: Task with categories
- **Errors**: 400 (duplicate), 401 (unauth), 403 (forbidden), 404 (not found)
- **Auth**: Bearer JWT

### Remove Category
**DELETE** `/api/v1/tasks/{task_id}/categories/{cat_id}`
- **Response 204**: No Content
- **Errors**: 401 (unauth), 403 (forbidden), 404 (not found)
- **Auth**: Bearer JWT

### Health Check
**GET** `/health`
- **Response 200**: `{ "status": "ok" }`
- **Auth**: None

## 7. Implementation Phases

### Phase 0: Research
- Validate FastAPI + SQLAlchemy 2.0 async patterns and session management.
- Confirm PyJWT token rotation best practices and Redis-based rate limiting.
- Review bcrypt and email verification token storage best practices.

### Phase 1: Foundation
- Initialize project structure, configuration, and dependency management.
- Define SQLAlchemy models and Alembic migrations for all entities.
- Implement DB session lifecycle and repository base classes.
- Build security utilities (hashing, JWT creation/verification).
- Set up logging (JSON), correlation IDs, and health check endpoint.
- Implement Redis client and rate limiting middleware.

### Phase 2: Core Features
- **US-1.1 Registration**: user creation, email verification token, and initial auth responses.
- **US-1.2 Login/Refresh**: credential validation, lockout tracking, refresh token rotation.
- **US-2.1 Create Task**: validation, ownership association, timestamps.
- **US-2.2 List Tasks**: filtering, pagination, sorting, and total counts.
- **US-2.3 Update Task**: PATCH handling, optimistic locking, validation.
- **US-2.4 Delete Task**: soft delete and exclusion from list queries.
- **US-3.1 Category CRUD**: create/list/delete with per-user uniqueness.
- **US-3.2 Assign/Remove Category**: junction table operations and validation.

### Phase 3: Testing & Polish
- Unit tests for services and validators; integration tests for all routes.
- Contract tests for OpenAPI schemas and error responses.
- Performance checks for list queries, indexing, and cache behavior.
- Security review: auth enforcement, rate limit behavior, input validation.
- Documentation review: OpenAPI tags, descriptions, and examples.

## 8. Risk Assessment

- **JWT/Refresh Token Security**: Risk of token misuse; mitigate with rotation, short-lived access tokens, and revocation storage in DB/Redis.
- **Rate Limiting Accuracy**: Sliding window correctness in Redis; mitigate with integration tests and time-based simulations.
- **Optimistic Locking Conflicts**: Potential update errors; mitigate with clear 409 responses and client guidance.
- **Email Verification Flow**: Deliverability in prod vs dev stub; mitigate with configurable SMTP and robust token expiration handling.
- **Performance Under Load**: Filtered task queries and joins; mitigate with indexes, query profiling, and caching.
- **Many-to-Many Integrity**: Duplicate or unauthorized category assignment; mitigate with DB constraints and ownership checks.