# Task Breakdown: Task Management API

**Version**: 1.0.0
**Date**: 2026-02-20
**Spec Version**: 1.0.0
**Plan Version**: 1.0.0
**TDD Policy**: Tests MUST be written and confirmed FAILING before any implementation begins. Every implementation phase is preceded by a test-writing sub-phase.

---

## Phase 1: Setup (Shared Infrastructure)

**Purpose**: Project initialization, tooling, containerization, and directory scaffolding. No implementation code — infrastructure only.

- [ ] T001 Create full project directory structure per plan (outputs/src/, outputs/src/core/, outputs/src/models/, outputs/src/schemas/, outputs/src/repositories/, outputs/src/services/, outputs/src/routes/, outputs/src/utils/, tests/unit/core/, tests/unit/services/, tests/unit/repositories/, tests/integration/, tests/factories/, alembic/versions/, all `__init__.py` stubs)
- [ ] T002 Initialize pyproject.toml with all runtime dependencies (fastapi, uvicorn, sqlalchemy[asyncio], asyncpg, alembic, pydantic, pydantic-settings, pyjwt, passlib[bcrypt], redis[asyncio], structlog, prometheus-fastapi-instrumentator) and dev dependencies (pytest, pytest-asyncio, pytest-cov, httpx, factory-boy, black, ruff) per Appendix A of the plan
- [ ] T003 [P] Create Dockerfile with multi-stage build (builder stage installs deps from pyproject.toml; runtime stage copies venv and runs uvicorn on port 8000)
- [ ] T004 [P] Create docker-compose.yml with three services: app (build from Dockerfile, env_file .env), postgres (postgres:15-alpine, volume for data), redis (redis:7-alpine)
- [ ] T005 [P] Create .env.example with all required and optional variables per Appendix B (DATABASE_URL, REDIS_URL, JWT_SECRET_KEY, JWT_ALGORITHM, ACCESS_TOKEN_EXPIRE_MINUTES, REFRESH_TOKEN_EXPIRE_DAYS, EMAIL_BACKEND, SMTP_*, APP_ENV, CORS_ORIGINS, JWT_SECRET_KEY_PREV, ENABLE_RATE_LIMITING, ENABLE_METRICS)
- [ ] T006 [P] Configure .pre-commit-config.yaml with black (line-length 88) and ruff (E, F, I rules) hooks targeting outputs/src/ and tests/
- [ ] T007 Initialize Alembic and configure alembic/env.py for async SQLAlchemy engine (use `run_async_migrations()` pattern with `AsyncEngine`, import all models before autogenerate)
- [ ] T008 [P] Create alembic.ini with script_location=alembic, sqlalchemy.url placeholder, and file_template for sequential migration naming

---

## Phase 2: Foundational (Blocking Prerequisites)

**Purpose**: Core ORM models, infrastructure modules, base repository, Alembic migration, and test fixtures that every user story depends on.

⚠️ **CRITICAL**: No user story work can begin until this phase is complete.

### 2A — Write Failing Tests First (TDD gate — confirm RED before proceeding to 2B)

- [ ] T009 Write failing unit tests for outputs/src/core/security.py covering: `hash_password` produces bcrypt hash, `verify_password` returns True/False, `create_access_token` encodes user_id and email with correct expiry, `decode_access_token` raises `AuthenticationError` on expired/invalid token, `create_refresh_token` returns 64-char hex string, `hash_token` produces consistent SHA-256 hex digest — in tests/unit/core/test_security.py
- [ ] T010 [P] Write failing unit tests for outputs/src/utils/pagination.py covering: `PaginationParams` rejects page < 1, rejects limit > 100, computes correct SQL offset, `PagedResponse` calculates total pages correctly, edge cases (page=1/limit=1/total=0) — in tests/unit/core/test_pagination.py
- [ ] T011 Write failing unit tests for outputs/src/repositories/base.py covering: `get_by_id` returns model or None, `create` persists and returns instance, `update` applies partial changes, `delete` removes record, `list` returns paginated slice — in tests/unit/repositories/test_base_repository.py

### 2B — ORM Models

- [ ] T012 Implement outputs/src/models/base.py (`Base` declarative base, `TimestampMixin` with `created_at`/`updated_at` using `server_default=func.now()` and `onupdate=func.now()`, `UUIDPrimaryKeyMixin` with `id` defaulting to `uuid.uuid4`)
- [ ] T013 [P] Implement outputs/src/models/user.py (`User` ORM model: id, email VARCHAR(255) UNIQUE indexed lowercase-normalized, password_hash VARCHAR(255), full_name VARCHAR(200), is_active BOOLEAN DEFAULT False, failed_login_attempts INTEGER DEFAULT 0, locked_until TIMESTAMP nullable, email_verification_token VARCHAR(255) nullable, email_verification_expires_at TIMESTAMP nullable, created_at, updated_at; relationships to Task, Category, RefreshToken)
- [ ] T014 [P] Implement outputs/src/models/task.py (`StatusEnum` [pending, in_progress, completed], `PriorityEnum` [low, medium, high], `Task` ORM model: id, user_id FK indexed, title VARCHAR(200), description TEXT nullable, status ENUM NOT NULL DEFAULT pending, priority ENUM NOT NULL DEFAULT medium, due_date TIMESTAMP nullable, deleted_at TIMESTAMP nullable indexed, version INTEGER NOT NULL DEFAULT 1, created_at, updated_at; composite indexes on (user_id, deleted_at), (user_id, status), (user_id, priority), (user_id, due_date), (user_id, created_at); many-to-many relationship to Category via task_categories)
- [ ] T015 [P] Implement outputs/src/models/category.py (`Category` ORM model: id, user_id FK, name VARCHAR(50) NOT NULL, color VARCHAR(7) nullable; UniqueConstraint on (user_id, name); relationship to User and Task via task_categories)
- [ ] T016 [P] Implement outputs/src/models/task_category.py (association `Table` named `task_categories` with task_id UUID FK → tasks.id and category_id UUID FK → categories.id; composite PK (task_id, category_id))
- [ ] T017 [P] Implement outputs/src/models/refresh_token.py (`RefreshToken` ORM model: id UUID PK, user_id UUID FK indexed, token_hash VARCHAR(255) UNIQUE NOT NULL, expires_at TIMESTAMP NOT NULL, revoked_at TIMESTAMP nullable, created_at TIMESTAMP NOT NULL)

### 2C — Core Infrastructure

- [ ] T018 Implement outputs/src/core/exceptions.py (`AppException` base with status_code and detail, `NotFoundError` (404), `ForbiddenError` (403), `ConflictError` (409), `AuthenticationError` (401), `AccountLockedError` (403, includes locked_until field), `RateLimitError` (429), `ValidationError` (400))
- [ ] T019 [P] Implement outputs/src/core/config.py (`Settings(BaseSettings)` reading all env vars from Appendix B; field validators: DATABASE_URL must start with `postgresql+asyncpg://`, JWT_SECRET_KEY minimum 32 chars, ACCESS_TOKEN_EXPIRE_MINUTES 1–1440, REFRESH_TOKEN_EXPIRE_DAYS 1–30, EMAIL_BACKEND must be `console` or `smtp`; `lru_cache`-wrapped `get_settings()` factory)
- [ ] T020 Implement outputs/src/core/database.py (`create_async_engine` with pool_size=10, max_overflow=20; `AsyncSessionLocal` sessionmaker; `get_db` async generator yielding session with auto-close; `check_database_health()` async function running `SELECT 1`)
- [ ] T021 [P] Implement outputs/src/core/redis.py (module-level `ConnectionPool` from `REDIS_URL`; `get_redis` dependency yielding `redis.asyncio.Redis` client; `check_redis_health()` async function running `PING`; `close_redis_pool()` for lifespan teardown)
- [ ] T022 Implement outputs/src/core/security.py (`hash_password(plain)` via passlib bcrypt, `verify_password(plain, hashed)`, `create_access_token(user_id, email)` encoding sub+email+exp claims signed with JWT_SECRET_KEY, `decode_access_token(token)` raising `AuthenticationError` on PyJWT exceptions, `create_refresh_token()` returning `secrets.token_hex(32)`, `hash_token(raw)` returning `hashlib.sha256(raw).hexdigest()`)
- [ ] T023 [P] Implement outputs/src/core/logging.py (configure `structlog` with JSON renderer bound to ISO timestamp and log level; `RequestIDMiddleware` (Starlette `BaseHTTPMiddleware`) that reads or generates `X-Request-ID` UUID, binds it to structlog context, sets it on response header; `get_logger()` factory returning bound logger)

### 2D — Base Repository

- [ ] T024 Implement outputs/src/repositories/base.py (generic `AsyncRepository[ModelT]` accepting `AsyncSession`; methods: `get_by_id(id: UUID) → ModelT | None`, `create(obj_in: dict) → ModelT` using `session.add` + `flush` + `refresh`, `update(id: UUID, obj_in: dict) → ModelT`, `delete(id: UUID) → None`, `list(offset: int, limit: int) → tuple[list[ModelT], int]` using `select + func.count`)

### 2E — Shared Utilities

- [ ] T025 Implement outputs/src/utils/pagination.py (`PaginationParams` Pydantic model with `page: int = 1` (ge=1), `limit: int = 20` (ge=1, le=100), computed `offset` property; `PagedResponse[T]` generic Pydantic model with items, total, page, limit, pages (ceiling division); `paginate(query, session, params)` async helper returning `PagedResponse`)

### 2F — Database Migration

- [ ] T026 Create Alembic migration alembic/versions/0001_initial_schema.py implementing `upgrade()` to create all five tables (users, tasks, categories, task_categories, refresh_tokens) with exact column types, constraints, FKs, composite indexes, and PostgreSQL native ENUMs (status_enum, priority_enum); `downgrade()` drops all tables and enum types in reverse dependency order

### 2G — Test Infrastructure

- [ ] T027 Setup tests/conftest.py with: `event_loop` fixture (session scope), `test_engine` fixture creating async SQLAlchemy engine against test PostgreSQL DB with all tables created via `Base.metadata.create_all`, `db_session` fixture with per-test rollback, `async_client` fixture using `httpx.AsyncClient` against the FastAPI test app with `db_session` override for `get_db`, `mock_redis` fixture using `fakeredis.aioredis`, `authenticated_client(user)` fixture injecting valid JWT header, `test_user` factory fixture
- [ ] T028 [P] Create tests/factories/user_factory.py (`UserFactory(AsyncSQLAlchemyModelFactory)` with email as `Faker('email')`, full_name as `Faker('name')`, password_hash via `hash_password('TestPass1!')`, is_active=True, failed_login_attempts=0)
- [ ] T029 [P] Create tests/factories/task_factory.py (`TaskFactory` with title as `Faker('sentence', nb_words=4)`, status=StatusEnum.pending, priority=PriorityEnum.medium, version=1, user via SubFactory(UserFactory))
- [ ] T030 [P] Create tests/factories/category_factory.py (`CategoryFactory` with name as `Faker('word')` + random suffix for uniqueness, color='#6366F1', user via SubFactory(UserFactory))

### 2H — App Entry Point and Core Dependencies

- [ ] T031 Implement outputs/src/core/dependencies.py (`oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/v1/auth/login")`; `get_current_user(token: Annotated[str, Depends(oauth2_scheme)], db: AsyncSession = Depends(get_db)) → User` decoding token then fetching user from DB (with Redis cache-aside stub returning None in Phase 2); `require_active_user` dependency raising `ForbiddenError` if `user.is_active` is False)
- [ ] T032 Create outputs/src/main.py (FastAPI app factory `create_app()` with title, description, version, contact; `@asynccontextmanager lifespan` connecting Redis pool and logging startup; `app.add_middleware(RequestIDMiddleware)`; `app.add_middleware(CORSMiddleware, allow_origins=settings.CORS_ORIGINS)`; global exception handlers mapping each domain exception subclass to correct HTTPException with structured JSON detail; include routers placeholder for each route module)

> ✅ **Checkpoint**: Phase 2 foundation complete. All unit tests in T009–T011 must now pass. User story phases can begin — Auth track and Task track can run in parallel.

---

## Phase 3: User Story 1.1 — User Registration (Priority: P1) 🎯 MVP

**Purpose**: Allow new users to register with email + password + full name, receive JWT tokens, and trigger a verification email stub.

**Independent Test Criteria**:
- [ ] Can register a new user and receive `access_token` + `refresh_token` with `201` response
- [ ] Duplicate email returns `409 Conflict`
- [ ] Password without uppercase/digit/special char returns `400` with field-level errors
- [ ] Registered user has `is_active=false` until email verified
- [ ] Console email backend logs verification token to stdout (no SMTP dependency in tests)

### 3A — Write Failing Tests First

- [ ] T033 [US1.1] Write failing unit tests for `auth_service.register()` covering: happy path returns `TokenResponse` with user, duplicate email raises `ConflictError`, password complexity failure raises `ValidationError`, `email_service.send_verification_email` is called with correct token, user created with `is_active=False` — in tests/unit/services/test_auth_service.py
- [ ] T034 [US1.1] Write failing unit tests for `user_repository` covering: `get_by_email` returns User or None (case-insensitive lookup), `create` persists hashed password (not plain), `create` normalizes email to lowercase, `get_by_email` on non-existent returns None — in tests/unit/repositories/test_user_repository.py
- [ ] T035 [US1.1] Write failing integration tests for `POST /api/v1/auth/register` covering: `201` with valid body containing `access_token`/`refresh_token`/`user`, `409` on duplicate email, `400` on missing required fields, `400` on invalid email format, `400` on weak password — in tests/integration/test_auth_endpoints.py

### 3B — Implementation

- [ ] T036 [US1.1] Implement outputs/src/schemas/user.py (`UserCreate` with `EmailStr` validator + `@field_validator` for password (min 8 chars, ≥1 uppercase, ≥1 digit, ≥1 of `[!@#$%^&*]`) + `full_name` whitespace strip, `UserRead` excluding `password_hash` (model_config excludes field), `TokenResponse` with access_token/refresh_token/token_type/expires_in/user, `RefreshTokenRequest`, `LoginRequest`)
- [ ] T037 [US1.1] Implement outputs/src/repositories/user_repository.py (`UserRepository(AsyncRepository[User])` with `get_by_email(email: str) → User | None` using `ilike` for case-insensitive, `create(data: UserCreate) → User` hashing password and normalizing email, `update_verification_token(user_id, token, expires_at)`, `activate_user(user_id)`, `increment_failed_attempts(user_id)`, `lock_account(user_id, locked_until)`, `reset_login_failures(user_id)`)
- [ ] T038 [US1.1] Implement outputs/src/services/email_service.py (`EmailBackend` ABC with abstract `send_verification_email(to_email, full_name, token)` and `send_password_reset(to_email, token)`; `ConsoleEmailBackend` logging token URL to structlog; `SMTPEmailBackend` using `smtplib.SMTP` with settings from config; `get_email_service()` factory function selecting backend from `EMAIL_BACKEND` config)
- [ ] T039 [US1.1] Implement `auth_service.register()` in outputs/src/services/auth_service.py (`AuthService.__init__(user_repo, refresh_token_repo, email_service)`; `register(data: UserCreate) → TokenResponse`: check duplicate email via `user_repo.get_by_email` → `ConflictError`, create user, generate `secrets.token_urlsafe(32)` verification token with 24h expiry stored on user, call `email_service.send_verification_email`, create access token via `create_access_token`, create refresh token raw + store hash via `refresh_token_repo.create`, return `TokenResponse`)
- [ ] T040 [US1.1] Implement `POST /api/v1/auth/register` endpoint in outputs/src/routes/auth.py (`APIRouter(prefix="/api/v1/auth", tags=["auth"])`; inject `AuthService` via `Depends`; call `auth_service.register(data)`; return `status_code=201`; register router in main.py)

---

## Phase 4: User Story 1.2 — User Authentication (Priority: P1) 🎯 MVP

**Purpose**: Allow registered users to log in, track failed attempts with lockout, and rotate refresh tokens for extended sessions.

**Independent Test Criteria**:
- [ ] Valid credentials return `200` with `access_token` and `refresh_token`
- [ ] Wrong password increments `failed_login_attempts` counter
- [ ] 5th consecutive failure sets `locked_until = now() + 15min` and returns `403`
- [ ] Locked account returns `403` with `locked_until` in response body
- [ ] Refresh returns new token pair and old refresh token is rejected on second use
- [ ] Expired refresh token returns `401`

### 4A — Write Failing Tests First

- [ ] T041 [US1.2] Extend tests/unit/services/test_auth_service.py with failing tests for `login()`: success returns TokenResponse, wrong password raises `AuthenticationError`, 5th failure raises `AccountLockedError`, locked account bypasses credential check and raises `AccountLockedError`, success resets `failed_login_attempts`; and `refresh()`: valid rotation returns new pair, second use of rotated token raises `AuthenticationError`, expired token raises `AuthenticationError`
- [ ] T042 [US1.2] Extend tests/unit/repositories/test_user_repository.py with failing tests for `increment_failed_attempts()` (increments by 1 each call), `lock_account()` (sets locked_until correctly), `reset_login_failures()` (resets counter + clears locked_until)
- [ ] T043 [US1.2] Write failing unit tests for `refresh_token_repository` covering: `create(user_id, token_hash, expires_at)` persists record, `get_by_hash(hash)` returns token or None, `revoke(id)` sets `revoked_at = now()`, `get_by_hash` returns None for revoked token, `get_by_hash` returns None for expired token — in tests/unit/repositories/test_refresh_token_repository.py
- [ ] T044 [US1.2] Extend tests/integration/test_auth_endpoints.py with failing tests for `POST /api/v1/auth/login` (200 success, 401 wrong password, 403 locked account with locked_until in body, 429 rate limit after threshold) and `POST /api/v1/auth/refresh` (200 new token pair, 401 on revoked token, 401 on reuse of rotated token)

### 4B — Implementation

- [ ] T045 [US1.2] Implement outputs/src/repositories/refresh_token_repository.py (`RefreshTokenRepository(AsyncRepository[RefreshToken])` with `create(user_id, raw_token) → RefreshToken` storing SHA-256 hash + 7-day expiry; `get_by_hash(hash) → RefreshToken | None` with `where(not revoked, not expired)` filters; `revoke(token_id)` setting `revoked_at=now()`; `delete_expired_for_user(user_id)` cleanup)
- [ ] T046 [US1.2] Implement `auth_service.login()` in outputs/src/services/auth_service.py (`login(data: LoginRequest) → TokenResponse`: fetch user by email → `AuthenticationError` if not found; check `locked_until > now()` → `AccountLockedError` with locked_until; `verify_password` → on failure `increment_failed_attempts`; if attempts ≥ 5 `lock_account(now() + 15min)`; on success `reset_login_failures`; generate and return token pair)
- [ ] T047 [US1.2] Implement `auth_service.refresh()` in outputs/src/services/auth_service.py (`refresh(raw_token: str) → TokenResponse`: hash token → `get_by_hash` → `AuthenticationError` if not found/revoked/expired; revoke old token atomically in same session; create new refresh token; decode user_id from old token record; return new token pair)
- [ ] T048 [US1.2] Implement `POST /api/v1/auth/login` and `POST /api/v1/auth/refresh` endpoints in outputs/src/routes/auth.py (login returns 200 TokenResponse; refresh returns 200 TokenResponse; both endpoints have `RateLimitMiddleware` dependency at router level)
- [ ] T049 [US1.2] Implement outputs/src/routes/health.py (`GET /health` endpoint: run `check_database_health()` and `check_redis_health()` concurrently via `asyncio.gather`; return 200 `{"status": "healthy", "version": "1.0.0", "checks": {"database": "ok", "redis": "ok"}, "timestamp": "..."}` or 503 with `"status": "degraded"` naming the failing component; register router in main.py)

---

## Phase 5: User Story 2.1 — Create Task (Priority: P2)

**Purpose**: Allow authenticated users to create tasks with title, optional description, due date, and priority.

**Independent Test Criteria**:
- [ ] Authenticated user creates task and receives `201` with `TaskRead` including generated UUID
- [ ] Title shorter than 3 or longer than 200 characters returns `400`
- [ ] Due date in the past returns `400`
- [ ] Priority field defaults to `medium` when omitted
- [ ] `status` always defaults to `pending` regardless of request body
- [ ] Unauthenticated request returns `401`

### 5A — Write Failing Tests First

- [ ] T050 [US2.1] Write failing unit tests for `task_service.create_task()` covering: valid payload returns TaskRead with correct user_id, past due_date raises `ValidationError`, title boundary (2 chars fails, 3 passes, 200 passes, 201 fails), priority defaults to medium when omitted, status is always pending regardless of input — in tests/unit/services/test_task_service.py
- [ ] T051 [US2.1] Write failing unit tests for `task_repository.create()` covering: UUID auto-generated, user_id FK stored correctly, version initialized to 1, deleted_at is None on creation, created_at/updated_at auto-set — in tests/unit/repositories/test_task_repository.py
- [ ] T052 [US2.1] Write failing integration tests for `POST /api/v1/tasks` covering: `201` with valid JWT and body, response contains `id`/`categories`/`version`=1, `400` title too short, `400` past due_date, `401` missing JWT, `401` expired JWT — in tests/integration/test_task_endpoints.py

### 5B — Implementation

- [ ] T053 [US2.1] Implement outputs/src/schemas/task.py (`TaskCreate` with title (3–200 chars), optional description (max 2000 chars), optional due_date with `@field_validator` enforcing future datetime, priority defaulting to `medium`; `TaskRead` with categories: `list[CategoryRead]` embedded, version, all timestamps; `TaskUpdate` all optional fields; `TaskFilters` Pydantic model for query params (status, priority, due_date_from, due_date_to, sort_by, sort_order); `TaskListResponse(PagedResponse[TaskRead])`)
- [ ] T054 [US2.1] Implement `task_repository.create()` in outputs/src/repositories/task_repository.py (`TaskRepository(AsyncRepository[Task])` with `create(user_id: UUID, data: TaskCreate) → Task` persisting task; also stub signatures for all other methods to be implemented in later phases: `get_by_id_for_user`, `list_tasks`, `update`, `soft_delete`)
- [ ] T055 [US2.1] Implement `task_service.create_task()` in outputs/src/services/task_service.py (`TaskService.__init__(task_repo, category_repo)`; `create_task(user_id: UUID, data: TaskCreate) → TaskRead`: validate due_date > utcnow() if provided, call `task_repo.create`, return `TaskRead.model_validate(task)`)
- [ ] T056 [US2.1] Implement `POST /api/v1/tasks` endpoint in outputs/src/routes/tasks.py (`APIRouter(prefix="/api/v1/tasks", tags=["tasks"])`; require `current_user: User = Depends(get_current_user)`; call `task_service.create_task`; return `status_code=201`; register router in main.py)

---

## Phase 6: User Story 2.2 — List Tasks (Priority: P2)

**Purpose**: Allow authenticated users to retrieve paginated, filtered, and sorted views of their tasks.

**Independent Test Criteria**:
- [ ] Returns only tasks owned by the authenticated user (not other users' tasks)
- [ ] Soft-deleted tasks are excluded from all results
- [ ] Status filter applied independently and combined with priority filter
- [ ] Due date range filters (from/to) work with open-ended ranges
- [ ] Pagination default is page=1 limit=20; page=1 limit=1 on 3 tasks yields pages=3
- [ ] Sort by `priority` uses enum ordinal (high > medium > low) not alphabetical

### 6A — Write Failing Tests First

- [ ] T057 [US2.2] Extend tests/unit/services/test_task_service.py with failing tests for `list_tasks()`: no filters returns own tasks only, status filter excludes non-matching, priority filter works, combined filters intersect correctly, soft-deleted tasks excluded, pagination metadata (total/pages) correct, sort_by=priority uses correct ordering
- [ ] T058 [US2.2] Extend tests/unit/repositories/test_task_repository.py with failing tests for `list_tasks()`: user isolation confirmed, all filter combinations, due_date_from/due_date_to open-ended ranges, sort_by each allowed column, sort_order asc/desc, page/limit offset calculation, returns (items, total_count) tuple
- [ ] T059 [US2.2] Extend tests/integration/test_task_endpoints.py with failing tests for `GET /api/v1/tasks`: `200` with pagination envelope, filter by status returns subset, empty result returns `{"items":[], "total":0, "pages":0}`, limit=1 returns single item, `400` on limit > 100, `401` without JWT

### 6B — Implementation

- [ ] T060 [US2.2] Implement `task_repository.list_tasks()` in outputs/src/repositories/task_repository.py (single async SQLAlchemy `select(Task)` with: `where(Task.user_id == user_id, Task.deleted_at.is_(None))`; conditional `where` clauses for status/priority/due_date_from/due_date_to; `selectinload(Task.categories)` for N+1 prevention; `order_by` mapped to column + direction; `func.count()` subquery for total; returns `(list[Task], total: int)`)
- [ ] T061 [US2.2] Implement `task_service.list_tasks()` in outputs/src/services/task_service.py (`list_tasks(user_id, filters: TaskFilters, pagination: PaginationParams) → TaskListResponse`: delegate to `task_repo.list_tasks`, wrap results in `TaskListResponse` with computed pages)
- [ ] T062 [US2.2] Implement `GET /api/v1/tasks` endpoint in outputs/src/routes/tasks.py (inject `filters: TaskFilters = Depends()` and `pagination: PaginationParams = Depends()`; call `task_service.list_tasks`; return `200 TaskListResponse`)

---

## Phase 7: User Story 2.3 — Update Task (Priority: P2)

**Purpose**: Allow authenticated users to partially update their tasks with optimistic locking preventing concurrent overwrites.

**Independent Test Criteria**:
- [ ] Can update any subset of (title, description, due_date, priority, status) independently
- [ ] `id`, `user_id`, `created_at` are ignored even if included in request body
- [ ] `version` field in request must match current DB version or `409` is returned
- [ ] Successful update increments version by 1 and refreshes `updated_at`
- [ ] Task owned by another user returns `403`
- [ ] Non-existent task returns `404`

### 7A — Write Failing Tests First

- [ ] T063 [US2.3] Extend tests/unit/services/test_task_service.py with failing tests for `update_task()`: partial update (title only) persists only changed field, ownership check raises `ForbiddenError` for wrong user, stale version raises `ConflictError`, version increments on success, `updated_at` changes, past due_date raises `ValidationError`
- [ ] T064 [US2.3] Extend tests/unit/repositories/test_task_repository.py with failing tests for `update()`: WHERE version = expected_version condition, raises `ConflictError` when version mismatches, increments version to current+1, leaves unchanged fields intact
- [ ] T065 [US2.3] Extend tests/integration/test_task_endpoints.py with failing tests for `PATCH /api/v1/tasks/{task_id}`: `200` with updated fields and new version, `400` invalid field value, `403` accessing other user's task, `404` non-existent task, `409` stale version

### 7B — Implementation

- [ ] T066 [US2.3] Implement `task_repository.get_by_id_for_user()` and `task_repository.update()` in outputs/src/repositories/task_repository.py (`get_by_id_for_user(task_id, user_id) → Task | None`: select with `deleted_at.is_(None)` and `user_id` filter; `update(task_id, user_id, data: dict, expected_version: int) → Task`: execute `UPDATE tasks SET ... WHERE id=:id AND version=:ev`; check `rowcount == 0` → `ConflictError`; return refreshed Task)
- [ ] T067 [US2.3] Implement `task_service.update_task()` in outputs/src/services/task_service.py (`update_task(user_id, task_id, data: TaskUpdate) → TaskRead`: fetch task with `get_by_id_for_user` → `NotFoundError` if None; then check user_id equality → `ForbiddenError`; validate due_date if provided; extract non-None fields from data; call `task_repo.update` with `expected_version=data.version`)
- [ ] T068 [US2.3] Implement `PATCH /api/v1/tasks/{task_id}` endpoint in outputs/src/routes/tasks.py (inject `task_id: UUID`, `data: TaskUpdate`, `current_user`; call `task_service.update_task`; return `200 TaskRead`)

---

## Phase 8: User Story 2.4 — Delete Task (Priority: P2)

**Purpose**: Allow authenticated users to soft-delete tasks, preserving data while hiding from queries.

**Independent Test Criteria**:
- [ ] Soft delete sets `deleted_at = utcnow()` but does NOT remove the DB row
- [ ] Deleted task no longer appears in `GET /api/v1/tasks` list
- [ ] Deleted task returns `404` on `GET /api/v1/tasks/{id}`
- [ ] Returns `204 No Content` with empty body on success
- [ ] Attempting to delete another user's task returns `403`
- [ ] Already-deleted task returns `404` (not 204)

### 8A — Write Failing Tests First

- [ ] T069 [US2.4] Extend tests/unit/services/test_task_service.py with failing tests for `delete_task()`: sets deleted_at, ownership check raises `ForbiddenError`, calling delete on already-deleted raises `NotFoundError`, DB row still exists with deleted_at set
- [ ] T070 [US2.4] Extend tests/unit/repositories/test_task_repository.py with failing tests for `soft_delete()`: sets deleted_at, row remains in DB, subsequent `get_by_id_for_user` returns None, `list_tasks` excludes deleted rows
- [ ] T071 [US2.4] Extend tests/integration/test_task_endpoints.py with failing tests for `DELETE /api/v1/tasks/{task_id}`: `204` with empty body, task absent from subsequent `GET /api/v1/tasks`, `404` on second delete, `403` on other user's task, `401` without JWT

### 8B — Implementation

- [ ] T072 [US2.4] Implement `task_repository.soft_delete()` in outputs/src/repositories/task_repository.py (`soft_delete(task_id: UUID, user_id: UUID) → None`: execute `UPDATE tasks SET deleted_at=now() WHERE id=:id AND user_id=:uid AND deleted_at IS NULL`; check `rowcount == 0` and raise `NotFoundError`)
- [ ] T073 [US2.4] Implement `task_service.delete_task()` in outputs/src/services/task_service.py (`delete_task(user_id, task_id) → None`: fetch task with `get_by_id_for_user` → `NotFoundError`; ownership check → `ForbiddenError`; call `task_repo.soft_delete`)
- [ ] T074 [US2.4] Implement `DELETE /api/v1/tasks/{task_id}` endpoint in outputs/src/routes/tasks.py (call `task_service.delete_task`; return `Response(status_code=204)` with no body)
- [ ] T075 [US2.4] Implement `GET /api/v1/tasks/{task_id}` endpoint in outputs/src/routes/tasks.py (call `task_service.get_task(user_id, task_id)` → `NotFoundError` or `ForbiddenError`; return `200 TaskRead`)

---

## Phase 9: User Story 3.1 — Create Category (Priority: P3)

**Purpose**: Allow authenticated users to create, list, and delete named categories with optional hex color codes.

**Independent Test Criteria**:
- [ ] Can create category with valid name (3–50 chars) and receive `201 CategoryRead`
- [ ] Duplicate name for same user returns `409`; different user with same name succeeds
- [ ] Hex color regex validates `#RRGGBB` format; invalid format returns `400`
- [ ] Omitting color uses default `#6366F1`
- [ ] `GET /api/v1/categories` returns all categories for authenticated user only
- [ ] `DELETE /api/v1/categories/{id}` returns `204` and cascades removal from task_categories

### 9A — Write Failing Tests First

- [ ] T076 [US3.1] Write failing unit tests for `category_service`: `create_category` happy path, duplicate name same user raises `ConflictError`, duplicate name different user succeeds, `list_categories` returns only own categories, `delete_category` ownership check, cascading test verifying task_categories rows removed — in tests/unit/services/test_category_service.py
- [ ] T077 [US3.1] Write failing unit tests for `category_repository`: `create` persists with default color, `get_by_name_for_user` case-sensitive lookup, `list_for_user` returns all categories sorted by name, `delete` removes record — in tests/unit/repositories/test_category_repository.py
- [ ] T078 [US3.1] Write failing integration tests for category endpoints: `POST /api/v1/categories` (201, 409 duplicate, 400 invalid color, 400 name too short), `GET /api/v1/categories` (200 list only own), `DELETE /api/v1/categories/{id}` (204, 403, 404) — in tests/integration/test_category_endpoints.py

### 9B — Implementation

- [ ] T079 [US3.1] Implement outputs/src/schemas/category.py (`CategoryCreate` with name (min_length=3, max_length=50) and optional color with `@field_validator` enforcing `^#[0-9A-Fa-f]{6}$` regex, defaulting to `#6366F1`; `CategoryRead` with id/name/color/created_at; `CategoryListResponse` with items and total)
- [ ] T080 [US3.1] Implement outputs/src/repositories/category_repository.py (`CategoryRepository(AsyncRepository[Category])` with `get_by_id_for_user(cat_id, user_id) → Category | None`, `get_by_name_for_user(name, user_id) → Category | None`, `list_for_user(user_id) → list[Category]` ordered by name, `create(user_id, data: CategoryCreate) → Category` applying default color, `delete(cat_id) → None`)
- [ ] T081 [US3.1] Implement `category_service.create_category()`, `list_categories()`, `delete_category()` in outputs/src/services/category_service.py (`CategoryService.__init__(category_repo, task_repo)`; create: unique name check → `ConflictError`; delete: ownership check → `ForbiddenError`)
- [ ] T082 [US3.1] Implement `GET /api/v1/categories`, `POST /api/v1/categories`, `DELETE /api/v1/categories/{cat_id}` endpoints in outputs/src/routes/categories.py (router prefix `/api/v1/categories`, tag `categories`; all require JWT; register in main.py)

---

## Phase 10: User Story 3.2 — Assign Category to Task (Priority: P3)

**Purpose**: Allow authenticated users to assign and remove categories on their tasks with ownership validation on both sides.

**Independent Test Criteria**:
- [ ] Can assign an owned category to an owned task; returns `200 TaskRead` with categories populated
- [ ] Assigning same category twice returns `409 Conflict`
- [ ] Assigning category owned by a different user returns `403`
- [ ] Assigning to a deleted task returns `404`
- [ ] Removing an assignment returns `204 No Content`
- [ ] Removing non-existent assignment returns `404`

### 10A — Write Failing Tests First

- [ ] T083 [US3.2] Extend tests/unit/services/test_category_service.py with failing tests for `assign_category()`: happy path inserts into task_categories and returns TaskRead with category, duplicate assignment raises `ConflictError`, category from other user raises `ForbiddenError`, task from other user raises `ForbiddenError`, task not found raises `NotFoundError`; and `remove_category()`: success removes row, non-existent assignment raises `NotFoundError`
- [ ] T084 [US3.2] Extend tests/integration/test_category_endpoints.py with failing tests for `POST /api/v1/tasks/{task_id}/categories/{cat_id}` (200 with categories in response, 403 cross-user, 404 missing task or category, 409 duplicate) and `DELETE /api/v1/tasks/{task_id}/categories/{cat_id}` (204, 404 not assigned)

### 10B — Implementation

- [ ] T085 [US3.2] Implement `category_service.assign_category()` and `category_service.remove_category()` in outputs/src/services/category_service.py (`assign_category(task_id, cat_id, user_id) → TaskRead`: fetch task with `get_by_id_for_user` → `NotFoundError`; fetch category with `get_by_id_for_user` → `NotFoundError`; ownership checks on both → `ForbiddenError`; check not already assigned → `ConflictError`; insert into task_categories; reload task with `selectinload(categories)`; return `TaskRead`; `remove_category`: validate ownership, check assignment exists → `NotFoundError`, delete junction row)
- [ ] T086 [US3.2] Implement `POST /api/v1/tasks/{task_id}/categories/{cat_id}` and `DELETE /api/v1/tasks/{task_id}/categories/{cat_id}` endpoints in outputs/src/routes/tasks.py (inject both UUIDs and current_user; call service methods; return 200 TaskRead or 204 Response respectively)

---

## Phase 11: Cross-Cutting Concerns & Polish

**Purpose**: Rate limiting, full observability stack, security hardening, performance optimization, API documentation, and final quality gate.

### 11A — Rate Limiting

- [ ] T087 Write failing unit tests for `utils/rate_limiter.py` covering: first request within window is allowed, 100th per-user request is allowed, 101st raises `RateLimitError`, window expiry resets counter, per-IP anonymous limit is 20, authenticated requests use user_id key not IP — in tests/unit/core/test_rate_limiter.py
- [ ] T088 Implement outputs/src/utils/rate_limiter.py (Redis Lua script using `ZADD`/`ZCOUNT`/`ZREMRANGEBYSCORE` for atomic sliding-window; `SlidingWindowRateLimiter.is_allowed(key, limit, window_seconds) → bool`; `RateLimitMiddleware(BaseHTTPMiddleware)` extracting user_id from JWT header if present else client IP; raising `RateLimitError` with `Retry-After` header; fails open with logged warning if Redis unavailable)
- [ ] T089 Register `RateLimitMiddleware` in outputs/src/main.py (add middleware before CORS; configure per-user limit=100/window=60 and per-IP limit=20/window=60 from settings; guard with `ENABLE_RATE_LIMITING` feature flag)

### 11B — Observability

- [ ] T090 [P] Extend outputs/src/core/logging.py with `RequestLoggingMiddleware` that logs a structured JSON entry per request containing: `request_id`, `method`, `path`, `status_code`, `duration_ms` (via `time.perf_counter`), `user_id` (if authenticated); ensure log entry emitted in `finally` block to capture error responses
- [ ] T091 [P] Configure `prometheus-fastapi-instrumentator` in outputs/src/main.py (instrument app in lifespan, expose `/metrics` endpoint, add custom counter for `auth_failures_total` and `rate_limit_rejections_total`; guard with `ENABLE_METRICS` feature flag)
- [ ] T092 [P] Register `RequestLoggingMiddleware` in outputs/src/main.py after RequestIDMiddleware (ensure request_id is already bound to context when logging fires)

### 11C — Performance Optimization

- [ ] T093 [P] Audit all task query methods in outputs/src/repositories/task_repository.py and confirm `selectinload(Task.categories)` is used in every method returning `TaskRead`-destined objects (`get_by_id_for_user`, `list_tasks`, `update` return path); add missing selectinload calls
- [ ] T094 [P] Implement Redis cache-aside for `get_current_user` in outputs/src/core/dependencies.py (after JWT decode, check `redis.get(f"user:{user_id}")` → deserialize if hit; on miss fetch from DB, serialize with `json.dumps`, `redis.setex(key, 900, value)`; invalidate cache key in `user_repository.py` on any user update)
- [ ] T095 [P] Verify all seven composite indexes in Alembic migration match actual `task_repository.list_tasks()` filter/sort columns; add any missing index definitions to alembic/versions/0001_initial_schema.py and generate corrective migration if needed

### 11D — Security Hardening

- [ ] T096 [P] Audit all Pydantic response schemas in outputs/src/schemas/user.py and outputs/src/schemas/task.py to confirm `password_hash` is excluded via `model_config = ConfigDict(populate_by_name=True)` and explicit `exclude` set; add integration test asserting `password_hash` is absent from any auth API response
- [ ] T097 [P] Configure `CORSMiddleware` in outputs/src/main.py to read `CORS_ORIGINS` from settings (comma-split to list); in `production` mode allow only explicit origins, in `development` mode allow `["http://localhost:3000", "http://localhost:8000"]`
- [ ] T098 [P] Add `SecurityHeadersMiddleware` to outputs/src/main.py (active only when `APP_ENV=production`): set `Strict-Transport-Security: max-age=63072000; includeSubDomains`, `X-Content-Type-Options: nosniff`, `X-Frame-Options: DENY`, `Referrer-Policy: strict-origin-when-cross-origin`

### 11E — API Documentation

- [ ] T099 [P] Add `model_config = ConfigDict(json_schema_extra={"example": {...}})` with realistic example data to all Pydantic schemas in outputs/src/schemas/ (UserCreate, UserRead, TokenResponse, TaskCreate, TaskRead, TaskUpdate, CategoryCreate, CategoryRead); ensure examples appear correctly in Swagger UI
- [ ] T100 [P] Update `create_app()` in outputs/src/main.py with full FastAPI metadata: `title="Task Management API"`, `description` with markdown overview, `version="1.0.0"`, `contact={"name": "Dev Team", "email": "dev@example.com"}`, `openapi_tags` list with descriptions for auth/tasks/categories/health tag groups
- [ ] T101 [P] Add `summary`, `description`, and `response_description` to all route function docstrings in outputs/src/routes/*.py for rich Swagger UI display; add `responses` dict to each endpoint decorator for non-200 status code documentation

### 11F — Integration Test Completion

- [ ] T102 Write integration tests for `GET /health` in tests/integration/test_health_endpoint.py: `200` with correct schema when DB and Redis up, `503` with `"status": "degraded"` and `"checks": {"database": "ok", "redis": "error"}` when Redis is unavailable (use mock to simulate Redis failure), response body has `timestamp` in ISO 8601 format
- [ ] T103 [P] Write end-to-end scenario integration test in tests/integration/test_e2e_workflow.py covering full user journey: register → login → create task (no category) → create category → assign category → list tasks (verify category in response) → update task status → get task (verify status) → delete task → list tasks (verify absent) → delete category

### 11G — Final Quality Gate

- [ ] T104 Run full pytest suite with coverage reporting (`pytest --cov=outputs/src --cov-report=term-missing --cov-fail-under=80`) and resolve any failures; if coverage < 80% identify uncovered branches and add targeted unit tests
- [ ] T105 [P] Run `ruff check outputs/src/ tests/ --fix` and `black outputs/src/ tests/ --check`; fix all remaining linting and formatting violations; ensure CI would pass
- [ ] T106 [P] Final review of alembic/versions/0001_initial_schema.py: confirm PostgreSQL native enum types created with `create_type=True`, all NOT NULL constraints match models, all FKs have `ondelete` clauses, indexes match query access patterns; run `alembic upgrade head` against test DB to confirm no migration errors

---

## Dependency & Execution Order

### Phase Dependency Graph

```
Phase 1 (Setup: T001–T008)
    └── Phase 2 (Foundation: T009–T032)
            ├── [Auth Track]
            │       Phase 3 (US-1.1 Registration: T033–T040)
            │           └── Phase 4 (US-1.2 Authentication: T041–T049)
            │
            ├── [Task Track]
            │       Phase 5 (US-2.1 Create: T050–T056)
            │           ├── Phase 6 (US-2.2 List: T057–T062)
            │           ├── Phase 7 (US-2.3 Update: T063–T068)
            │           └── Phase 8 (US-2.4 Delete: T069–T075)
            │
            └── [Category Track]
                    Phase 9 (US-3.1 Categories: T076–T082)
                        └── Phase 10 (US-3.2 Assignment: T083–T086)
                            [also requires Phase 5 task_repository complete]
                                └── Phase 11 (Polish: T087–T106)
```

### Parallel Opportunities

After **Phase 2** completes, the Auth Track, Task Track, and Category Track (Phases 3–10) can execute on separate branches simultaneously. Within each phase, tasks marked **[P]** have no shared file dependencies and can run concurrently.

### TDD Enforcement Flow (Per Phase)

```
Write failing tests (TDD gate) → Confirm RED (all new tests fail)
    → Implement code
        → Confirm GREEN (all tests pass)
            → Refactor (keep GREEN)
                → Next phase
```

---

## Task Count Summary

| Metric | Count |
|--------|-------|
| **Total tasks** | **106** |
| **Tasks marked [P] (parallelizable)** | **32** |
| **Test-writing tasks (TDD gates)** | **30** |
| **Test infrastructure tasks (conftest, factories)** | **4** |
| **Implementation tasks** | **52** |
| **Setup / infra tasks** | **20** |

### Tasks per User Story

| User Story | Test Tasks | Impl Tasks | Total |
|------------|------------|------------|-------|
| US-1.1 User Registration | 3 | 5 | **8** |
| US-1.2 User Authentication | 4 | 5 | **9** |
| US-2.1 Create Task | 3 | 4 | **7** |
| US-2.2 List Tasks | 3 | 3 | **6** |
| US-2.3 Update Task | 3 | 3 | **6** |
| US-2.4 Delete Task | 3 | 4 | **7** |
| US-3.1 Create Category | 3 | 4 | **7** |
| US-3.2 Assign Category | 2 | 2 | **4** |
| Foundation + Setup | 7 | 25 | **32** |
| Polish + Cross-cutting | 3 | 17 | **20** |

### MVP Scope

**Minimum Viable Product** = Phases 1–5 (US-1.1 + US-1.2 + US-2.1):
Tasks **T001–T056** (56 tasks) deliver: user registration, login, token refresh, and task creation — a working, authenticated, tested REST API.