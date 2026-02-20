"""
Spec Kit Template Prompts Module

Contains template prompts that mirror GitHub Spec Kit's command templates.
These templates guide AI agents through plan, tasks, and implementation phases.
"""

# Plan Generation Template (mirrors .specify/templates/commands/plan.md)
PLAN_PROMPT_TEMPLATE = """You are executing the PLAN generation phase of a spec-driven development workflow.

## Context

**Constitution** (Project Principles):
{constitution}

**Feature Specification**:
{spec}

## User Input (Tech Stack & Architecture)

{user_input}

## Your Task

Generate a comprehensive implementation plan following this structure:

### 1. Summary
- Provide a 2-3 sentence overview of the feature and chosen tech stack

### 2. Technical Context
Extract from user input and spec:
- **Stack**: [Programming language, framework, key libraries]
- **Architecture**: [Pattern: MVC, microservices, serverless, etc.]
- **Database**: [Type and specific database]
- **Constraints**: [Performance targets, scale requirements]
- **Deployment**: [Platform and approach]

### 3. Constitution Check

Review the constitution and verify:
- List each principle that applies to this implementation
- For each principle, add a checklist item showing compliance
- Example:
  - [ ] Test-First Development: Tests will be written before implementation
  - [ ] CLI-First: All features expose CLI interfaces
  - [ ] Library-First: Core logic in standalone libraries

### 4. Project Structure

Provide the actual directory structure based on the tech stack.

For single project (backend only):
```
src/
├── models/
├── services/
├── api/
└── utils/

tests/
├── unit/
├── integration/
└── contract/
```

For web application (frontend + backend):
```
backend/
├── src/
│   ├── models/
│   ├── services/
│   └── api/
└── tests/

frontend/
├── src/
│   ├── components/
│   ├── pages/
│   └── services/
└── tests/
```

### 5. Data Model

List all entities/models needed:
- Entity name
- Key fields with types
- Relationships
- Validation rules

### 6. API Contracts

For each user story, define:
- Endpoint path and method
- Request/Response schemas
- Status codes
- Authentication requirements

### 7. Implementation Phases

**Phase 0: Research**
- List key technologies that need investigation
- Best practices to research
- Integration patterns to validate

**Phase 1: Foundation**
- Project setup tasks
- Database schema
- Authentication/authorization framework
- Base models and services

**Phase 2: Core Features**
- Group by user story
- List implementation order
- Note dependencies

**Phase 3: Testing & Polish**
- Test coverage requirements
- Performance optimization
- Documentation

### 8. Risk Assessment

Identify:
- Technical risks
- Complexity hotspots
- External dependencies
- Mitigation strategies

## Output Format

YOU MUST provide the COMPLETE, DETAILED plan in Markdown format with ALL sections filled out.

DO NOT respond with:
- A summary saying "I'll create the plan" or "Plan written to file"
- A description of what you would write
- A brief overview with no details

INSTEAD, respond with the ACTUAL, COMPLETE PLAN CONTENT following the structure above.

Example start of your response:
```markdown
# Implementation Plan

## 1. Summary

[Actual 2-3 sentence summary here...]

## 2. Technical Context

**Stack**: Python 3.10+, FastAPI, PostgreSQL...
[etc.]
```

Mark any uncertainties as [NEEDS CLARIFICATION] but try to make reasonable assumptions based on context.

BEGIN YOUR RESPONSE WITH THE PLAN CONTENT NOW:
"""

# Tasks Generation Template (mirrors .specify/templates/commands/tasks.md)
TASKS_PROMPT_TEMPLATE = """You are executing the TASKS generation phase of a spec-driven development workflow.

## Context

**Constitution**:
{constitution}

**Feature Specification**:
{spec}

**Implementation Plan**:
{plan}

## Your Task

Generate a detailed, actionable task list following this structure:

### Task Format Requirements

Each task MUST follow this format:
```
- [ ] [TaskID] [P?] [Story?] Description with file path
```

Where:
- **Checkbox**: Always `- [ ]`
- **TaskID**: Sequential (T001, T002, T003...)
- **[P]**: Include ONLY if task can run in parallel (different files, no dependencies)
- **[Story]**: Required for user story tasks: [US1], [US2], etc.
- **Description**: Clear action with exact file path

Examples:
- [ ] T001 Create project structure per implementation plan
- [ ] T002 [P] Create User model in src/models/user.py
- [ ] T003 [P] [US1] Implement UserService in src/services/user_service.py
- [ ] T004 [US1] Create user registration endpoint in src/api/users.py

### Task Organization

Organize tasks into phases:

**## Phase 1: Setup (Shared Infrastructure)**

Purpose: Project initialization and basic structure

- [ ] T001 Create project structure per implementation plan
- [ ] T002 Initialize [language] project with [framework] dependencies
- [ ] T003 [P] Configure linting and formatting tools
- [ ] T004 [P] Setup environment configuration

**## Phase 2: Foundational (Blocking Prerequisites)**

Purpose: Core infrastructure that MUST be complete before ANY user story

⚠️ CRITICAL: No user story work can begin until this phase is complete

- [ ] T005 Setup database schema and migrations framework
- [ ] T006 [P] Implement authentication/authorization framework
- [ ] T007 [P] Setup API routing and middleware structure
- [ ] T008 Create base models/entities
- [ ] T009 Configure error handling and logging

Checkpoint: Foundation ready - user story implementation can now begin in parallel

**## Phase 3: User Story 1 - [Title from spec] (Priority: P1) 🎯 MVP**

Purpose: [Goal from spec]

Independent Test Criteria:
- [ ] Can [user action] without other stories
- [ ] Validates [business rule]
- [ ] Returns expected [output]

Tasks:
- [ ] T010 [US1] Create [Entity] model in src/models/[name].py
- [ ] T011 [US1] Implement [Service] in src/services/[name]_service.py
- [ ] T012 [US1] Create [endpoint] in src/api/[name].py
- [ ] T013 [US1] Add validation logic for [rules]

**## Phase 4: User Story 2 - [Title] (Priority: P2)**

[Repeat structure for each user story]

**## Phase N: Polish & Cross-Cutting Concerns**

Purpose: Final touches and system-wide features

- [ ] TXXX Add comprehensive error handling
- [ ] TXXX [P] Implement logging throughout
- [ ] TXXX [P] Add API documentation
- [ ] TXXX Add integration tests
- [ ] TXXX Performance optimization

### Dependencies & Execution Order

**Phase Dependencies:**
1. Setup MUST complete first
2. Foundational MUST complete before any user story
3. User stories can run in parallel after foundational
4. Polish runs last

**Parallel Opportunities:**
Tasks marked [P] can run simultaneously if:
- Different files
- No shared dependencies
- Independent business logic

### Task Count Summary

Provide at end:
- Total tasks: [number]
- Parallel tasks: [number]
- Tasks per user story
- Estimated MVP scope (typically User Story 1)

## Output Format

YOU MUST provide the COMPLETE, DETAILED tasks breakdown with ALL tasks listed.

DO NOT respond with:
- A summary saying "I'll create the tasks" or "Tasks written to file"
- A description of what you would write
- Just the count of tasks

INSTEAD, respond with the ACTUAL, COMPLETE TASK LIST following the structure above.

Ensure ALL tasks have:
1. Checkbox `- [ ]`
2. Task ID
3. Exact file paths
4. Story labels for user story tasks
5. [P] marker where applicable

BEGIN YOUR RESPONSE WITH THE TASKS CONTENT NOW:
"""

# Implementation Template (mirrors .specify/templates/commands/implement.md)
IMPLEMENT_PROMPT_TEMPLATE = """You are executing the IMPLEMENTATION phase of a spec-driven development workflow.

## Context

**Constitution**:
{constitution}

**Feature Specification**:
{spec}

**Implementation Plan**:
{plan}

**Task List**:
{tasks}

## Your Task

Execute ALL tasks from the task list following these rules:

### Implementation Approach

1. **Follow Task Order**:
   - Complete Setup phase first
   - Complete Foundational phase second
   - Then proceed with User Stories in priority order
   - Tasks marked [P] can be done in parallel

2. **Test-Driven Development** (if constitution requires):
   - Write tests FIRST
   - Run tests (they should FAIL)
   - Implement code
   - Run tests (they should PASS)
   - Refactor if needed

3. **Constitution Compliance**:
   Review each principle from constitution and ensure implementation adheres:
{constitution_checks}

4. **File Generation**:
   - Create files in exact paths specified in tasks
   - Include proper imports and dependencies
   - Add comprehensive docstrings and type hints
   - Follow language-specific best practices

5. **Code Quality Standards**:
   - No syntax errors
   - Proper error handling
   - Input validation
   - Memory safety
   - Security best practices
   - Performance considerations

### Output Format

YOU MUST provide the COMPLETE, WORKING IMPLEMENTATION for ALL tasks.

DO NOT respond with:
- A summary saying "Implementation written" or "Code generated"
- Placeholders or TODOs
- Just file names without content

INSTEAD, respond with the ACTUAL, COMPLETE CODE for each task.

For each task, provide:

#### Task [TaskID]: [Description]
**File**: [exact path from task]

```[language]
[Complete, working code for this file]
```

**Explanation**:
[Brief explanation of implementation choices]

**Tests** (if TDD required):
```[language]
[Test code that validates this implementation]
```

---

BEGIN YOUR RESPONSE WITH THE IMPLEMENTATION CONTENT NOW:

Continue until ALL tasks are implemented.

### Final Validation

After all tasks:
1. ✅ All files created in correct structure
2. ✅ All imports resolve correctly
3. ✅ No syntax errors
4. ✅ Constitution principles followed
5. ✅ Tests pass (if applicable)
6. ✅ API contracts match specification

## Important Notes

- Generate COMPLETE, working code (no placeholders like "# TODO" or "# Add logic here")
- Include ALL necessary imports
- Add proper error handling
- Follow the exact file paths from tasks.md
- Respect the constitution principles
- Ensure code is production-ready
"""

# Research Generation Template (optional, for Phase 0)
RESEARCH_PROMPT_TEMPLATE = """You are executing the RESEARCH phase for implementation planning.

## Context

**Tech Stack from User**:
{tech_stack}

**Feature Requirements**:
{spec}

## Your Task

Research and document decisions for:

### 1. Technology Choices

For each technology in the stack:
- **Decision**: [What was chosen]
- **Rationale**: [Why this choice]
- **Alternatives Considered**: [What else was evaluated]
- **Trade-offs**: [Pros and cons]

### 2. Best Practices

For the chosen stack:
- Project structure conventions
- Naming conventions
- Testing approaches
- Error handling patterns
- Security considerations

### 3. Integration Patterns

How components will work together:
- Database connection patterns
- API design patterns
- Authentication flows
- State management (if frontend)
- Caching strategies

### 4. Known Limitations

- Scale limits
- Performance considerations
- Browser/platform compatibility
- Third-party service dependencies

## Output Format

YOU MUST provide the COMPLETE research document with ALL sections filled out.

DO NOT respond with a summary or meta-response.
INSTEAD, provide the ACTUAL, DETAILED research.md content.

Focus on actionable information that will guide implementation.

BEGIN YOUR RESPONSE WITH THE RESEARCH CONTENT NOW:
"""

# Data Model Template
DATA_MODEL_PROMPT_TEMPLATE = """You are generating the data model for the feature.

## Context

**Feature Specification**:
{spec}

**Implementation Plan**:
{plan}

## Your Task

Extract all entities/models and define their structure:

### Format

For each entity:

## [EntityName]

**Description**: [What this entity represents]

**Fields**:
| Field | Type | Required | Constraints | Description |
|-------|------|----------|-------------|-------------|
| id | UUID | Yes | Primary Key | Unique identifier |
| name | String | Yes | Max 255 chars | Entity name |
| created_at | DateTime | Yes | Auto-set | Creation timestamp |

**Relationships**:
- Has many [OtherEntity]
- Belongs to [ParentEntity]

**Validation Rules**:
- name must be unique
- email must be valid format

**Indexes**:
- Index on email for fast lookup
- Composite index on (user_id, created_at)

---

Continue for all entities identified in the specification.
"""


def get_plan_prompt(constitution: str, spec: str, user_input: str) -> str:
    """Generate plan creation prompt."""
    return PLAN_PROMPT_TEMPLATE.format(
        constitution=constitution,
        spec=spec,
        user_input=user_input
    )


def get_tasks_prompt(constitution: str, spec: str, plan: str) -> str:
    """Generate tasks creation prompt."""
    return TASKS_PROMPT_TEMPLATE.format(
        constitution=constitution,
        spec=spec,
        plan=plan
    )


def get_implement_prompt(constitution: str, spec: str, plan: str, tasks: str) -> str:
    """Generate implementation prompt."""
    # Extract constitution principles for checks
    constitution_checks = _extract_constitution_checks(constitution)
    
    return IMPLEMENT_PROMPT_TEMPLATE.format(
        constitution=constitution,
        spec=spec,
        plan=plan,
        tasks=tasks,
        constitution_checks=constitution_checks
    )


def get_research_prompt(tech_stack: str, spec: str) -> str:
    """Generate research prompt."""
    return RESEARCH_PROMPT_TEMPLATE.format(
        tech_stack=tech_stack,
        spec=spec
    )


def get_data_model_prompt(spec: str, plan: str) -> str:
    """Generate data model prompt."""
    return DATA_MODEL_PROMPT_TEMPLATE.format(
        spec=spec,
        plan=plan
    )


def _extract_constitution_checks(constitution: str) -> str:
    """Extract principle checks from constitution."""
    # Simple extraction - looks for headings that might be principles
    lines = constitution.split('\n')
    checks = []
    
    for line in lines:
        # Look for markdown headers that might be principles
        if line.strip().startswith('###') or line.strip().startswith('##'):
            principle = line.strip().lstrip('#').strip()
            if principle and not principle.lower() in ['core principles', 'governance', 'principles']:
                checks.append(f"   - [ ] {principle}: [Verify compliance]")
    
    if not checks:
        checks.append("   - [ ] Review all constitution principles for compliance")
    
    return '\n'.join(checks)
