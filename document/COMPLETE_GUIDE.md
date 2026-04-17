# AI Code Generator - Complete Guide

**Last Updated**: April 17, 2026

> Comprehensive documentation for the AI Code Generator with Microsoft Agent Framework and Spec-Driven Development workflows.

---

## 📑 Table of Contents

### Quick Start
- [Overview](#overview)
- [Features](#features)
- [Installation & Setup](#installation--setup)
- [Quick Start Examples](#quick-start-examples)

### Core Components
- [1. Code Generator](#1-code-generator)
  - [Available Models](#available-models)
  - [Basic Usage](#basic-usage)
  - [Agent Configuration](#agent-configuration)
  - [API Reference](#code-generator-api-reference)
- [2. Spec-Driven Development](#2-spec-driven-development)
  - [Workflow Overview](#workflow-overview)
  - [Directory Structure](#directory-structure)
  - [Usage Examples](#spec-driven-examples)
  - [API Reference](#spec-orchestrator-api-reference)
- [3. Microsoft Agent Framework Workflows](#3-microsoft-agent-framework-workflows)
  - [Workflow Implementation](#workflow-implementation)
  - [Human-in-the-Loop Approval](#human-in-the-loop-approval)
  - [Executor Classes](#executor-classes)
  - [Event Flow](#event-flow)

### Architecture & Implementation
- [Architecture Overview](#architecture-overview)
  - [System Components](#system-components)
  - [Data Flow](#data-flow)
  - [Integration Points](#integration-points)
- [Implementation Details](#implementation-details)
  - [Framework Usage](#framework-usage)
  - [Workflow Patterns](#workflow-patterns)
  - [State Management](#state-management)

### Advanced Topics
- [Validation & Testing](#validation--testing)
- [Best Practices](#best-practices)
- [Troubleshooting](#troubleshooting)
- [Advanced Usage](#advanced-usage)

### Reference
- [Environment Setup Guide](#environment-setup-guide)
  - [Backend 1: GitHub Copilot](#backend-1-github-copilot)
  - [Backend 2: Claude API (Direct)](#backend-2-claude-api-direct)
  - [Backend 3: AWS Bedrock](#backend-3-aws-bedrock)
- [Configuration Reference](#configuration-reference)
- [File Formats](#file-formats)
- [External Resources](#external-resources)

---

<a name="overview"></a>
## Overview

The AI Code Generator is a Python-based system that combines two powerful approaches to AI-assisted software development:

1. **Direct Code Generation**: Interactive code generation using Claude or GitHub Copilot agents
2. **Spec-Driven Development**: Automated workflow that transforms specifications into complete implementations

Both approaches leverage the **Microsoft Agent Framework** for reliable, production-ready AI agent integration.

### Architecture at a Glance

```
┌─────────────────────────────────────────────────────────────┐
│                    AI Code Generator                        │
├─────────────────────────────────────────────────────────────┤
│                                                             │
│  ┌─────────────────┐          ┌────────────────────────┐   │
│  │  Code Generator │          │  Spec-Driven Workflow  │   │
│  │  (Interactive)  │          │   (Automated)          │   │
│  └────────┬────────┘          └──────────┬─────────────┘   │
│           │                              │                 │
│           └──────────────┬───────────────┘                 │
│                          │                                 │
│           ┌──────────────▼─────────────────┐               │
│           │  Microsoft Agent Framework     │               │
│           ├────────────────────────────────┤               │
│           │  GitHubCopilotAgent │ ClaudeAgent             │               │
│           └────────────────────────────────┘               │
│                                                             │
└─────────────────────────────────────────────────────────────┘
```

---

<a name="features"></a>
## Features

### Code Generator Features

- ✅ **Dual Agent Support**: Choose between Claude or GitHub Copilot
- ✅ **Multiple Models**: Claude (Sonnet, Opus, Haiku), GPT-4o, GPT-5.2, O1
- ✅ **Async Context Manager**: Automatic resource management
- ✅ **Interactive Generation**: Natural language to code
- ✅ **Function/Class Generation**: Structured code creation
- ✅ **Code Refactoring**: AI-assisted code improvements
- ✅ **Documentation Generation**: Auto-generate docs
- ✅ **Error Fixing**: Fix bugs with AI assistance

### Spec-Driven Development Features

- ✅ **Automated Workflow**: Constitution → Spec → Plan → Tasks → Implementation
- ✅ **Human-in-the-Loop**: Approval gates at critical points
- ✅ **Multi-Agent Support**: Run with Copilot or Claude
- ✅ **TDD Integration**: Test-driven development by default
- ✅ **Validation System**: Comprehensive artifact validation
- ✅ **Resume Capability**: Continue from any phase
- ✅ **Comparison Mode**: Run both agents for comparison

### Framework Features

- ✅ **WorkflowBuilder**: Sequential workflow orchestration
- ✅ **Executor Pattern**: Modular workflow steps
- ✅ **Event Streaming**: Real-time progress monitoring
- ✅ **State Management**: Shared context across executors
- ✅ **Request/Response**: Human input handling
- ✅ **Checkpoint Support**: Save and resume workflows

---

<a name="installation--setup"></a>
## Installation & Setup

### Prerequisites

- Python 3.10 - 3.13 (3.14 not yet supported)
- GitHub Copilot subscription (for GitHub Copilot agent)
- Anthropic API key (for Claude agent)

### Installation Steps

1. **Clone the repository**:
   ```bash
   git clone <repository-url>
   cd code-gen-agent
   ```

2. **Create virtual environment**:
   ```bash
   python -m venv .venv
   
   # Windows
   .venv\Scripts\activate
   
   # Linux/Mac
   source .venv/bin/activate
   ```

3. **Install dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

4. **Configure environment**:
   Create a `.env` file:
   ```env
   # Agent Selection
   AGENT_TYPE=github_copilot  # or "claude"
   
   # Claude Agent Settings
   ANTHROPIC_API_KEY=your-api-key-here
   CLAUDE_MODEL=sonnet  # Options: sonnet, opus, haiku
   CLAUDE_AGENT_PERMISSION_MODE=default
   CLAUDE_AGENT_MAX_TURNS=50
   
   # GitHub Copilot Settings
   GITHUB_COPILOT_MODEL=gpt-5.2-codex  # Options: gpt-5.2, gpt-4o, claude-sonnet-4, o1
   GITHUB_COPILOT_TIMEOUT=60
   ```

5. **Verify installation**:
   ```bash
   python -c "from code_generator import CodeGenerator; print('✓ Installation successful')"
   ```

---

<a name="quick-start-examples"></a>
## Quick Start Examples

### Example 1: Interactive Code Generation

```bash
python main.py
```

Then enter prompts:
```
> Create a function to calculate fibonacci numbers
> Add a class for user authentication
> Refactor this code to use async/await
```

### Example 2: Generate a Single Function

```python
import asyncio
from code_generator import CodeGenerator

async def main():
    async with CodeGenerator(agent_type="github_copilot") as gen:
        code = await gen.generate_function(
            function_name="calculate_average",
            description="calculates the average of a list of numbers"
        )
        print(code)

asyncio.run(main())
```

### Example 3: Spec-Driven Full Workflow

```python
import asyncio
from spec_orchestrator import SpecOrchestrator

async def main():
    async with SpecOrchestrator("document/co-pilot") as orch:
        result = await orch.run_full_workflow(
            tech_stack="Python 3.10+ with FastAPI"
        )
        print(f"Generated {result['file_count']} files")

asyncio.run(main())
```

### Example 4: Workflow with Human Approval

```bash
python workflow_example.py ./document/co-pilot github_copilot "Python 3.10+"
```
```bash
python workflow_example.py ./anthropic claude  "Python 3.14"
```

The workflow will pause for your approval after generating tasks.

---

<a name="1-code-generator"></a>
## 1. Code Generator

The **CodeGenerator** class provides a unified interface for both Claude and GitHub Copilot agents.

<a name="available-models"></a>
### Available Models

#### Claude Agent
- `sonnet` - Claude Sonnet (default, fast and balanced)
- `opus` - Claude Opus (most capable)
- `haiku` - Claude Haiku (fastest)

#### GitHub Copilot Agent
- `gpt-5.2-codex` - GPT-5.2 Codex (default)
- `gpt-4o` - GPT-4 Optimized
- `claude-sonnet-4` - Claude Sonnet via Copilot
- `o1` - O1 Model
- And other models supported by GitHub Copilot

<a name="basic-usage"></a>
### Basic Usage

#### With Async Context Manager (Recommended)

```python
import asyncio
from code_generator import CodeGenerator

async def main():
    async with CodeGenerator(agent_type="claude", model="sonnet") as gen:
        # Generate code from natural language
        code = await gen.generate("Create a REST API endpoint for user login")
        print(code)
        
        # Generate a specific function
        func = await gen.generate_function(
            function_name="validate_email",
            description="validates email format using regex"
        )
        print(func)
        
        # Generate a class
        cls = await gen.generate_class(
            class_name="UserManager",
            description="handles user CRUD operations with database"
        )
        print(cls)

asyncio.run(main())
```

#### Traditional Try/Finally Pattern

```python
async def main():
    gen = CodeGenerator(agent_type="github_copilot")
    try:
        await gen._ensure_started()
        code = await gen.generate("Create a binary search function")
        print(code)
    finally:
        await gen.close()
```

<a name="agent-configuration"></a>
### Agent Configuration

#### Configure via Constructor

```python
# GitHub Copilot with specific model
gen = CodeGenerator(
    agent_type="github_copilot",
    model="gpt-4o"
)

# Claude with custom settings
gen = CodeGenerator(
    agent_type="claude",
    model="opus",
    instructions="You are a security-focused code generator..."
)
```

#### Configure via Environment Variables

```env
# In .env file
AGENT_TYPE=github_copilot
GITHUB_COPILOT_MODEL=o1
GITHUB_COPILOT_TIMEOUT=900
CLAUDE_MODEL=haiku
```

<a name="code-generator-api-reference"></a>
### Code Generator API Reference

```python
class CodeGenerator:
    """Unified interface for Claude and GitHub Copilot agents."""
    
    def __init__(
        self,
        agent_type: str = "github_copilot",
        model: str = None,
        instructions: str = None
    )
    
    async def generate(self, prompt: str) -> str:
        """Generate code from natural language prompt."""
        
    async def generate_function(
        self,
        function_name: str,
        description: str
    ) -> str:
        """Generate a specific function."""
        
    async def generate_class(
        self,
        class_name: str,
        description: str
    ) -> str:
        """Generate a complete class."""
        
    async def refactor_code(
        self,
        code: str,
        instructions: str
    ) -> str:
        """Refactor existing code."""
        
    async def add_documentation(self, code: str) -> str:
        """Add documentation to code."""
        
    async def fix_code(
        self,
        code: str,
        error_message: str
    ) -> str:
        """Fix errors in code."""
        
    async def close(self) -> None:
        """Cleanup resources."""
```

---

<a name="2-spec-driven-development"></a>
## 2. Spec-Driven Development

The **Spec-Driven Development** system automates the software development workflow from specification to implementation.

<a name="workflow-overview"></a>
### Workflow Overview

```
┌────────────────┐    ┌────────────────┐    ┌────────────────┐
│  Constitution  │───▶│  Specification │───▶│      Plan      │
│  Principles    │    │  Requirements  │    │  Architecture  │
└────────────────┘    └────────────────┘    └────────┬───────┘
                                                     │
                                                     ▼
┌────────────────┐    ┌────────────────┐    ┌────────────────┐
│ Implementation │◀───│  [APPROVAL]    │◀───│     Tasks      │
│  Generated     │    │  Human Review  │    │   Breakdown    │
│  Code Files    │    └────────────────┘    └────────────────┘
└────────────────┘
```

**Phases**:
1. **Load Context**: Read constitution.md and spec.md
2. **Generate Plan**: Create technical implementation plan
3. **Generate Tasks**: Break plan into actionable tasks
4. **[APPROVAL GATE]**: Human reviews tasks before proceeding
5. **Execute Implementation**: Generate all code with tests

<a name="directory-structure"></a>
### Directory Structure

```
code-gen-agent/
├── code_generator.py           # Agent wrapper
├── spec_orchestrator.py        # Workflow orchestration
├── spec_workflow.py            # Framework workflows
├── spec_templates.py           # Prompt templates
├── spec_validator.py           # Validation utilities
├── workflow_example.py         # Usage examples
│
└── document/
    ├── co-pilot/                # GitHub Copilot workspace
    │   ├── constitution.md      # Project principles
    │   ├── spec.md              # Requirements
    │   └── outputs/             # Generated artifacts
    │       ├── plan.md
    │       ├── tasks.md
    │       ├── implementation.md
    │       └── src/             # Extracted code files
    │
    └── anthropic/               # Claude workspace
        ├── constitution.md
        ├── spec.md
        └── outputs/
```

<a name="spec-driven-examples"></a>
### Spec-Driven Examples

#### Example 1: Full Automated Workflow

```python
import asyncio
from spec_orchestrator import SpecOrchestrator

async def main():
    # Auto-detects agent from directory name
    async with SpecOrchestrator("document/co-pilot") as orch:
        result = await orch.run_full_workflow(
            tech_stack="Python 3.10+ with FastAPI",
            include_research=True,
            include_data_model=True
        )
        
        print(f"✓ Plan: {result['plan']}")
        print(f"✓ Tasks: {len(result['tasks'].split('- [ ]'))} tasks")
        print(f"✓ Code: {result['file_count']} files generated")

asyncio.run(main())
```

#### Example 2: Phase-by-Phase with Review

```python
async def main():
    async with SpecOrchestrator("document/anthropic") as orch:
        # Phase 1: Load context
        context = await orch.load_context()
        print("✓ Loaded constitution and spec")
        
        # Phase 2: Generate plan
        plan = await orch.generate_plan("Node.js Express with MongoDB")
        print(f"✓ Generated plan ({len(plan)} chars)")
        # ... Review plan.md ...
        
        # Phase 3: Generate tasks
        tasks = await orch.generate_tasks()
        print(f"✓ Generated tasks")
        # ... Review tasks.md ...
        
        # Phase 4: Execute implementation
        impl = await orch.execute_implementation()
        print(f"✓ Generated {impl['file_count']} files")

asyncio.run(main())
```

#### Example 3: With Human Approval (Framework Workflow)

```bash
# Command line
python workflow_example.py ./document/co-pilot github_copilot "Python 3.10+"
```

Or programmatically:
```python
from spec_orchestrator import SpecOrchestrator

async def main():
    async with SpecOrchestrator("document/co-pilot") as orch:
        # Uses Microsoft Agent Framework with HITL approval
        result = await orch.run_workflow_with_approval(
            tech_stack="Python 3.10+ with FastAPI"
        )
        
        print(f"Generated {result['file_count']} files")

asyncio.run(main())
```

<a name="spec-orchestrator-api-reference"></a>
### Spec Orchestrator API Reference

```python
class SpecOrchestrator:
    """Orchestrates spec-driven development workflow."""
    
    def __init__(
        self,
        base_dir: str,
        agent_type: Optional[str] = None
    ):
        """
        Initialize orchestrator.
        
        Args:
            base_dir: Directory with constitution.md and spec.md
            agent_type: "github_copilot" or "claude" (auto-detected if None)
        """
    
    async def load_context(self) -> Dict[str, str]:
        """Load constitution and spec files."""
        
    async def generate_plan(
        self,
        tech_stack: str,
        save: bool = True
    ) -> str:
        """Generate implementation plan."""
        
    async def generate_tasks(self, save: bool = True) -> str:
        """Generate task breakdown."""
        
    async def execute_implementation(
        self,
        save_code: bool = True
    ) -> Dict[str, Any]:
        """Execute implementation phase."""
        
    async def run_full_workflow(
        self,
        tech_stack: str,
        include_research: bool = False,
        include_data_model: bool = False
    ) -> Dict[str, Any]:
        """Execute complete workflow."""
        
    async def run_workflow_with_approval(
        self,
        tech_stack: str = "Python 3.10+"
    ) -> Dict[str, Any]:
        """Execute workflow with human approval gates."""
```

---

<a name="3-microsoft-agent-framework-workflows"></a>
## 3. Microsoft Agent Framework Workflows

The system uses the **Microsoft Agent Framework** for workflow orchestration with human-in-the-loop capabilities.

<a name="workflow-implementation"></a>
### Workflow Implementation

The framework provides:
- **WorkflowBuilder**: Create sequential workflows
- **Executor**: Base class for workflow steps
- **@handler**: Decorator for input handlers
- **@response_handler**: Handle human responses
- **WorkflowContext**: State management
- **WorkflowEvent**: Event streaming

<a name="human-in-the-loop-approval"></a>
### Human-in-the-Loop Approval

The workflow pauses after generating tasks and waits for human approval:

```
============================================================
HUMAN APPROVAL REQUIRED
============================================================
Task Count: 12
Tasks File: ./document/co-pilot/outputs/tasks.md

Preview:
# Task Breakdown

## Phase 1: Setup
- [ ] T01: Create project structure
- [ ] T02: Initialize configuration files
...
============================================================

Generated 12 tasks. Please review tasks.md and approve.

Approve? (yes/no): _
```

**Workflow continues if approved, terminates if rejected.**

<a name="executor-classes"></a>
### Executor Classes

#### LoadContextExecutor

Loads constitution.md and spec.md from the base directory.

```python
class LoadContextExecutor(Executor):
    @handler
    async def load(
        self,
        input_data: Dict[str, str],
        ctx: WorkflowContext[ContextData]
    ) -> None:
        # Load files
        context_data = ContextData(...)
        await ctx.send_message(context_data)
```

#### GeneratePlanExecutor

Generates implementation plan using CodeGenerator.

```python
class GeneratePlanExecutor(Executor):
    @handler
    async def generate_plan(
        self,
        context: ContextData,
        ctx: WorkflowContext[PlanData]
    ) -> None:
        # Generate plan
        plan = await self.code_generator.generate(prompt)
        await ctx.send_message(PlanData(plan=plan, ...))
```

#### GenerateTasksExecutor

Generates tasks and requests human approval.

```python
class GenerateTasksExecutor(Executor):
    @handler
    async def generate_tasks(
        self,
        plan_data: PlanData,
        ctx: WorkflowContext[str]
    ) -> None:
        # Generate tasks
        tasks = await self.code_generator.generate(prompt)
        
        # Request approval (pauses workflow)
        await ctx.request_info(
            request_data=ApprovalRequest(...),
            response_type=bool
        )
    
    @response_handler
    async def on_approval_response(
        self,
        original_request: ApprovalRequest,
        approved: bool,
        ctx: WorkflowContext[str]
    ) -> None:
        if approved:
            await ctx.send_message("approved")
        else:
            await ctx.yield_output("Workflow cancelled")
```

#### ExecuteImplementationExecutor

Generates final implementation (only after approval).

```python
class ExecuteImplementationExecutor(Executor):
    @handler
    async def execute(
        self,
        approval_status: str,
        ctx: WorkflowContext[ImplementationData]
    ) -> None:
        # Generate implementation
        implementation = await self.code_generator.generate(prompt)
        
        # Extract and save code files
        # ...
        
        await ctx.yield_output(ImplementationData(...))
```

<a name="event-flow"></a>
### Event Flow

```python
# Create workflow
workflow = create_spec_workflow(base_dir, agent_type, tech_stack)

# Run with streaming
stream = workflow.run(
    message={'base_dir': base_dir, 'tech_stack': tech_stack},
    stream=True
)

# Process events
async for event in stream:
    if event.type == "request_info":
        # Human approval requested
        approval = input("Approve? (yes/no): ") == "yes"
        responses[event.request_id] = approval
    elif event.type == "output":
        # Progress or final output
        print(f"[{event.executor_id}] {event.data}")

# Continue with responses
workflow.run(stream=True, responses=responses)
```

**Event Types**:
- `start` - Workflow begins
- `output` - Executor yields output
- `request_info` - Human input requested (workflow pauses)
- `complete` - Workflow finishes

---

<a name="architecture-overview"></a>
## Architecture Overview

<a name="system-components"></a>
### System Components

#### 1. code_generator.py
**Purpose**: Wrapper for Microsoft Agent Framework agents  
**Framework**: ✅ Uses actual framework (GitHubCopilotAgent, ClaudeAgent)  
**Methods**: `generate()`, `generate_function()`, `generate_class()`, `close()`

#### 2. spec_orchestrator.py
**Purpose**: Workflow orchestration  
**Framework**: ❌ Direct execution (no framework)  
**Methods**: `load_context()`, `generate_plan()`, `generate_tasks()`, `execute_implementation()`, `run_full_workflow()`, `run_workflow_with_approval()`

#### 3. spec_workflow.py
**Purpose**: Microsoft Agent Framework workflows  
**Framework**: ✅ Uses WorkflowBuilder, Executor, @handler, @response_handler  
**Classes**: LoadContextExecutor, GeneratePlanExecutor, GenerateTasksExecutor, ExecuteImplementationExecutor

#### 4. spec_templates.py
**Purpose**: Prompt templates  
**Framework**: ❌ Template functions only  
**Functions**: `get_plan_prompt()`, `get_tasks_prompt()`, `get_implement_prompt()`

#### 5. spec_validator.py
**Purpose**: Validation utilities  
**Framework**: ❌ Validation logic  
**Classes**: ConstitutionValidator, PlanValidator, TaskValidator, ImplementationValidator

<a name="data-flow"></a>
### Data Flow

```
Input Files (per agent):
document/
├── co-pilot/
│   ├── constitution.md
│   └── spec.md
└── anthropic/
    ├── constitution.md
    └── spec.md

        ↓

Orchestrator Workflow:
1. Load Context
2. Generate Plan
3. Generate Tasks
4. [APPROVAL]
5. Execute Implementation

        ↓

Generated Artifacts:
document/co-pilot/outputs/
├── plan.md
├── tasks.md
├── implementation.md
└── src/
    ├── main.py
    └── ...
```

<a name="integration-points"></a>
### Integration Points

1. **code_generator.py ↔ Microsoft Agent Framework**
   - Direct integration with GitHubCopilotAgent and ClaudeAgent
   - Handles agent lifecycle, streaming, multi-turn conversations

2. **spec_orchestrator.py ↔ code_generator.py**
   - Orchestrator calls CodeGenerator for each phase
   - Passes prompts built from templates

3. **spec_workflow.py ↔ Microsoft Agent Framework**
   - Uses WorkflowBuilder for sequential orchestration
   - Executor classes with @handler decorators
   - Human-in-the-loop via request_info()

4. **All components ↔ File System**
   - Read input files (constitution.md, spec.md)
   - Write output files (plan.md, tasks.md, implementation.md, code files)

---

<a name="implementation-details"></a>
## Implementation Details

<a name="framework-usage"></a>
### Framework Usage

#### What USES the Framework

**code_generator.py**:
```python
from agent_framework_github_copilot import GitHubCopilotAgent
from agent_framework_claude import ClaudeAgent

self.agent = GitHubCopilotAgent(instructions=..., default_options=...)
response = await self.agent.generate(prompt)
```

**spec_workflow.py**:
```python
from agent_framework import (
    Executor, WorkflowBuilder, WorkflowContext,
    handler, response_handler
)

class MyExecutor(Executor):
    @handler
    async def process(self, data, ctx: WorkflowContext):
        await ctx.send_message(result)

workflow = WorkflowBuilder(start_executor=...).build()
```

#### What DOESN'T Use the Framework

**spec_orchestrator.py**: Direct async method calls, no framework workflow builders

**Why?** The orchestrator just calls CodeGenerator methods sequentially. The framework's workflow orchestration is optional and provided separately in spec_workflow.py for use cases requiring human approval gates.

<a name="workflow-patterns"></a>
### Workflow Patterns

#### Pattern 1: Direct Execution (No Framework)

```python
async with SpecOrchestrator("document/co-pilot") as orch:
    await orch.load_context()
    await orch.generate_plan("Python FastAPI")
    await orch.generate_tasks()
    await orch.execute_implementation()
```

Simple, sequential execution without framework overhead.

#### Pattern 2: Framework Workflow (With HITL)

```python
from spec_workflow import run_spec_workflow

result = await run_spec_workflow(
    base_dir="document/co-pilot",
    agent_type="github_copilot",
    tech_stack="Python FastAPI"
)
```

Uses Microsoft Agent Framework with human approval gates.

<a name="state-management"></a>
### State Management

#### SpecOrchestrator State

```python
class SpecOrchestrator:
    # State tracking
    self.constitution: Optional[str] = None
    self.spec: Optional[str] = None
    self.plan: Optional[str] = None
    self.tasks: Optional[str] = None
```

State is instance variables, preserved across method calls.

#### Workflow Context State

```python
# In executors
ctx.context["context"] = context_data
ctx.context["plan"] = plan
ctx.context["tasks"] = tasks

# Retrieve in other executors
context = ctx.context["context"]
plan = ctx.context["plan"]
```

State is shared across executors via WorkflowContext.

---

<a name="validation--testing"></a>
## Validation & Testing

### Validation System

```python
from spec_validator import (
    ConstitutionValidator,
    PlanValidator,
    TaskValidator,
    ImplementationValidator,
    validate_workflow
)

# Validate individual artifacts
constitution_valid = ConstitutionValidator.validate(constitution_content)
plan_valid = PlanValidator.validate(plan_content)
tasks_valid = TaskValidator.validate(tasks_content)
impl_valid = ImplementationValidator.validate(impl_content, tasks_content)

# Validate entire workflow
is_valid, report = validate_workflow("document/co-pilot")
print(report)
```

### Running Tests

```bash
# Run example workflows
python spec_workflow_example.py

# Run quick validation
python quick_test.py

# Run simple tests
python simple_test.py
```

---

<a name="best-practices"></a>
## Best Practices

### 1. Write Clear Constitutions

Define **non-negotiable principles**:

```markdown
# Project Constitution

## Core Principles

### I. Test-First Development (NON-NEGOTIABLE)
All code must follow TDD. Tests are written before implementation.

### II. Security by Default
All endpoints require authentication by default.

### III. API-First Design
All features expose REST APIs before UI implementation.
```

### 2. Use Detailed Specifications

```markdown
# Specification

## User Stories

### US-1.1: User Registration
**As a** new user
**I want to** register with email and password
**So that** I can access protected features

**Acceptance Criteria**:
- Email must be unique
- Password must be 8+ characters
- Confirmation email sent
- Account requires activation
```

### 3. Provide Rich Context

```python
await orchestrator.generate_plan(
    user_context="""
    This API handles 10K requests/sec.
    Deploy to AWS using ECS Fargate.
    Integrate with existing OAuth2 provider.
    Database: PostgreSQL with connection pooling.
    """
)
```

### 4. Validate Output

```python
from spec_validator import validate_workflow

# After generating artifacts
is_valid, report = validate_workflow("document/co-pilot")
if not is_valid:
    print(f"❌ Validation failed:\n{report}")
else:
    print("✅ All artifacts valid")
```

### 5. Review Before Implementation

```python
# Generate plan
await orch.generate_plan(tech_stack)

# STOP - Review plan.md manually
# Make edits if needed

# Continue with tasks
await orch.generate_tasks()
```

### 6. Use Appropriate Agent

- **GitHub Copilot**: Faster, code-focused, good for standard patterns
- **Claude**: Better reasoning, complex logic, architectural decisions

---

<a name="troubleshooting"></a>
## Troubleshooting

### Installation Issues

**Problem**: `ModuleNotFoundError: No module named 'agent_framework'`

**Solution**:
```bash
pip install agent-framework-core
```

### Missing Input Files

**Problem**: `FileNotFoundError: constitution.md not found`

**Solution**: Create required files:
```bash
mkdir -p document/co-pilot
# Create constitution.md and spec.md
```

### Agent Not Starting

**Problem**: `Error: Agent failed to start`

**Solutions**:
- GitHub Copilot: Ensure you're signed in to GitHub Copilot in VS Code
- Claude: Check `ANTHROPIC_API_KEY` in .env file
- Verify agent packages are installed

### Workflow Hangs

**Problem**: Workflow pauses indefinitely

**Solution**: Check for pending approval requests:
- Look for "HUMAN APPROVAL REQUIRED" message
- Ensure you're handling request_info events properly

### Empty or Invalid Output

**Problem**: Generated artifacts are empty or malformed

**Solutions**:
- Add more detail to spec.md
- Provide richer user_context
- Try a different model (opus instead of haiku)
- Check agent API quotas/limits

### Validation Failures

**Problem**: `validate_workflow()` returns False

**Solution**: Review validation report:
```python
is_valid, report = validate_workflow("document/co-pilot")
print(report)  # Shows specific validation errors
```

---

<a name="advanced-usage"></a>
## Advanced Usage

### Custom Prompt Templates

Override default templates:

```python
from spec_templates import get_plan_prompt

# Create custom template
custom_prompt = get_plan_prompt(
    constitution=constitution,
    spec=spec,
    tech_stack=f"{tech_stack}\n\nADDITIONAL CONTEXT:\n{custom_context}"
)

# Use in orchestrator
plan = await code_generator.generate(custom_prompt)
```

### Extract Code Blocks

```python
from spec_validator import ImplementationValidator

impl_content = open("document/co-pilot/outputs/implementation.md").read()
code_blocks = ImplementationValidator.extract_code_blocks(impl_content)

for block in code_blocks:
    print(f"File: {block['filename']}")
    print(f"Language: {block['language']}")
    print(f"Code:\n{block['code']}\n")
```

### Parallel Agent Execution

Compare both agents simultaneously:

```python
import asyncio

async def run_with_copilot():
    async with SpecOrchestrator("document/co-pilot") as orch:
        return await orch.run_full_workflow("Python FastAPI")

async def run_with_claude():
    async with SpecOrchestrator("document/anthropic") as orch:
        return await orch.run_full_workflow("Python FastAPI")

async def main():
    copilot_result, claude_result = await asyncio.gather(
        run_with_copilot(),
        run_with_claude()
    )
    
    print("Copilot generated:", copilot_result['file_count'], "files")
    print("Claude generated:", claude_result['file_count'], "files")

asyncio.run(main())
```

### CI/CD Integration

```yaml
# .github/workflows/spec-driven-dev.yml
name: Spec-Driven Development

on:
  push:
    paths:
      - 'document/*/spec.md'
      - 'document/*/constitution.md'

jobs:
  generate:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      
      - name: Set up Python
        uses: actions/setup-python@v4
        with:
          python-version: '3.11'
      
      - name: Install dependencies
        run: pip install -r requirements.txt
      
      - name: Run workflow
        env:
          ANTHROPIC_API_KEY: ${{ secrets.ANTHROPIC_API_KEY }}
        run: python spec_workflow_example.py
      
      - name: Validate output
        run: python -c "from spec_validator import validate_workflow; validate_workflow('document/co-pilot')"
```

---

<a name="environment-setup-guide"></a>
## Environment Setup Guide

The AI Code Generator supports **three code companion backends**. You only need to configure the one(s) you intend to use. A complete `.env.example` is provided in the project root — copy it and fill in your values:

```bash
cp .env.example .env
```

### How the Backends Work

```
┌──────────────────────────────────────────────────────────────────────┐
│                        CodeGenerator                                │
│                    (AGENT_TYPE env var)                              │
├─────────────────────┬────────────────────────────────────────────────┤
│                     │                                                │
│  "github_copilot"   │  "claude"                                      │
│         │           │      │                                         │
│         ▼           │      ▼                                         │
│  _RobustCopilotAgent│   ClaudeAgent (MAF)                            │
│         │           │      │                                         │
│         ▼           │      ▼                                         │
│  GitHub Copilot API │   ClaudeSDKClient                              │
│                     │      │                                         │
│                     │      ▼                                         │
│                     │   Claude Code CLI (subprocess)                 │
│                     │      │                                         │
│                     │      ├──── ANTHROPIC_API_KEY → Anthropic API   │
│                     │      │     (direct, default)                   │
│                     │      │                                         │
│                     │      └──── CLAUDE_CODE_USE_BEDROCK=1           │
│                     │            + AWS creds → AWS Bedrock API       │
└─────────────────────┴────────────────────────────────────────────────┘
```

> **Key insight**: AWS Bedrock is NOT a separate agent type. It's a backend switch for the Claude agent. Setting `CLAUDE_CODE_USE_BEDROCK=1` tells the Claude Code CLI to route LLM calls through Bedrock instead of the Anthropic API. All agentic capabilities (tool use, file I/O) are fully preserved.

---

<a name="backend-1-github-copilot"></a>
### Backend 1: GitHub Copilot

**When to use**: Default choice. Uses GitHub's infrastructure. Supports GPT and Claude models via the Copilot proxy.

#### Prerequisites

1. Active [GitHub Copilot subscription](https://github.com/features/copilot) (Individual, Business, or Enterprise)
2. VS Code with the GitHub Copilot extension installed and signed in
3. A [Personal Access Token (PAT)](https://github.com/settings/tokens) with `copilot` scope

#### Setup

```env
# .env
AGENT_TYPE=github_copilot
COPILOT_GITHUB_TOKEN=github_pat_XXXXXXXXXXXXXXXXXXXX
GITHUB_COPILOT_MODEL=gpt-5.3-codex
GITHUB_COPILOT_TIMEOUT=900
```

#### Available Models

| Model | Description |
|---|---|
| `gpt-5.3-codex` | Default. Most capable for code generation |
| `gpt-4o` | Fast, good general-purpose |
| `claude-sonnet-4` | Claude Sonnet via Copilot proxy |
| `o1` | Reasoning-focused |

#### Verify

```python
import asyncio
from code_generator import CodeGenerator

async def main():
    async with CodeGenerator(agent_type="github_copilot") as gen:
        result = await gen.generate("Write a Python hello world function")
        print(result)

asyncio.run(main())
```

---

<a name="backend-2-claude-api-direct"></a>
### Backend 2: Claude API (Direct)

**When to use**: When you want full Claude Code agentic capabilities (file I/O, bash, tools) via the Anthropic API directly.

#### Prerequisites

1. [Anthropic API key](https://console.anthropic.com/) (starts with `sk-ant-`)
2. `agent-framework-claude` package (included in `agent-framework[all]`)

#### How to Get an API Key

1. Go to [console.anthropic.com](https://console.anthropic.com/)
2. Navigate to **API Keys** → **Create Key**
3. Copy the key

#### Setup

```env
# .env
AGENT_TYPE=claude
ANTHROPIC_API_KEY=sk-ant-api03-XXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX
CLAUDE_MODEL=sonnet
CLAUDE_CODE_MAX_OUTPUT_TOKENS=92000
```

#### Available Models

| Model | Description |
|---|---|
| `sonnet` | Default. Balanced speed and quality |
| `opus` | Most capable, slower |
| `haiku` | Fastest, best for simple tasks |

#### Architecture Detail

The Claude agent works through the **Claude Code CLI**, which is bundled inside the `claude-agent-sdk` Python package:

```
CodeGenerator(agent_type="claude")
  → ClaudeAgent (agent-framework-claude)
    → ClaudeSDKClient (claude-agent-sdk)
      → Claude Code CLI subprocess
        → Anthropic Messages API (using ANTHROPIC_API_KEY)
```

The CLI provides agentic capabilities: file reading/writing, bash execution, tool use, and MCP server support. Your `CodeGenerator` has write permissions denied to keep output as text responses.

#### Verify

```python
import asyncio
from code_generator import CodeGenerator

async def main():
    async with CodeGenerator(agent_type="claude") as gen:
        result = await gen.generate("Write a Python hello world function")
        print(result)

asyncio.run(main())
```

---

<a name="backend-3-aws-bedrock"></a>
### Backend 3: AWS Bedrock

**When to use**: When you want Claude's agentic capabilities but need to route LLM calls through your AWS account (cost control, compliance, data residency, enterprise billing).

#### How It Works

This is **not a code change** — it's a configuration switch. Setting `CLAUDE_CODE_USE_BEDROCK=1` tells the Claude Code CLI subprocess to use AWS Bedrock's Invoke API instead of the Anthropic API. Everything else (the agent, the SDK, the CLI, the tools) works identically.

```
CodeGenerator(agent_type="claude")
  → ClaudeAgent (agent-framework-claude)        ← same
    → ClaudeSDKClient (claude-agent-sdk)        ← same
      → Claude Code CLI subprocess              ← same
        → AWS Bedrock Invoke API                ← changed (was Anthropic API)
          (uses AWS_ACCESS_KEY_ID / AWS_REGION)
```

#### Prerequisites

1. **AWS account** with Bedrock access enabled
2. **Enable Claude models in Bedrock** (one-time):
   - Go to [Amazon Bedrock console](https://console.aws.amazon.com/bedrock/) → **Model catalog**
   - Select the Anthropic Claude model you want (e.g., Claude Sonnet)
   - Submit the use case form — access is granted immediately
3. **IAM permissions** — attach this policy to your IAM user/role:
   ```json
   {
     "Version": "2012-10-17",
     "Statement": [
       {
         "Effect": "Allow",
         "Action": [
           "bedrock:InvokeModel",
           "bedrock:InvokeModelWithResponseStream",
           "bedrock:ListInferenceProfiles"
         ],
         "Resource": [
           "arn:aws:bedrock:*:*:inference-profile/*",
           "arn:aws:bedrock:*:*:application-inference-profile/*",
           "arn:aws:bedrock:*:*:foundation-model/*"
         ]
       }
     ]
   }
   ```
4. **AWS credentials** via one of the options below

#### Setup

Add these to your `.env` (in addition to `AGENT_TYPE=claude` and `CLAUDE_MODEL`):

```env
# .env — Bedrock additions
CLAUDE_CODE_USE_BEDROCK=1
AWS_REGION=us-east-1
```

Then choose **one** authentication method:

**Option A — Access Keys** (simplest for development):
```env
AWS_ACCESS_KEY_ID=AKIAIOSFODNN7EXAMPLE
AWS_SECRET_ACCESS_KEY=wJalrXUtnFEMI/K7MDENG/bPxRfiCYEXAMPLEKEY
# AWS_SESSION_TOKEN=...   # only if using temporary credentials (STS)
```

**Option B — AWS CLI Profile** (preferred for SSO / multi-account):
```env
AWS_PROFILE=your-profile-name
```
First run: `aws sso login --profile=your-profile-name`

**Option C — Bedrock API Key** (simplest, no full AWS credentials):
```env
AWS_BEARER_TOKEN_BEDROCK=your-bedrock-api-key
```

#### Model Pinning (Recommended)

Without pinning, model aliases like `sonnet` resolve to the latest version. If Anthropic releases a new model version before it's enabled in your Bedrock account, the CLI falls back to the previous version — but you may want deterministic control:

```env
# Pin specific Bedrock model versions
ANTHROPIC_DEFAULT_SONNET_MODEL=us.anthropic.claude-sonnet-4-5-20250929-v1:0
ANTHROPIC_DEFAULT_OPUS_MODEL=us.anthropic.claude-opus-4-6
ANTHROPIC_DEFAULT_HAIKU_MODEL=us.anthropic.claude-haiku-4-5-20251001-v1:0
```

Model IDs use the `us.` prefix for cross-region inference profiles. Adjust the prefix for your region.

#### Switching Between Backends

| To use... | Set in `.env` |
|---|---|
| Claude via Anthropic API | `AGENT_TYPE=claude` + `ANTHROPIC_API_KEY=...` |
| Claude via AWS Bedrock | `AGENT_TYPE=claude` + `CLAUDE_CODE_USE_BEDROCK=1` + AWS creds |
| Back to Anthropic API | Set `CLAUDE_CODE_USE_BEDROCK=0` or remove the line |
| GitHub Copilot | `AGENT_TYPE=github_copilot` (Bedrock vars are ignored) |

`ANTHROPIC_API_KEY` can remain in `.env` even when Bedrock is active — it is ignored when `CLAUDE_CODE_USE_BEDROCK=1` is set, and serves as a fallback if you disable Bedrock.

#### Verify

```python
import asyncio
from code_generator import CodeGenerator

async def main():
    async with CodeGenerator(agent_type="claude") as gen:
        result = await gen.generate("Write a Python hello world function")
        print(result)

asyncio.run(main())
```

To confirm Bedrock is the actual backend:
1. Temporarily remove `ANTHROPIC_API_KEY` from `.env`
2. Run the test above — if it succeeds, Bedrock is active
3. Restore `ANTHROPIC_API_KEY` afterward

#### Cost & Operations Notes

- **Billing**: Bedrock usage appears on your **AWS bill**, not Anthropic's. Use AWS Cost Explorer to track costs.
- **Region latency**: Choose the AWS region closest to your workload. Ensure the Claude model is enabled there.
- **Credential rotation**: For production, prefer AWS SSO or IAM roles over static access keys.
- **Guardrails**: Bedrock supports content filtering — see [AWS Guardrails docs](https://docs.aws.amazon.com/bedrock/latest/userguide/guardrails.html).

---

### Complete `.env` Quick Reference

```
┌─────────────────────────┬─────────────────┬───────────┬───────────────────┐
│ Variable                │ GitHub Copilot  │ Claude API│ Claude + Bedrock  │
├─────────────────────────┼─────────────────┼───────────┼───────────────────┤
│ AGENT_TYPE              │ github_copilot  │ claude    │ claude            │
│ COPILOT_GITHUB_TOKEN    │ ✅ required     │ —         │ —                 │
│ GITHUB_COPILOT_MODEL    │ ✅ optional     │ —         │ —                 │
│ ANTHROPIC_API_KEY       │ —               │ ✅ required│ — (ignored)      │
│ CLAUDE_MODEL            │ —               │ ✅ optional│ ✅ optional       │
│ CLAUDE_CODE_USE_BEDROCK │ —               │ — (unset) │ ✅ = 1            │
│ AWS_REGION              │ —               │ —         │ ✅ required        │
│ AWS_ACCESS_KEY_ID       │ —               │ —         │ ✅ required*       │
│ AWS_SECRET_ACCESS_KEY   │ —               │ —         │ ✅ required*       │
└─────────────────────────┴─────────────────┴───────────┴───────────────────┘
* Or use AWS_PROFILE / AWS_BEARER_TOKEN_BEDROCK instead of access keys.
```

---

<a name="configuration-reference"></a>
## Configuration Reference

### Orchestrator Configuration

```python
SpecOrchestrator(
    base_dir="document/co-pilot",  # Auto-detects github_copilot
    agent_type=None                 # Explicit override
)
```

Auto-detection rules:
- Directory contains "copilot" or "co-pilot" → `github_copilot`
- Directory contains "claude" or "anthropic" → `claude`

---

<a name="file-formats"></a>
## File Formats

### constitution.md

```markdown
# Project Constitution

## Core Principles

### I. Principle Name (NON-NEGOTIABLE)
Description of the principle...

### II. Another Principle
Description...

## Technical Standards

### Testing
- All code must have tests
- Minimum 80% code coverage

### Documentation
- All public APIs documented
- Inline comments for complex logic
```

### spec.md

```markdown
# Project Specification: Project Name

## Overview
Brief description of the project.

## User Stories

### US-1.1: Feature Name
**As a** user type
**I want to** do something
**So that** I achieve benefit

**Acceptance Criteria**:
- Criterion 1
- Criterion 2

**Technical Notes**:
- Implementation detail
- Constraint

## Non-Functional Requirements
- Performance: 1000 req/sec
- Security: OAuth2 authentication
```

### Generated Files

**plan.md**: Architecture, components, data models, API contracts

**tasks.md**: Phased task breakdown with checkboxes
```markdown
## Phase 1: Foundation
- [ ] Task 1: Description
- [ ] Task 2: Description

## Phase 2: Core Features
- [ ] Task 3: Description
```

**implementation.md**: Tests + implementation code with file markers
```markdown
**File**: `src/main.py`
```python
# Code here
```

**File**: `tests/test_main.py`
```python
# Tests here
```
```

---

<a name="external-resources"></a>
## External Resources

### Microsoft Agent Framework

- [Documentation](https://learn.microsoft.com/en-us/agent-framework/)
- [Workflows Guide](https://learn.microsoft.com/en-us/agent-framework/workflows/workflows)
- [Declarative Workflows](https://learn.microsoft.com/en-us/agent-framework/workflows/declarative)
- [Human-in-the-Loop](https://learn.microsoft.com/en-us/agent-framework/workflows/human-in-the-loop)
- [State Management](https://learn.microsoft.com/en-us/agent-framework/workflows/state)
- [Checkpoints](https://learn.microsoft.com/en-us/agent-framework/workflows/checkpoints)
- [GitHub Repository](https://github.com/microsoft/agent-framework)

### AI Agents & Cloud Providers

- [GitHub Copilot](https://github.com/features/copilot)
- [Anthropic Claude](https://www.anthropic.com/claude)
- [Claude Code CLI Documentation](https://code.claude.com/docs/en/overview)
- [Claude Agent SDK (Python)](https://pypi.org/project/claude-agent-sdk/)
- [Amazon Bedrock — Claude Setup](https://code.claude.com/docs/en/amazon-bedrock)
- [Amazon Bedrock Console](https://console.aws.amazon.com/bedrock/)
- [Bedrock IAM Permissions](https://docs.aws.amazon.com/bedrock/latest/userguide/security-iam.html)
- [Bedrock Pricing](https://aws.amazon.com/bedrock/pricing/)

### Inspiration

- [GitHub Spec Kit](https://github.com/github/spec-kit)

---

## Summary

This guide covers:

✅ **Code Generator**: Interactive code generation with Claude/Copilot  
✅ **Environment Setup**: Complete guide for GitHub Copilot, Claude API, and AWS Bedrock  
✅ **Spec-Driven Development**: Automated workflow from spec to implementation  
✅ **Microsoft Agent Framework**: Workflow orchestration with HITL approval  
✅ **Architecture**: System components and integration points  
✅ **Implementation**: Framework usage patterns and state management  
✅ **Best Practices**: Writing constitutions, specs, validation  
✅ **Troubleshooting**: Common issues and solutions  
✅ **Advanced Usage**: Custom templates, parallel execution, CI/CD  

---

**Version**: 1.1.0  
**Last Updated**: April 17, 2026  
**Framework**: Microsoft Agent Framework (Python)  
**License**: [Your License]

---

For questions, issues, or contributions, please visit the project repository.
