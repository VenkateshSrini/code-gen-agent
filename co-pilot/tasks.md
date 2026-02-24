---
description: "Task list template for feature implementation"
---

# Tasks: Task Management API

**Input**: Design documents from `/specs/001-task-management-api/`  
**Prerequisites**: plan.md (required), spec.md (required for user stories), research.md, data-model.md, contracts/

**Tests**: Required — TDD mandated by constitution and spec.  
**Organization**: Tasks are grouped by user story to enable independent implementation and testing of each story.

## Format: `[ID] [P?] [Story] Description`

- **[P]**: Can run in parallel (different files, no dependencies)
- **[Story]**: Which user story this task belongs to (e.g., US1.1, US2.2)
- Include exact file paths in descriptions

## Path Conventions

- **Single project**: `src/`, `tests/` at repository root  
- Paths shown below follow the plan.md structure for a single FastAPI service

---

## Phase 1: Setup (Shared Infrastructure)

**Purpose**: Project initialization and basic structure

- [ ] T001 Create base directory structure in `src/`, `tests/`, and `specs/001-task-management-api/contracts/`
- [ ] T002 Initialize Python project dependencies in `pyproject.toml`
- [ ] T003 [P] Configure Ruff linting in `ruff.toml`
- [ ] T004 [P] Configure mypy type checking in `mypy.ini`
- [ ] T005 [P] Add environment template in `.env.example`
- [ ] T006 [P] Create API container build file in `Dockerfile`
- [ ] T007 [P] Create local dev stack in `docker-compose.yml`

---

## Phase 2: Foundational (Blocking Prerequisites)

**Purpose**: Core infrastructure that MUST be complete before ANY user story can be implemented

**⚠️ CRITICAL**: No user story work can begin until this phase is complete

- [ ] T008 Create SQLAlchemy base model in `src/db/base.py`
- [ ] T009 Create async DB session/engine in `src/db/session.py`
- [ ] T010 Configure Alembic in `alembic.ini`
- [ ] T011 Configure Alembic env in `src/db/migrations/env.py`
- [ ] T012 Create initial migration with tables/indexes in `src/db/migrations/versions/0001_initial.py`
- [ ] T013 [P] Implement settings loader in `src/core/config.py`
- [ ] T014 [P] Implement structured logging + correlation IDs in `src/core/logging.py`
- [ ] T015 [P] Implement security utilities (bcrypt, JWT, token hashing) in `src/core/security.py`
- [ ] T016 [P] Implement Redis cache client in `src/core/cache.py`
- [ ] T017 [P] Implement rate limiter utilities in `src/core/rate_limit.py`
- [ ] T018 [P] Implement pagination helpers in `src/utils/pagination.py`
- [ ] T019 [P] Implement UUID helpers in `src/utils/uuid.py`
- [ ] T020 [P] Implement time helpers in `src/utils/time.py`
- [ ] T021 [P] Define error response schemas in `src/schemas/error.py`
- [ ] T022 [P] Create User model in `src/models/user.py`
- [ ] T023 [P] Create Task model in `src/models/task.py`
- [ ] T024 [P] Create Category model in `src/models/category.py`
- [ ] T025 [P] Create TaskCategory model in `src/models/task_category.py`
- [ ] T026 [P] Create RefreshToken model in `src/models/refresh_token.py`
- [ ] T027 [P] Create EmailVerificationToken model in `src/models/email_verification_token.py`
- [ ] T028 [P] Export models in `src/models/__init__.py`
- [ ] T029 [P] Create repository base class in `src/repositories/base.py`
- [ ] T030 [P] Create user repository skeleton in `src/repositories/user_repo.py`
- [ ] T031 [P] Create task repository skeleton in `src/repositories/task_repo.py`
- [ ] T032 [P] Create category repository skeleton in `src/repositories/category_repo.py`
- [ ] T033 [P] Create token repository skeleton in `src/repositories/token_repo.py`
- [ ] T034 [P] Implement API dependencies (DB session, current user) in `src/api/dependencies.py`
- [ ] T035 Create FastAPI app and middleware wiring in `src/main.py`
- [ ] T036 [P] Create auth route module skeleton in `src/api/v1/auth_routes.py`
- [ ] T037 [P] Create task route module skeleton in `src/api/v1/task_routes.py`
- [ ] T038 [P] Create category route module skeleton in `src/api/v1/category_routes.py`
- [ ] T039 [P] Implement health endpoint in `src/api/v1/health_routes.py`
- [ ] T040 Implement exception handlers in `src/api/error_handlers.py`

**Checkpoint**: Foundation ready — user story implementation can now begin in parallel

---

## Phase 3: User Story 1.1 - User Registration (Priority: P1) 🎯 MVP

**Goal**: Register new users with email verification token issuance and JWT response  
**Independent Test**: Registering with valid data returns tokens, creates inactive user, and logs email send

### Tests for User Story 1.1 (REQUIRED - TDD)

- [ ] T041 [P] [US1.1] Contract test for `POST /api/v1/auth/register` in `tests/contract/test_auth_register_contract.py`
- [ ] T042 [P] [US1.1] Integration test for registration flow in `tests/integration/test_auth_register_flow.py`
- [ ] T043 [P] [US1.1] Unit test for AuthService.register in `tests/unit/services/test_auth_service_register.py`

### Implementation for User Story 1.1

- [ ] T044 [US1.1] Add registration request/response schemas in `src/schemas/auth.py`
- [ ] T045 [US1.1] Add token response schema for registration in `src/schemas/token.py`
- [ ] T046 [US1.1] Implement email verification sender stub in `src/services/email_service.py`
- [ ] T047 [US1.1] Implement user creation + uniqueness checks in `src/repositories/user_repo.py`
- [ ] T048 [US1.1] Implement verification token persistence in `src/repositories/token_repo.py`
- [ ] T049 [US1.1] Implement AuthService.register in `src/services/auth_service.py`
- [ ] T050 [US1.1] Implement `POST /auth/register` endpoint in `src/api/v1/auth_routes.py`
- [ ] T051 [US1.1] Map registration errors to HTTP responses in `src/api/error_handlers.py`

**Checkpoint**: User registration is fully functional and testable independently

---

## Phase 4: User Story 1.2 - User Authentication (Priority: P1)

**Goal**: Authenticate users with JWT access + refresh tokens, lockout, and rate limiting  
**Independent Test**: Valid login returns tokens; repeated failures trigger lockout; refresh rotates tokens

### Tests for User Story 1.2 (REQUIRED - TDD)

- [ ] T052 [P] [US1.2] Contract test for `POST /api/v1/auth/login` in `tests/contract/test_auth_login_contract.py`
- [ ] T053 [P] [US1.2] Contract test for `POST /api/v1/auth/refresh` in `tests/contract/test_auth_refresh_contract.py`
- [ ] T054 [P] [US1.2] Integration test for login flow + lockout in `tests/integration/test_auth_login_flow.py`
- [ ] T055 [P] [US1.2] Integration test for refresh rotation in `tests/integration/test_auth_refresh_flow.py`
- [ ] T056 [P] [US1.2] Unit test for AuthService.login/refresh in `tests/unit/services/test_auth_service_login.py`

### Implementation for User Story 1.2

- [ ] T057 [US1.2] Add login/refresh schemas in `src/schemas/auth.py`
- [ ] T058 [US1.2] Implement refresh token CRUD + rotation in `src/repositories/token_repo.py`
- [ ] T059 [US1.2] Implement login attempt tracking/lockout in `src/core/rate_limit.py`
- [ ] T060 [US1.2] Implement AuthService.login/refresh in `src/services/auth_service.py`
- [ ] T061 [US1.2] Implement `POST /auth/login` endpoint in `src/api/v1/auth_routes.py`
- [ ] T062 [US1.2] Implement `POST /auth/refresh` endpoint in `src/api/v1/auth_routes.py`
- [ ] T063 [US1.2] Implement JWT auth dependency in `src/api/dependencies.py`

**Checkpoint**: Authentication and refresh flows are fully functional and testable independently

---

## Phase 5: User Story 2.1 - Create Task (Priority: P2)

**Goal**: Create tasks with validation, defaults, and user ownership  
**Independent Test**: Authenticated user can create task; due_date validation enforced

### Tests for User Story 2.1 (REQUIRED - TDD)

- [ ] T064 [P] [US2.1] Contract test for `POST /api/v1/tasks` in `tests/contract/test_tasks_create_contract.py`
- [ ] T065 [P] [US2.1] Integration test for task creation in `tests/integration/test_tasks_create.py`
- [ ] T066 [P] [US2.1] Unit test for TaskService.create in `tests/unit/services/test_task_service_create.py`

### Implementation for User Story 2.1

- [ ] T067 [US2.1] Add create-task schemas in `src/schemas/task.py`
- [ ] T068 [US2.1] Implement task creation in `src/repositories/task_repo.py`
- [ ] T069 [US2.1] Implement TaskService.create in `src/services/task_service.py`
- [ ] T070 [US2.1] Implement `POST /tasks` endpoint in `src/api/v1/task_routes.py`
- [ ] T071 [US2.1] Add create-task validation rules in `src/schemas/task.py`

**Checkpoint**: Task creation is fully functional and testable independently

---

## Phase 6: User Story 2.2 - List Tasks (Priority: P2)

**Goal**: List user tasks with filtering, sorting, and pagination  
**Independent Test**: Authenticated user can filter by status/priority/dates and paginate results

### Tests for User Story 2.2 (REQUIRED - TDD)

- [ ] T072 [P] [US2.2] Contract test for `GET /api/v1/tasks` in `tests/contract/test_tasks_list_contract.py`
- [ ] T073 [P] [US2.2] Integration test for list/filter/pagination in `tests/integration/test_tasks_list.py`
- [ ] T074 [P] [US2.2] Unit test for TaskRepository.list filters in `tests/unit/repositories/test_task_repo_list.py`

### Implementation for User Story 2.2

- [ ] T075 [US2.2] Add list query/response schemas in `src/schemas/task.py`
- [ ] T076 [US2.2] Implement filtered list query in `src/repositories/task_repo.py`
- [ ] T077 [US2.2] Implement TaskService.list in `src/services/task_service.py`
- [ ] T078 [US2.2] Implement `GET /tasks` endpoint in `src/api/v1/task_routes.py`

**Checkpoint**: Task listing is fully functional and testable independently

---

## Phase 7: User Story 2.3 - Update Task (Priority: P2)

**Goal**: Update task fields with optimistic locking and ownership checks  
**Independent Test**: Valid PATCH updates task; incorrect version yields 409; non-owner yields 403

### Tests for User Story 2.3 (REQUIRED - TDD)

- [ ] T079 [P] [US2.3] Contract test for `PATCH /api/v1/tasks/{task_id}` in `tests/contract/test_tasks_update_contract.py`
- [ ] T080 [P] [US2.3] Integration test for update + optimistic locking in `tests/integration/test_tasks_update.py`
- [ ] T081 [P] [US2.3] Unit test for TaskService.update in `tests/unit/services/test_task_service_update.py`

### Implementation for User Story 2.3

- [ ] T082 [US2.3] Add update-task schema with version in `src/schemas/task.py`
- [ ] T083 [US2.3] Implement optimistic locking update in `src/repositories/task_repo.py`
- [ ] T084 [US2.3] Implement TaskService.update in `src/services/task_service.py`
- [ ] T085 [US2.3] Implement `PATCH /tasks/{task_id}` endpoint in `src/api/v1/task_routes.py`

**Checkpoint**: Task updates are fully functional and testable independently

---

## Phase 8: User Story 2.4 - Delete Task (Priority: P2)

**Goal**: Soft delete tasks with ownership checks  
**Independent Test**: Delete sets deleted_at and excludes from list; non-owner yields 403

### Tests for User Story 2.4 (REQUIRED - TDD)

- [ ] T086 [P] [US2.4] Contract test for `DELETE /api/v1/tasks/{task_id}` in `tests/contract/test_tasks_delete_contract.py`
- [ ] T087 [P] [US2.4] Integration test for soft delete in `tests/integration/test_tasks_delete.py`
- [ ] T088 [P] [US2.4] Unit test for TaskService.delete in `tests/unit/services/test_task_service_delete.py`

### Implementation for User Story 2.4

- [ ] T089 [US2.4] Implement soft delete in `src/repositories/task_repo.py`
- [ ] T090 [US2.4] Implement TaskService.delete in `src/services/task_service.py`
- [ ] T091 [US2.4] Implement `DELETE /tasks/{task_id}` endpoint in `src/api/v1/task_routes.py`

**Checkpoint**: Task deletion is fully functional and testable independently

---

## Phase 9: User Story 3.1 - Create Category (Priority: P3)

**Goal**: Create, list, and delete categories with per-user uniqueness  
**Independent Test**: User can CRUD categories; duplicate name per user returns 409

### Tests for User Story 3.1 (REQUIRED - TDD)

- [ ] T092 [P] [US3.1] Contract test for `POST /api/v1/categories` in `tests/contract/test_categories_create_contract.py`
- [ ] T093 [P] [US3.1] Contract test for `GET /api/v1/categories` in `tests/contract/test_categories_list_contract.py`
- [ ] T094 [P] [US3.1] Contract test for `DELETE /api/v1/categories/{cat_id}` in `tests/contract/test_categories_delete_contract.py`
- [ ] T095 [P] [US3.1] Integration test for category CRUD in `tests/integration/test_categories_flow.py`
- [ ] T096 [P] [US3.1] Unit test for CategoryService in `tests/unit/services/test_category_service.py`

### Implementation for User Story 3.1

- [ ] T097 [US3.1] Add category schemas in `src/schemas/category.py`
- [ ] T098 [US3.1] Implement category repo create/list/delete in `src/repositories/category_repo.py`
- [ ] T099 [US3.1] Implement CategoryService in `src/services/category_service.py`
- [ ] T100 [US3.1] Implement category endpoints in `src/api/v1/category_routes.py`
- [ ] T101 [US3.1] Add category validation rules in `src/schemas/category.py`

**Checkpoint**: Category management is fully functional and testable independently

---

## Phase 10: User Story 3.2 - Assign Category to Task (Priority: P3)

**Goal**: Assign and remove categories on tasks with ownership validation  
**Independent Test**: Assigning valid category updates task; duplicates return 409; removal works

### Tests for User Story 3.2 (REQUIRED - TDD)

- [ ] T102 [P] [US3.2] Contract test for `POST /api/v1/tasks/{task_id}/categories/{cat_id}` in `tests/contract/test_task_category_assign_contract.py`
- [ ] T103 [P] [US3.2] Contract test for `DELETE /api/v1/tasks/{task_id}/categories/{cat_id}` in `tests/contract/test_task_category_remove_contract.py`
- [ ] T104 [P] [US3.2] Integration test for category assignment flow in `tests/integration/test_task_category_flow.py`
- [ ] T105 [P] [US3.2] Unit test for task-category service in `tests/unit/services/test_task_category_service.py`

### Implementation for User Story 3.2

- [ ] T106 [US3.2] Implement task-category join operations in `src/repositories/task_repo.py`
- [ ] T107 [US3.2] Implement TaskService.assign/remove category in `src/services/task_service.py`
- [ ] T108 [US3.2] Implement assign/remove endpoints in `src/api/v1/task_routes.py`
- [ ] T109 [US3.2] Extend task response schema with categories in `src/schemas/task.py`

**Checkpoint**: Task-category assignment is fully functional and testable independently

---

## Phase 11: Polish & Cross-Cutting Concerns

**Purpose**: Improvements that affect multiple user stories and non-functional requirements

- [ ] T110 Add OpenAPI metadata/tags/versioning in `src/main.py`
- [ ] T111 [P] Add request/response metrics logging in `src/core/logging.py`
- [ ] T112 [P] Implement metrics collector in `src/core/metrics.py`
- [ ] T113 Add metrics middleware wiring in `src/main.py`
- [ ] T114 Add cache-aside user lookup in `src/repositories/user_repo.py`
- [ ] T115 Add security-focused error responses and sanitization in `src/api/error_handlers.py`
- [ ] T116 Add coverage thresholds in `.coveragerc`
- [ ] T117 Add integration test for `/health` in `tests/integration/test_health.py`
- [ ] T118 Add load test scaffold in `tests/performance/test_load.py`
- [ ] T119 Update quickstart guide in `specs/001-task-management-api/quickstart.md`

---

## Dependencies & Execution Order

### Phase Dependencies

- **Setup (Phase 1)**: No dependencies — can start immediately
- **Foundational (Phase 2)**: Depends on Setup — BLOCKS all user stories
- **User Stories (Phase 3–10)**: All depend on Foundational completion  
  - Can run in parallel by different developers  
  - Or sequentially by priority (P1 → P2 → P3)
- **Polish (Phase 11)**: Depends on all desired user stories being complete

### User Story Dependencies

- **US1.1 (Registration)**: Depends only on Foundational phase  
- **US1.2 (Authentication)**: Depends only on Foundational phase  
- **US2.x (Tasks)**: Depends on Foundational phase and JWT auth dependency  
- **US3.x (Categories)**: Depends on Foundational phase and JWT auth dependency  

### Within Each User Story

- Tests MUST be written and FAIL before implementation
- Schemas/validation before services
- Services before endpoints
- Repository methods before service methods
- Story must pass tests before moving to next priority

### Parallel Opportunities

- All Setup tasks marked [P] can run in parallel
- All Foundational tasks marked [P] can run in parallel (within Phase 2)
- After Foundational, user stories can be worked on in parallel
- Tests for a story marked [P] can run in parallel
- Models and repositories within a story marked [P] can run in parallel

---

## Parallel Example: User Story 1.1

```bash
# Run tests for User Story 1.1 together:
Task: "Contract test for POST /api/v1/auth/register in tests/contract/test_auth_register_contract.py"
Task: "Integration test for registration flow in tests/integration/test_auth_register_flow.py"
Task: "Unit test for AuthService.register in tests/unit/services/test_auth_service_register.py"
```

---

## Implementation Strategy

### MVP First (User Story 1.1 Only)

1. Complete Phase 1: Setup  
2. Complete Phase 2: Foundational (CRITICAL — blocks all stories)  
3. Complete Phase 3: User Story 1.1  
4. **Validate**: All US1.1 tests pass  
5. Deploy/demo registration flow  

### Incremental Delivery

1. Setup + Foundational → Foundation ready  
2. Add US1.1 → Test independently → Deploy/Demo  
3. Add US1.2 → Test independently → Deploy/Demo  
4. Add US2.x → Test independently → Deploy/Demo  
5. Add US3.x → Test independently → Deploy/Demo  

---

## Notes

- [P] tasks = different files, no dependencies
- Each user story should be independently completable and testable
- Verify tests fail before implementing
- Commit after each task or logical group
- Stop at any checkpoint to validate story independently

### Task Count Summary

- **Total tasks**: 119  
- **Parallel tasks**: 62  
- **Tasks per user story**:  
  - US1.1 (Registration): 11  
  - US1.2 (Authentication): 12  
  - US2.1 (Create Task): 8  
  - US2.2 (List Tasks): 7  
  - US2.3 (Update Task): 7  
  - US2.4 (Delete Task): 6  
  - US3.1 (Categories): 10  
  - US3.2 (Assign Category): 8  
- **Estimated MVP scope**: User Story 1.1 (Registration)