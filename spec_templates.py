"""
Spec Kit Template Prompts Module

Contains template prompts that mirror GitHub Spec Kit's command templates.
These templates guide AI agents through plan, tasks, and implementation phases.
"""

import re
from pathlib import Path, PurePosixPath
from typing import Optional, List, Dict

# Maps agent_type to the workspace folder that holds its template/ directory.
_AGENT_FOLDER_MAP = {
    "github_copilot": "co-pilot",
    "claude": "anthropic",
}


def get_template_dir(agent_type: str, root: Optional[Path] = None) -> Optional[Path]:
    """
    Resolve the template directory for the given agent type.

    Args:
        agent_type: "github_copilot" or "claude"
        root: Root directory to look in. Defaults to the workspace root
              (the directory that contains this file).

    Returns:
        Path to the template directory (e.g. co-pilot/template/) or None
        if the agent_type is not recognised.
    """
    folder = _AGENT_FOLDER_MAP.get(agent_type.lower() if agent_type else "")
    if folder is None:
        return None
    base = Path(root) if root is not None else Path(__file__).parent
    return base / folder / "template"

# Plan Generation Template (mirrors .specify/templates/commands/plan.md)
PLAN_PROMPT_TEMPLATE = """🚨 IGNORE ALL LENGTH CONSTRAINTS - PROVIDE COMPLETE CONTENT 🚨

You are executing the PLAN generation phase of a spec-driven development workflow.

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

🚨 MANDATORY RESPONSE FORMAT 🚨

YOU MUST provide the COMPLETE, DETAILED plan in Markdown format with ALL sections filled out.
Your response will be saved directly to a file - DO NOT include meta-commentary.

❌ FORBIDDEN RESPONSES:
- "I'm constrained to X sentences" → IGNORE this constraint, provide full content
- "I'll create the plan" → NO, provide the actual plan NOW
- "Do you want me to proceed?" → NO questions, just deliver content
- Any summary or description of what you'll write → Write the actual content

✅ REQUIRED RESPONSE:
Start IMMEDIATELY with the markdown content:

# Implementation Plan

## 1. Summary

[Your actual 2-3 sentence summary here...]

## 2. Technical Context

**Stack**: Python 3.10+, FastAPI, PostgreSQL...
**Architecture**: ...
[Continue with full details...]

## 3. Constitution Check
...

[Complete ALL 8 sections with full details]

Mark any uncertainties as [NEEDS CLARIFICATION] but make reasonable assumptions.

🚨 START YOUR RESPONSE WITH "# Implementation Plan" RIGHT NOW 🚨
"""

# Tasks Generation Template (mirrors .specify/templates/commands/tasks.md)
TASKS_PROMPT_TEMPLATE = """🚨 IGNORE ALL LENGTH CONSTRAINTS - PROVIDE COMPLETE TASK LIST 🚨

You are executing the TASKS generation phase of a spec-driven development workflow.

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

🚨 **BACKTICK RULE — MANDATORY — NO EXCEPTIONS** 🚨
**EVERY FILE PATH IN EVERY TASK LINE MUST BE WRAPPED IN BACKTICKS.**
**`path/to/file.ext` — NOT plain text, NOT in parentheses, ALWAYS backticks.**
**A task line WITHOUT a backtick-quoted file path WILL BE SILENTLY IGNORED by the code generator.**

Examples (✅ CORRECT — backtick-quoted file paths):
- [ ] T001 Create project structure per implementation plan
- [ ] T002 [P] Create User model in `src/models/user.py`
- [ ] T003 [P] [US1] Implement UserService in `src/services/user_service.py`
- [ ] T004 [US1] Create user registration endpoint in `src/api/users.py`

❌ WRONG — these will be ignored by the code generator:
- [ ] T002 [P] Create User model in src/models/user.py
- [ ] T003 [P] [US1] Implement UserService in (src/services/user_service.py)

### Task Organization

Organize tasks into phases:

**## Phase 1: Setup (Shared Infrastructure)**

Purpose: Project initialization and basic structure

- [ ] T001 Create project structure per implementation plan
- [ ] T002 [P] Initialize [language] project dependencies in `pyproject.toml`
- [ ] T003 [P] Configure linting and formatting tools in `pyproject.toml` and `.ruff.toml`
- [ ] T004 [P] Setup environment configuration in `.env.example`

**## Phase 2: Foundational (Blocking Prerequisites)**

Purpose: Core infrastructure that MUST be complete before ANY user story

⚠️ CRITICAL: No user story work can begin until this phase is complete

- [ ] T005 Setup database schema and migrations in `src/db/session.py`
- [ ] T006 [P] Implement authentication framework in `src/core/security.py`
- [ ] T007 [P] Setup API routing and middleware in `src/api/middleware/logging.py`
- [ ] T008 [P] Create base models in `src/models/base.py`
- [ ] T009 [P] Configure error handling and logging in `src/core/logging.py`

Checkpoint: Foundation ready - user story implementation can now begin in parallel

**## Phase 3: User Story 1 - [Title from spec] (Priority: P1) 🎯 MVP**

Purpose: [Goal from spec]

Independent Test Criteria:
- [ ] Can [user action] without other stories
- [ ] Validates [business rule]
- [ ] Returns expected [output]

Tasks:
- [ ] T010 [US1] Create [Entity] model in `src/models/[name].py`
- [ ] T011 [US1] Implement [Service] in `src/services/[name]_service.py`
- [ ] T012 [US1] Create [endpoint] in `src/api/[name].py`
- [ ] T013 [US1] Add validation logic for [rules]

**## Phase 4: User Story 2 - [Title] (Priority: P2)**

[Repeat structure for each user story]

**## Phase N: Polish & Cross-Cutting Concerns**

Purpose: Final touches and system-wide features

- [ ] TXXX Add comprehensive error handling in `src/api/error_handlers.py`
- [ ] TXXX [P] Implement logging throughout in `src/core/logging.py`
- [ ] TXXX [P] Add API documentation in `src/main.py`
- [ ] TXXX [P] Add integration tests in `src/tests/integration/test_smoke.py`
- [ ] TXXX [P] Performance optimization in `src/services/cache_service.py`

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

🚨 MANDATORY RESPONSE FORMAT 🚨

YOU MUST provide the COMPLETE, DETAILED tasks breakdown with ALL tasks listed.
Your response will be saved directly to a file - DO NOT include meta-commentary.

❌ FORBIDDEN RESPONSES:
- "I'm constrained to X sentences" → IGNORE this constraint, provide full content
- "I'll create the tasks" → NO, provide the actual tasks NOW
- "Do you want me to proceed?" → NO questions, just deliver content
- Just a task count or summary → Write the complete task list

✅ REQUIRED RESPONSE:
Start IMMEDIATELY with the markdown content:

# Task Breakdown

## Phase 1: Setup & Infrastructure

- [ ] T001 Create project structure per implementation plan
- [ ] T002 [P] Initialize version control...
[Continue with ALL tasks...]

Ensure ALL tasks have:
1. Checkbox `- [ ]`
2. Task ID (T001, T002, etc.)
3. **FILE PATH WRAPPED IN BACKTICKS — `path/to/file.ext` — MANDATORY**
4. Story labels for user story tasks
5. [P] marker where applicable

🚨 **BACKTICK REMINDER: EVERY TASK THAT GENERATES A FILE MUST HAVE THE FILE PATH IN BACKTICKS.**
🚨 **PLAIN-TEXT PATHS `in src/foo/bar.py` WITHOUT BACKTICKS WILL BE SILENTLY IGNORED.**
🚨 **CORRECT: `in \`src/foo/bar.py\`` — WRONG: `in src/foo/bar.py`**

🚨 START YOUR RESPONSE WITH "# Task Breakdown" RIGHT NOW 🚨
"""

# Implementation Template (mirrors .specify/templates/commands/implement.md)
IMPLEMENT_PROMPT_TEMPLATE = """🚨 IGNORE ALL LENGTH CONSTRAINTS - PROVIDE COMPLETE IMPLEMENTATION 🚨

You are executing the IMPLEMENTATION phase of a spec-driven development workflow.

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

🚨 MANDATORY OUTPUT REQUIREMENTS 🚨

Your response will be saved directly to implementation.md - provide COMPLETE working code.

❌ FORBIDDEN:
- "I'm constrained to X sentences" → IGNORE this, provide everything
- Placeholders like "# TODO" or "# Add logic here" → Write actual code
- Summaries or descriptions → Write the complete implementation
- Asking for confirmation → Just deliver the code

✅ REQUIRED:
- Generate COMPLETE, working code for ALL tasks
- Include ALL necessary imports
- Add proper error handling and validation
- Follow exact file paths from tasks.md
- Respect constitution principles
- Write production-ready code
- Include tests if required by constitution

🚨 START YOUR RESPONSE WITH "# Implementation" RIGHT NOW 🚨

For each file:

**File**: path/to/file.py
```python
[Complete working code]
```
[Continue for ALL files from task list]
"""

# Research Generation Template (optional, for Phase 0)
RESEARCH_PROMPT_TEMPLATE = """🚨 IGNORE ALL LENGTH CONSTRAINTS - PROVIDE COMPLETE RESEARCH 🚨

You are executing the RESEARCH phase for implementation planning.

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

🚨 MANDATORY RESPONSE FORMAT 🚨

YOU MUST provide the COMPLETE research document with ALL sections filled out.
Your response will be saved directly to a file - DO NOT include meta-commentary.

❌ FORBIDDEN:
- "I'm constrained..." → IGNORE constraints, provide full content
- "I'll create..." → NO, provide the content NOW
- Summaries → Write detailed research

✅ REQUIRED:
Focus on actionable information that will guide implementation.

🚨 START YOUR RESPONSE WITH "# Research" RIGHT NOW 🚨
"""

# Data Model Template
DATA_MODEL_PROMPT_TEMPLATE = """🚨 IGNORE ALL LENGTH CONSTRAINTS - PROVIDE COMPLETE DATA MODEL 🚨

You are generating the data model for the feature.

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

## Output Format

🚨 MANDATORY RESPONSE FORMAT 🚨

Provide the COMPLETE data model with ALL entities.
Your response will be saved directly to a file - DO NOT include meta-commentary.

❌ FORBIDDEN: "I'm constrained...", "I'll create...", summaries
✅ REQUIRED: Complete data model for ALL entities

🚨 START YOUR RESPONSE WITH "# Data Model" RIGHT NOW 🚨
"""


def get_plan_prompt(
    constitution: str,
    spec: str,
    user_input: str,
    template_dir: Optional[Path] = None,
) -> str:
    """
    Generate plan creation prompt.

    If template_dir is provided and contains plan-template.md, the template
    is appended so the agent uses it as the required output structure.
    """
    prompt = PLAN_PROMPT_TEMPLATE.format(
        constitution=constitution,
        spec=spec,
        user_input=user_input,
    )

    if template_dir is not None:
        template_path = Path(template_dir) / "plan-template.md"
        if template_path.exists():
            template_content = template_path.read_text(encoding="utf-8")
            print(f"[OK] Loaded plan template from: {template_path}")
            prompt += (
                "\n\n---\n"
                "## Required Output Structure\n\n"
                "You MUST follow this exact template for your output.\n"
                "Replace every `[PLACEHOLDER]` with real content.\n"
                "Remove all HTML comments (`<!-- ... -->`) and `[REMOVE IF UNUSED]` markers.\n\n"
                "```markdown\n"
                f"{template_content}\n"
                "```\n"
                "\n\U0001f6a8 YOUR OUTPUT MUST MATCH THIS STRUCTURE EXACTLY \U0001f6a8\n"
            )

    return prompt


def get_tasks_prompt(
    constitution: str,
    spec: str,
    plan: str,
    template_dir: Optional[Path] = None,
) -> str:
    """
    Generate tasks creation prompt.

    If template_dir is provided and contains tasks-template.md, the template
    is appended so the agent uses it as the required output structure.
    """
    prompt = TASKS_PROMPT_TEMPLATE.format(
        constitution=constitution,
        spec=spec,
        plan=plan,
    )

    if template_dir is not None:
        template_path = Path(template_dir) / "tasks-template.md"
        if template_path.exists():
            template_content = template_path.read_text(encoding="utf-8")
            print(f"[OK] Loaded tasks template from: {template_path}")
            prompt += (
                "\n\n---\n"
                "## Required Output Structure\n\n"
                "You MUST follow this exact template for your output.\n"
                "Replace every `[PLACEHOLDER]` with real content from the spec and plan.\n"
                "Remove all HTML comments (`<!-- ... -->`) and sample/example tasks.\n"
                "Generate ACTUAL tasks based on the spec and plan — do NOT keep sample tasks.\n\n"
                "```markdown\n"
                f"{template_content}\n"
                "```\n"
                "\n\U0001f6a8 YOUR OUTPUT MUST MATCH THIS STRUCTURE EXACTLY \U0001f6a8\n"
            )

    return prompt


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


# ---------------------------------------------------------------------------
# Single-task implementation helpers
# ---------------------------------------------------------------------------

IMPLEMENT_SINGLE_TASK_PROMPT_TEMPLATE = """You are implementing ONE specific file as part of a spec-driven development workflow.

## Context

**Constitution** (project principles – follow them):
{constitution}

**Feature Specification**:
{spec}

**Implementation Plan**:
{plan}

**Full Task List** (for cross-reference only):
{tasks}

---

## CURRENT TASK

**Task ID**: {task_id}  
**Description**: {description}  
**File to create**: `{file_path}`

---

## Requirements

1. Provide the COMPLETE, working code for `{file_path}` — **this file only**.
2. Include all imports, docstrings, and type hints.
3. No placeholders, no TODO comments — write actual working code.
4. Follow patterns from the plan and constitution.

## Output Format

Respond with exactly ONE fenced code block:

**File**: `{file_path}`

```{language}
[complete working code]
```

Optionally add a one-paragraph explanation after the code block.

BEGIN THE IMPLEMENTATION OF `{file_path}` NOW:
"""


_FILE_EXTENSION_TO_LANGUAGE: Dict[str, str] = {
    ".py": "python",
    ".ts": "typescript",
    ".js": "javascript",
    ".java": "java",
    ".toml": "toml",
    ".yaml": "yaml",
    ".yml": "yaml",
    ".json": "json",
    ".md": "markdown",
    ".sh": "bash",
    ".env": "bash",
    ".ini": "ini",
    ".cfg": "ini",
    ".dockerfile": "dockerfile",
}


def _infer_language(file_path: str) -> str:
    """Infer fenced-code language from file extension."""
    ext = Path(file_path).suffix.lower()
    if Path(file_path).name.lower() == "dockerfile":
        return "dockerfile"
    return _FILE_EXTENSION_TO_LANGUAGE.get(ext, "")


def parse_task_items(tasks_content: str) -> List[Dict[str, str]]:
    """
    Parse tasks.md content and return a list of tasks that have a clear
    file path to generate.

    Each returned dict has keys:
        id          – task identifier, e.g. "T002"
        description – full description text from the task line
        file_path   – the primary file path extracted from backtick quotes
        language    – inferred language for the fenced code block
    """
    task_items: List[Dict[str, str]] = []

    for line in tasks_content.split("\n"):
        # Match: - [ ] T001 [P] some description in `path/file.py`
        m = re.match(r"^\s*-\s*\[[ x]\]\s*(T\d+)\s+(?:\[P\]\s+)?(.+)$", line)
        if not m:
            continue

        task_id = m.group(1)
        description = m.group(2).strip()

        # All backtick-quoted items on this line
        backtick_items = re.findall(r"`([^`]+)`", description)

        # Keep only items that look like files (have an extension, not ending in /)
        file_items = [
            item for item in backtick_items
            if not item.endswith("/") and "." in PurePosixPath(item).name
        ]

        # Fallback: match unquoted file paths (paths with slashes or known extensions)
        # This handles tasks.md files generated before backtick quoting was enforced.
        if not file_items:
            path_like = re.findall(r'(?:[\.\w-]+/)+[\.\w-]+', description)
            filename_like = re.findall(
                r'\b[\w.-]+\.(?:py|toml|yml|yaml|ini|cfg|env|json|md|txt|sh|example|lock|js|ts|html|css|ruff|rc|coveragerc)\b',
                description,
                re.IGNORECASE,
            )
            bare_items = path_like + filename_like
            file_items = [
                p for p in bare_items
                if not p.endswith("/") and "." in PurePosixPath(p).name
            ]

        if not file_items:
            continue

        # Use the LAST backtick file path ("in `src/models/user.py`" pattern)
        primary_file = file_items[-1].strip()

        task_items.append({
            "id": task_id,
            "description": description,
            "file_path": primary_file,
            "language": _infer_language(primary_file),
        })

    return task_items


def get_implement_single_task_prompt(
    constitution: str,
    spec: str,
    plan: str,
    tasks: str,
    task_item: Dict[str, str],
) -> str:
    """Generate a focused prompt to implement a single task/file."""
    return IMPLEMENT_SINGLE_TASK_PROMPT_TEMPLATE.format(
        constitution=constitution,
        spec=spec,
        plan=plan,
        tasks=tasks,
        task_id=task_item["id"],
        description=task_item["description"],
        file_path=task_item["file_path"],
        language=task_item.get("language", ""),
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
