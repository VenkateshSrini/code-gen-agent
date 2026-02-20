## Phase 1: Setup (Shared Infrastructure)
Purpose: Project initialization and basic structure
- [ ] T001 Create project structure per implementation plan under outputs\src\ and outputs\tests\
- [ ] T002 Initialize Python dependencies in requirements.txt
- [ ] T003 [P] Configure linting/formatting in pyproject.toml
- [ ] T004 [P] Add Dockerfile at project root
- [ ] T005 [P] Add docker-compose.yml for app + PostgreSQL + Redis
- [ ] T006 [P] Create .env.example with required environment variables

## Phase 2: Foundational (Blocking Prerequisites)
Purpose: Core infrastructure that MUST be complete before ANY user story
- [ ] T007 Setup SQLAlchemy async engine/session in outputs\src\db\session.py
- [ ] T008 [P] Create SQLAlchemy base/mixins and enums in outputs\src\db\base.py
- [ ] T009 Configure Alembic migrations in alembic.ini and outputs\src\db\migrations\env.py
- [ ] T010 [P] Implement settings loader in outputs\src\core\config.py
- [ ] T011 [P] Implement security helpers (bcrypt, JWT) in outputs\src\core\security.py
- [ ] T012 [P] Implement structured logging and request ID middleware in outputs\src\core\logging.py
- [ ] T013 [P] Implement tracing/correlation utilities in outputs\src\core\tracing.py
- [ ] T014 [P] Implement rate limiting middleware in outputs\src\core\rate_limit.py
- [ ] T015 [P] Implement Redis client/cache service in outputs\src\services\cache_service.py
- [ ] T016 Setup FastAPI app and API router wiring in outputs\src\main.py and outputs\src\api\v1\__init__.py
- [ ] T017 Add global exception handlers and error schemas in outputs\src\schemas\errors.py and outputs\src\core\logging.py
- [ ] T018 Add health check endpoint in outputs\src\api\v1\health.py

Checkpoint: Foundation ready - user story implementation can now begin in parallel

## Phase 3: User Story 1 - User Registration (Priority: P1) 🎯 MVP
Purpose: Register new users with email verification and initial tokens
Independent Test Criteria:
- [ ] Can register with email, password, full_name and receive tokens
- [ ] Validates email format/uniqueness and password complexity
- [ ] Creates inactive user and logs verification email

Tasks:
- [ ] T019 [US1] Write registration unit tests in outputs\tests\unit\test_auth_registration.py
- [ ] T020 [US1] Write registration integration tests in outputs\tests\integration\test_auth_register.py
- [ ] T021 [US1] Define auth request/response schemas in outputs\src\schemas\auth.py
- [ ] T022 [US1] Implement User model in outputs\src\models\user.py
- [ ] T023 [US1] Implement EmailVerificationToken model in outputs\src\models\email_verification.py
- [ ] T024 [US1] Implement user repository create/find methods in outputs\src\repositories\user_repo.py
- [ ] T025 [US1] Implement email verification repository in outputs\src\repositories\email_verification_repo.py
- [ ] T026 [US1] Implement EmailService (console backend) in outputs\src\services\email_service.py
- [ ] T027 [US1] Add validators for email/password/full_name in outputs\src\utils\validators.py
- [ ] T028 [US1] Implement AuthService.register in outputs\src\services\auth_service.py
- [ ] T029 [US1] Create registration endpoint in outputs\src\api\v1\auth.py

## Phase 4: User Story 2 - User Authentication (Priority: P1)
Purpose: Authenticate users, issue tokens, and enforce lockout/rate limits
Independent Test Criteria:
- [ ] Can login with valid credentials and receive tokens
- [ ] Locks account after 5 failed attempts
- [ ] Refresh token rotation returns new access/refresh tokens

Tasks:
- [ ] T030 [US2] Write login unit tests in outputs\tests\unit\test_auth_login.py
- [ ] T031 [US2] Write login integration tests in outputs\tests\integration\test_auth_login.py
- [ ] T032 [US2] Write refresh token integration tests in outputs\tests\integration\test_auth_refresh.py
- [ ] T033 [US2] Implement RefreshToken model in outputs\src\models\refresh_token.py
- [ ] T034 [US2] Add login tracking fields to User model in outputs\src\models\user.py
- [ ] T035 [US2] Implement token repository in outputs\src\repositories\token_repo.py
- [ ] T036 [US2] Implement TokenService (rotation/revocation) in outputs\src\services\token_service.py
- [ ] T037 [US2] Implement AuthService.login/refresh in outputs\src\services\auth_service.py
- [ ] T038 [US2] Add login and refresh endpoints in outputs\src\api\v1\auth.py
- [ ] T039 [US2] Add auth dependency for current user in outputs\src\core\security.py

## Phase 5: User Story 3 - Create Task (Priority: P1)
Purpose: Create tasks linked to authenticated users
Independent Test Criteria:
- [ ] Can create task with required title and optional fields
- [ ] Validates title length and due_date future constraint
- [ ] Returns created task with timestamps and defaults

Tasks:
- [ ] T040 [US3] Write create task unit tests in outputs\tests\unit\test_tasks_create.py
- [ ] T041 [US3] Write create task integration tests in outputs\tests\integration\test_tasks_create.py
- [ ] T042 [US3] Define task schemas in outputs\src\schemas\task.py
- [ ] T043 [US3] Implement Task model in outputs\src\models\task.py
- [ ] T044 [US3] Implement task repository create method in outputs\src\repositories\task_repo.py
- [ ] T045 [US3] Implement TaskService.create in outputs\src\services\task_service.py
- [ ] T046 [US3] Add task validators in outputs\src\utils\validators.py and outputs\src\utils\datetime.py
- [ ] T047 [US3] Create task endpoint in outputs\src\api\v1\tasks.py

## Phase 6: User Story 4 - List Tasks (Priority: P2)
Purpose: List tasks with filters, sorting, and pagination
Independent Test Criteria:
- [ ] Lists only authenticated user's tasks
- [ ] Supports filters, sorting, and pagination with total count
- [ ] Retrieves a single task by id with authorization

Tasks:
- [ ] T048 [US4] Write list tasks integration tests in outputs\tests\integration\test_tasks_list.py
- [ ] T049 [US4] Add pagination schemas in outputs\src\schemas\pagination.py
- [ ] T050 [US4] Implement list/filter query in outputs\src\repositories\task_repo.py
- [ ] T051 [US4] Implement TaskService.list in outputs\src\services\task_service.py
- [ ] T052 [US4] Add list tasks endpoint in outputs\src\api\v1\tasks.py
- [ ] T053 [US4] Add pagination utilities in outputs\src\utils\pagination.py
- [ ] T054 [US4] Write get task detail integration tests in outputs\tests\integration\test_tasks_get.py
- [ ] T055 [US4] Implement get task by id in outputs\src\repositories\task_repo.py and outputs\src\services\task_service.py
- [ ] T056 [US4] Add get task endpoint in outputs\src\api\v1\tasks.py

## Phase 7: User Story 5 - Update Task (Priority: P2)
Purpose: Update task fields with optimistic locking
Independent Test Criteria:
- [ ] Updates allowed fields only
- [ ] Enforces optimistic locking by version
- [ ] Returns 403/404 for unauthorized/missing tasks

Tasks:
- [ ] T057 [US5] Write update task integration tests in outputs\tests\integration\test_tasks_update.py
- [ ] T058 [US5] Add optimistic locking/version handling in outputs\src\models\task.py
- [ ] T059 [US5] Implement update task repository method in outputs\src\repositories\task_repo.py
- [ ] T060 [US5] Implement TaskService.update in outputs\src\services\task_service.py
- [ ] T061 [US5] Add update endpoint in outputs\src\api\v1\tasks.py

## Phase 8: User Story 6 - Delete Task (Priority: P2)
Purpose: Soft delete tasks for authenticated users
Independent Test Criteria:
- [ ] Soft deletes own task and hides it from lists
- [ ] Returns 404 for missing tasks
- [ ] Returns 403 for tasks owned by others

Tasks:
- [ ] T062 [US6] Write delete task integration tests in outputs\tests\integration\test_tasks_delete.py
- [ ] T063 [US6] Implement soft delete fields and query filters in outputs\src\models\task.py and outputs\src\repositories\task_repo.py
- [ ] T064 [US6] Implement TaskService.delete in outputs\src\services\task_service.py
- [ ] T065 [US6] Add delete endpoint in outputs\src\api\v1\tasks.py

## Phase 9: User Story 7 - Create Category (Priority: P2)
Purpose: Create and manage user categories
Independent Test Criteria:
- [ ] Creates category with name and optional color
- [ ] Enforces unique category name per user
- [ ] Lists and deletes categories for user only

Tasks:
- [ ] T066 [US7] Write category create/list/delete integration tests in outputs\tests\integration\test_categories.py
- [ ] T067 [US7] Define category schemas in outputs\src\schemas\category.py
- [ ] T068 [US7] Implement Category model in outputs\src\models\category.py
- [ ] T069 [US7] Implement category repository methods in outputs\src\repositories\category_repo.py
- [ ] T070 [US7] Implement CategoryService.create/list/delete in outputs\src\services\category_service.py
- [ ] T071 [US7] Add category validators in outputs\src\utils\validators.py
- [ ] T072 [US7] Add create/list/delete endpoints in outputs\src\api\v1\categories.py

## Phase 10: User Story 8 - Assign Category to Task (Priority: P2)
Purpose: Assign and remove task categories
Independent Test Criteria:
- [ ] Assigns category to task with ownership validation
- [ ] Prevents duplicate assignments
- [ ] Removes category assignment successfully

Tasks:
- [ ] T073 [US8] Write assign/remove category integration tests in outputs\tests\integration\test_task_categories.py
- [ ] T074 [US8] Implement TaskCategory model in outputs\src\models\task_category.py
- [ ] T075 [US8] Implement task-category repository in outputs\src\repositories\task_category_repo.py
- [ ] T076 [US8] Implement assign/remove logic in outputs\src\services\task_service.py
- [ ] T077 [US8] Add assign/remove endpoints in outputs\src\api\v1\tasks.py

## Phase 11: Polish & Cross-Cutting Concerns
Purpose: Final touches and system-wide features
- [ ] T078 Add OpenAPI metadata/tags and API versioning in outputs\src\main.py
- [ ] T079 [P] Add metrics middleware in outputs\src\core\metrics.py
- [ ] T080 [P] Wire cache-aside for user/task lookups in outputs\src\services\cache_service.py and outputs\src\services\auth_service.py
- [ ] T081 Add database indexes for filters in outputs\src\db\migrations\versions\*.py
- [ ] T082 Add contract tests for OpenAPI in outputs\tests\contract\test_openapi.py
- [ ] T083 Add security/rate limit integration tests in outputs\tests\integration\test_security.py
- [ ] T084 Add coverage configuration and test command in pyproject.toml
- [ ] T085 Add implementation documentation in implementation.md

Task Count Summary:
- Total tasks: 85
- Parallel tasks: 13
- Tasks per user story: US1=11, US2=10, US3=8, US4=9, US5=5, US6=4, US7=7, US8=5
- Estimated MVP scope: User Story 1 (User Registration)