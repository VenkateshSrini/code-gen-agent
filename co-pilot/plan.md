# Implementation Plan: Task Management API

**Branch**: `001-task-management-api` | **Date**: 2026-02-24 | **Spec**: specs/001-task-management-api/spec.md  
**Input**: Feature specification from `/specs/001-task-management-api/spec.md`

**Note**: This template is filled in by the `/speckit.plan` command. See `.specify/templates/plan-template.md` for the execution workflow.

## Summary

Build a FastAPI-based Task Management REST API with JWT authentication, task CRUD operations, category management, and filtering/pagination, backed by PostgreSQL and Redis. The implementation will use Python 3.14, SQLAlchemy 2.0, PyJWT, and pytest to deliver a secure, observable, and performance-conscious service with API-first contracts and test-first development.

## Technical Context

**Language/Version**: Python 3.14  
**Primary Dependencies**: FastAPI, SQLAlchemy 2.0, Pydantic v2, PyJWT, bcrypt, Alembic, Redis client (redis-py), pytest, pytest-asyncio  
**Storage**: PostgreSQL 15+, Redis (cache + rate limiting + token/session)  
**Testing**: pytest, pytest-asyncio, coverage.py  
**Target Platform**: Linux server (Docker/Kubernetes), HTTPS in production  
**Project Type**: Web-service (REST API)  
**Performance Goals**: p95 < 200ms, 1000 concurrent users, optimized DB queries, cache-aside for frequent reads  
**Constraints**: 80%+ test coverage, JWT access tokens (1 hour), refresh tokens (7 days), rate limiting (100 req/min user, 20 req/min IP unauthenticated), soft delete tasks, optimistic locking  
**Scale/Scope**: Single monolithic API service, thousands of users, task and category management with filtering and pagination

## Constitution Check

*GATE: Must pass before Phase 0 research. Re-check after Phase 1 design.*

- [ ] **Test-First Development**: Tests will be written before implementation and must initially fail  
- [ ] **Clean Code & Documentation**: Clear naming, docstrings, type hints, and documented modules  
- [ ] **API-First Design**: Define endpoint contracts and schemas before implementation  
- [ ] **Security by Default**: Input validation, JWT auth, bcrypt hashing, secret management via env vars  
- [ ] **Performance Consciousness**: Indexed queries, caching strategy, avoid N+1 queries  
- [ ] **Observability**: Structured logging, correlation IDs, metrics, health checks  
- [ ] **Error Handling**: Meaningful errors, exceptions only for exceptional cases, no stack traces to users  
- [ ] **Code Organization**: Layered architecture, dependency injection, configuration separate from code  

## Project Structure

### Documentation (this feature)

```text
specs/001-task-management-api/
├── plan.md              # This file (/speckit.plan command output)
├── research.md          # Phase 0 output (/speckit.plan command)
├── data-model.md        # Phase 1 output (/speckit.plan command)
├── quickstart.md        # Phase 1 output (/speckit.plan command)
├── contracts/           # Phase 1 output (/speckit.plan command)
└── tasks.md             # Phase 2 output (/speckit.tasks command - NOT created by /speckit.plan)
```

### Source Code (repository root)

```text
src/
├── api/
│   ├── v1/
│   │   ├── auth_routes.py
│   │   ├── task_routes.py
│   │   ├── category_routes.py
│   │   └── health_routes.py
│   └── dependencies.py
├── core/
│   ├── config.py
│   ├── security.py
│   ├── logging.py
│   ├── rate_limit.py
│   └── cache.py
├── db/
│   ├── session.py
│   ├── base.py
│   └── migrations/
├── models/
│   ├── user.py
│   ├── task.py
│   ├── category.py
│   ├── task_category.py
│   ├── refresh_token.py
│   └── email_verification_token.py
├── repositories/
│   ├── user_repo.py
│   ├── task_repo.py
│   ├── category_repo.py
│   └── token_repo.py
├── services/
│   ├── auth_service.py
│   ├── task_service.py
│   ├── category_service.py
│   └── email_service.py
├── schemas/
│   ├── auth.py
│   ├── task.py
│   ├── category.py
│   ├── token.py
│   └── error.py
├── utils/
│   ├── uuid.py
│   ├── time.py
│   └── pagination.py
└── main.py

tests/
├── contract/
├── integration/
└── unit/
```

**Structure Decision**: Single-project FastAPI backend with layered services architecture (API → Services → Repositories → Models), matching the specification and supporting TDD, DI, and clear separation of concerns.

### Data Model

**User**
- Fields:  
  - id: UUID (PK)  
  - email: str (unique, regex-validated)  
  - password_hash: str (bcrypt)  
  - full_name: str  
  - is_active: bool (default False)  
  - created_at: datetime  
  - updated_at: datetime  
- Relationships:  
  - One-to-many: User → Task  
  - One-to-many: User → Category  
  - One-to-many: User → RefreshToken  
  - One-to-many: User → EmailVerificationToken  
- Validations:  
  - Email format (regex), unique  
  - Password ≥ 8 chars, complexity  
  - full_name required  

**Task**
- Fields:  
  - id: UUID (PK)  
  - user_id: UUID (FK → users.id)  
  - title: str (3–200 chars)  
  - description: str (max 2000 chars, optional)  
  - status: enum (pending, in_progress, completed)  
  - priority: enum (low, medium, high; default medium)  
  - due_date: datetime (optional, must be future)  
  - created_at: datetime  
  - updated_at: datetime  
  - deleted_at: datetime (nullable)  
  - version: int (optimistic locking)  
- Relationships:  
  - Many-to-one: Task → User  
  - Many-to-many: Task ↔ Category via TaskCategory  
- Validations:  
  - Title length and required  
  - Due date future  
  - Status/priority in allowed enums  

**Category**
- Fields:  
  - id: UUID (PK)  
  - user_id: UUID (FK → users.id)  
  - name: str (3–50 chars)  
  - color: str (hex #RRGGBB, optional)  
  - created_at: datetime  
- Relationships:  
  - Many-to-one: Category → User  
  - Many-to-many: Category ↔ Task via TaskCategory  
- Validations:  
  - Unique (user_id, name)  
  - Color hex format  

**TaskCategory**
- Fields:  
  - task_id: UUID (PK, FK → tasks.id)  
  - category_id: UUID (PK, FK → categories.id)  
- Relationships:  
  - Junction table for many-to-many  

**RefreshToken**
- Fields:  
  - id: UUID (PK)  
  - user_id: UUID (FK → users.id)  
  - token_hash: str  
  - expires_at: datetime  
  - created_at: datetime  
  - revoked_at: datetime (nullable)  
- Validations:  
  - One active token per device/session (policy)  

**EmailVerificationToken**
- Fields:  
  - id: UUID (PK)  
  - user_id: UUID (FK → users.id)  
  - token_hash: str  
  - expires_at: datetime  
  - created_at: datetime  
  - used_at: datetime (nullable)  
- Validations:  
  - Short TTL (e.g., 24 hours)  

**Additional Data (Redis)**
- Login attempt counters per user/IP for lockout  
- Rate limiter sliding window tokens  
- Cached user profile data (15 minutes)  
- Access token cache (optional, for revocation)  

### API Contracts

**US-1.1: User Registration**
- **POST /api/v1/auth/register**
- Auth: None  
- Request:
  - email: string  
  - password: string  
  - full_name: string  
- Response 201:
  - user: { id, email, full_name, is_active, created_at }
  - access_token: string  
  - refresh_token: string  
- Errors:
  - 400 (validation)  
  - 409 (email already exists)  

**US-1.2: User Authentication**
- **POST /api/v1/auth/login**
- Auth: None  
- Request:
  - email: string  
  - password: string  
- Response 200:
  - access_token: string (exp 1h)  
  - refresh_token: string (exp 7d)  
  - user: { id, email, full_name }  
- Errors:
  - 401 (invalid credentials)  
  - 429 (too many attempts)  

**Refresh Token**
- **POST /api/v1/auth/refresh**
- Auth: Refresh token required  
- Request:
  - refresh_token: string  
- Response 200:
  - access_token: string  
  - refresh_token: string (rotated)  
- Errors:
  - 401 (invalid/expired token)  

**US-2.1: Create Task**
- **POST /api/v1/tasks**
- Auth: Bearer JWT  
- Request:
  - title: string  
  - description: string (optional)  
  - due_date: datetime (optional)  
  - priority: low|medium|high (optional)  
- Response 201:
  - task: { id, user_id, title, description, status, priority, due_date, created_at, updated_at }  
- Errors:
  - 401 (unauthorized)  
  - 400 (validation)  

**US-2.2: List Tasks**
- **GET /api/v1/tasks**
- Auth: Bearer JWT  
- Query Params:
  - page: int (>=1)  
  - limit: int (<=100)  
  - status: pending|in_progress|completed  
  - priority: low|medium|high  
  - due_from: datetime  
  - due_to: datetime  
  - sort: created_at|updated_at|due_date|priority  
  - order: asc|desc  
- Response 200:
  - data: [task...]  
  - total: int  
  - page: int  
  - limit: int  
- Errors:
  - 401 (unauthorized)  
  - 400 (invalid params)  

**US-2.3: Update Task**
- **PATCH /api/v1/tasks/{task_id}**
- Auth: Bearer JWT  
- Request:
  - title?: string  
  - description?: string  
  - due_date?: datetime  
  - priority?: enum  
  - status?: enum  
  - version: int (required for optimistic locking)  
- Response 200:
  - task: { ...updated fields... }  
- Errors:
  - 401, 403 (not owner), 404 (not found), 409 (version conflict)  

**US-2.4: Delete Task**
- **DELETE /api/v1/tasks/{task_id}**
- Auth: Bearer JWT  
- Response 204: No Content  
- Errors:
  - 401, 403, 404  

**US-3.1: Create Category**
- **POST /api/v1/categories**
- Auth: Bearer JWT  
- Request:
  - name: string  
  - color?: string (hex)  
- Response 201:
  - category: { id, user_id, name, color, created_at }  
- Errors:
  - 401, 409 (duplicate), 400  

**List Categories**
- **GET /api/v1/categories**
- Auth: Bearer JWT  
- Response 200:
  - data: [category...]  

**Delete Category**
- **DELETE /api/v1/categories/{cat_id}**
- Auth: Bearer JWT  
- Response 204  
- Errors: 401, 403, 404  

**US-3.2: Assign Category to Task**
- **POST /api/v1/tasks/{task_id}/categories/{cat_id}**
- Auth: Bearer JWT  
- Response 200:
  - task: { ... , categories: [category...] }  
- Errors:
  - 401, 403, 404, 409 (duplicate assignment)  

**Remove Category from Task**
- **DELETE /api/v1/tasks/{task_id}/categories/{cat_id}**
- Auth: Bearer JWT  
- Response 204  
- Errors: 401, 403, 404  

**Health Check**
- **GET /health**
- Response 200:
  - status: "ok"  
  - uptime: seconds  
  - version: string  

### Implementation Phases

**Phase 0: Research**
- FastAPI best practices for layered architecture and dependency injection  
- SQLAlchemy 2.0 async patterns and performance optimization  
- JWT access/refresh token rotation security patterns  
- Redis sliding window rate limiting implementation  
- Email verification token storage and expiration handling  
- Observability patterns (structured logging, tracing, metrics)

**Phase 1: Foundation**
- Project scaffolding with Docker, Docker Compose, base config  
- Settings management with environment variables  
- Database models, migrations (Alembic), base repository layer  
- Core security utilities (bcrypt hashing, JWT issuance/verification)  
- Redis cache + rate limiter utilities  
- Logging setup (JSON structured logs + correlation IDs)  
- Base testing harness and fixtures  

**Phase 2: Core Features**
- **US-1.1 Registration**: DB model, validation, email verification service, JWT issuance  
- **US-1.2 Login**: credential validation, lockout, JWT + refresh flow  
- **US-2.1 Create Task**: service logic, validation, tests  
- **US-2.2 List Tasks**: filtering, sorting, pagination, optimized queries  
- **US-2.3 Update Task**: patch semantics, optimistic locking, ownership check  
- **US-2.4 Delete Task**: soft delete behavior  
- **US-3.1 Categories**: create/list/delete with uniqueness rules  
- **US-3.2 Assign Categories**: many-to-many operations + validation  

**Phase 3: Testing & Polish**
- Unit tests + integration tests for all endpoints  
- Contract tests for API schemas  
- Coverage enforcement (>80%)  
- Performance checks (query optimization, cache validation)  
- API documentation review (OpenAPI)  
- Security audit checklist (JWT, hashing, validation)  

### Risk Assessment

- **JWT token rotation complexity**: Mitigate with strict refresh token storage + rotation logic  
- **Rate limiting correctness**: Use tested Redis sliding window algorithm and integration tests  
- **Optimistic locking conflicts**: Ensure version checks and 409 responses in update logic  
- **Email verification flow**: Provide stub service for dev and ensure token expiry handling  
- **Query performance**: Add proper indexes and validate query plans with filters  
- **Concurrency issues**: Use SQLAlchemy transaction boundaries and versioning  

## Complexity Tracking

No constitution violations identified; complexity tracking not required.