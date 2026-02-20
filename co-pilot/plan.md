# Implementation Plan

## 1. Summary

This plan delivers a FastAPI-based Task Management API with JWT authentication, task CRUD, categories, filtering, and observability backed by PostgreSQL and Redis. The stack targets Python 3.14 with SQLAlchemy 2.0, PyJWT, bcrypt, and pytest to meet the security, performance, and test-first requirements.

## 2. Technical Context

**Stack**: Python 3.14, FastAPI, SQLAlchemy 2.0, Pydantic, PyJWT, bcrypt, pytest, pytest-asyncio, Redis client  
**Architecture**: Monolithic FastAPI, layered services (API routes → services → repositories → models), dependency injection  
**Database**: PostgreSQL 15+, Redis 7+ for caching and rate limiting  
**Constraints**: p95 < 200ms, 1000 concurrent users, coverage >= 80%, rate limits 100 req/min per user, 20 req/min per IP  
**Deployment**: Docker/Docker Compose for local, Kubernetes for production, health checks

## 3. Constitution Check

- [ ] Test-First Development: tests written before implementation, initial failures, coverage >= 80%
- [ ] Clean Code & Documentation: clear naming, docstrings, type hints, review readiness
- [ ] API-First Design: OpenAPI contracts defined and versioned before implementation
- [ ] Security by Default: validation, auth, secrets in env, rate limiting
- [ ] Performance Consciousness: indexed queries, caching, async I/O, p95 < 200ms
- [ ] Observability: structured logs, correlation IDs, metrics, tracing, health checks
- [ ] Error Handling: meaningful error messages, contextual logging, no stack traces to users
- [ ] Code Organization: layered services, DI, separation of concerns

## 4. Project Structure

```
project-root/
├── constitution.md
├── spec.md
├── plan.md
├── tasks.md
├── implementation.md
└── outputs/
    ├── src/
    │   ├── main.py
    │   ├── api/
    │   │   └── v1/
    │   │       ├── auth.py
    │   │       ├── tasks.py
    │   │       ├── categories.py
    │   │       └── health.py
    │   ├── core/
    │   │   ├── config.py
    │   │   ├── security.py
    │   │   ├── logging.py
    │   │   ├── rate_limit.py
    │   │   └── tracing.py
    │   ├── db/
    │   │   ├── base.py
    │   │   ├── session.py
    │   │   └── migrations/
    │   ├── models/
    │   │   ├── user.py
    │   │   ├── task.py
    │   │   ├── category.py
    │   │   ├── task_category.py
    │   │   ├── refresh_token.py
    │   │   └── email_verification.py
    │   ├── repositories/
    │   │   ├── user_repo.py
    │   │   ├── task_repo.py
    │   │   ├── category_repo.py
    │   │   ├── token_repo.py
    │   │   └── email_verification_repo.py
    │   ├── schemas/
    │   │   ├── auth.py
    │   │   ├── task.py
    │   │   ├── category.py
    │   │   ├── pagination.py
    │   │   └── errors.py
    │   ├── services/
    │   │   ├── auth_service.py
    │   │   ├── task_service.py
    │   │   ├── category_service.py
    │   │   ├── token_service.py
    │   │   ├── email_service.py
    │   │   └── cache_service.py
    │   └── utils/
    │       ├── validators.py
    │       ├── datetime.py
    │       └── pagination.py
    └── tests/
        ├── unit/
        ├── integration/
        └── contract/
```

## 5. Data Model

- User
  - Fields: id UUID, email str, password_hash str, full_name str, is_active bool, failed_login_count int, locked_until datetime?, created_at datetime, updated_at datetime
  - Relationships: has many tasks, categories, refresh_tokens, email_verification_tokens
  - Validation: email unique + regex, password complexity at API boundary, full_name required
- Task
  - Fields: id UUID, user_id UUID, title str(3-200), description str?(<=2000), status enum, priority enum, due_date datetime?, created_at datetime, updated_at datetime, deleted_at datetime?, version int
  - Relationships: belongs to user, many-to-many categories via task_categories
  - Validation: due_date future, status and priority enums
- Category
  - Fields: id UUID, user_id UUID, name str(3-50), color str?(hex), created_at datetime
  - Relationships: belongs to user, many-to-many tasks via task_categories
  - Validation: unique (user_id, name), color hex
- TaskCategory
  - Fields: task_id UUID, category_id UUID
  - Relationships: join table, composite PK
- RefreshToken
  - Fields: id UUID, user_id UUID, token_hash str, expires_at datetime, created_at datetime, revoked_at datetime?, rotated_from UUID?
  - Relationships: belongs to user
- EmailVerificationToken
  - Fields: id UUID, user_id UUID, token_hash str, expires_at datetime, created_at datetime, used_at datetime?
  - Relationships: belongs to user

## 6. API Contracts

### Shared Schemas
- Task: { id, user_id, title, description?, status, priority, due_date?, created_at, updated_at, deleted_at?, version }
- Category: { id, user_id, name, color?, created_at }
- User: { id, email, full_name, is_active, created_at, updated_at }

### US-1.1 Register
- Endpoint: POST /api/v1/auth/register
- Auth: none
- Request: { email, password, full_name }
- Response: 201 { access_token, refresh_token, token_type, expires_in, user }
- Status codes: 201, 400, 409

### US-1.2 Login
- Endpoint: POST /api/v1/auth/login
- Auth: none
- Request: { email, password }
- Response: 200 { access_token, refresh_token, token_type, expires_in, user }
- Status codes: 200, 401, 423, 429

### Auth Refresh
- Endpoint: POST /api/v1/auth/refresh
- Auth: refresh token
- Request: { refresh_token }
- Response: 200 { access_token, refresh_token, token_type, expires_in }
- Status codes: 200, 401, 403

### US-2.1 Create Task
- Endpoint: POST /api/v1/tasks
- Auth: bearer JWT
- Request: { title, description?, due_date?, priority? }
- Response: 201 Task
- Status codes: 201, 400, 401

### US-2.2 List Tasks
- Endpoint: GET /api/v1/tasks
- Auth: bearer JWT
- Request: query params page, limit, status?, priority?, due_from?, due_to?, sort?
- Response: 200 { items: [Task], total, page, limit }
- Status codes: 200, 401

### Get Task
- Endpoint: GET /api/v1/tasks/{task_id}
- Auth: bearer JWT
- Response: 200 Task
- Status codes: 200, 401, 403, 404

### US-2.3 Update Task
- Endpoint: PATCH /api/v1/tasks/{task_id}
- Auth: bearer JWT
- Request: { title?, description?, due_date?, priority?, status?, version }
- Response: 200 Task
- Status codes: 200, 400, 401, 403, 404, 409

### US-2.4 Delete Task
- Endpoint: DELETE /api/v1/tasks/{task_id}
- Auth: bearer JWT
- Response: 204
- Status codes: 204, 401, 403, 404

### US-3.1 Create Category
- Endpoint: POST /api/v1/categories
- Auth: bearer JWT
- Request: { name, color? }
- Response: 201 Category
- Status codes: 201, 400, 401, 409

### List Categories
- Endpoint: GET /api/v1/categories
- Auth: bearer JWT
- Response: 200 { items: [Category] }
- Status codes: 200, 401

### Delete Category
- Endpoint: DELETE /api/v1/categories/{cat_id}
- Auth: bearer JWT
- Response: 204
- Status codes: 204, 401, 403, 404

### US-3.2 Assign Category to Task
- Endpoint: POST /api/v1/tasks/{task_id}/categories/{cat_id}
- Auth: bearer JWT
- Response: 200 Task with categories
- Status codes: 200, 401, 403, 404, 409

### Remove Category from Task
- Endpoint: DELETE /api/v1/tasks/{task_id}/categories/{cat_id}
- Auth: bearer JWT
- Response: 204
- Status codes: 204, 401, 403, 404

### Health
- Endpoint: GET /health
- Auth: none
- Response: 200 { status, version, time }
- Status codes: 200

## 7. Implementation Phases

### Phase 0: Research
- FastAPI async patterns, dependency injection, request lifecycle
- SQLAlchemy 2.0 async sessions, optimistic locking, soft delete patterns
- PyJWT access and refresh token rotation with revocation storage
- Redis sliding window rate limiting and cache-aside patterns
- Email verification token flow and dev console backend
- OpenTelemetry or similar logging, metrics, tracing integration

### Phase 1: Foundation
- Project scaffolding under outputs/src and outputs/tests
- Environment config, secret management, settings validation
- PostgreSQL setup, Alembic migrations, base models
- Core middleware: request ID, structured logging, exception handlers
- Security utilities: bcrypt hashing, JWT helpers, token persistence
- Redis clients for cache and rate limiting
- Health check endpoint and base dependency wiring

### Phase 2: Core Features
- US-1.1 Registration: user creation in inactive state, verification token, email send, initial tokens
- US-1.2 Login: credential validation, failed login tracking, lockout, rate limit checks, tokens
- Auth refresh: token rotation, revoke prior refresh token, update last_used
- US-2.1 Create Task: validation, user linkage, timestamps, defaults
- US-2.2 List Tasks: filters, pagination, sorting, exclude deleted, total count
- US-2.3 Update Task: PATCH validation, optimistic locking on version
- US-2.4 Delete Task: soft delete, exclude in list and get
- US-3.1 Create Category: unique per user, default color handling
- US-3.2 Assign Category: ownership validation, junction insert, prevent duplicates
- Supporting endpoints: get task, list categories, delete category, remove category
- Dependencies: auth foundation before task endpoints, categories before assignment, tasks before assignment

### Phase 3: Testing & Polish
- Unit tests for validators, services, repositories, security helpers
- Integration tests for every endpoint and auth flow
- Contract tests against OpenAPI schemas
- Coverage gate >= 80%
- Performance profiling, indexes on user_id, status, priority, due_date, created_at
- Security verification for input validation, rate limiting, token rotation
- Documentation polish for OpenAPI descriptions and local dev steps

## 8. Risk Assessment

- Python 3.14 ecosystem compatibility risk and CI matrix support [NEEDS CLARIFICATION]
- Redis dependency for rate limiting and cache availability, fail-open vs fail-closed policy [NEEDS CLARIFICATION]
- Token rotation and revocation logic complexity, requires thorough tests
- Email delivery and verification timing issues, need retries and clear error handling
- Optimistic locking conflict handling and client retry guidance
- Filtering performance at scale, needs proper indexing and query plans