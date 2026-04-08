"""
Spec-Driven Development Workflow using Microsoft Agent Framework

This module implements the spec-driven development workflow using the
Microsoft Agent Framework's programmatic workflow API with WorkflowBuilder,
Executors, and human-in-the-loop approval gates.

Workflow Phases:
1. Load Context: Read constitution.md and spec.md
2. Generate Plan: Create implementation plan
3. Generate Tasks: Break down plan into tasks
4. **Human Approval Gate**: Review and approve tasks before implementation
5. Execute Implementation: Generate code after approval

Based on Microsoft Agent Framework documentation:
- https://learn.microsoft.com/en-us/agent-framework/workflows/workflows
- https://learn.microsoft.com/en-us/agent-framework/workflows/human-in-the-loop
"""

import asyncio
import json
import re
from dataclasses import dataclass
from pathlib import Path
from typing import Optional, Dict, Any, List, Union
from collections.abc import AsyncIterable

from agent_framework import (
    Executor,
    WorkflowBuilder,
    WorkflowContext,
    WorkflowEvent,
    handler,
    response_handler,
)

from code_generator import CodeGenerator
from context_providers import AnthropicCommandProvider, CopilotCommandProvider
from spec_templates import (
    get_spec_prompt,
    get_plan_prompt,
    get_tasks_prompt,
    get_implement_prompt,
    get_template_dir,
    get_command_dir,
    parse_task_items,
    get_implement_single_task_prompt,
    get_research_prompt,
    get_data_model_prompt,
    get_quickstart_prompt,
    get_contracts_prompt,
)


@dataclass
class ContextData:
    """Data structure for loaded context files."""
    constitution: str
    spec: str
    base_dir: Path
    tech_stack: str = "Python 3.10+"
    # Plan-phase companion documents (populated by GeneratePlanExecutor)
    research: str = ""
    data_model: str = ""
    quickstart: str = ""
    contracts: str = ""


@dataclass
class PlanData:
    """Data structure for generated plan."""
    plan: str
    tech_stack: str
    context: ContextData  # Include context for next executors


@dataclass
class TasksData:
    """Data structure for generated tasks."""
    tasks: str
    task_count: int
    plan: str  # Include plan for implementation
    context: ContextData  # Include context for implementation


@dataclass
class ApprovalRequest:
    """Request for human approval with task preview."""
    message: str
    tasks_preview: str
    task_count: int


@dataclass
class ImplementationData:
    """Data structure for implementation results."""
    implementation: str
    generated_files: List[str]
    file_count: int


@dataclass
class ArtifactPaths:
    """Resolved output paths for generated workflow artifacts."""
    output_root: Path
    spec_dir: Path
    code_dir: Path
    spec_file: Path
    plan_file: Path
    tasks_file: Path
    implementation_file: Path
    assumptions_file: Path
    # Plan-phase companion outputs
    research_file: Path
    data_model_file: Path
    quickstart_file: Path
    contracts_file: Path


def _resolve_artifact_paths(base_path: Path) -> ArtifactPaths:
    """Build canonical output paths for generated artifacts."""
    output_root = base_path / "output"
    spec_dir = output_root / "spec"
    code_dir = output_root / "code"
    return ArtifactPaths(
        output_root=output_root,
        spec_dir=spec_dir,
        code_dir=code_dir,
        spec_file=spec_dir / "spec.md",
        plan_file=spec_dir / "plan.md",
        tasks_file=spec_dir / "tasks.md",
        implementation_file=spec_dir / "implementation.md",
        assumptions_file=spec_dir / "assumptions.md",
        research_file=spec_dir / "research.md",
        data_model_file=spec_dir / "data-model.md",
        quickstart_file=spec_dir / "quickstart.md",
        contracts_file=spec_dir / "contracts.md",
    )


def _make_provider(agent_type: str):
    """Return the matching command context provider for the given agent type."""
    return AnthropicCommandProvider() if agent_type == "claude" else CopilotCommandProvider()


# ---------------------------------------------------------------------------
# Shared helpers — used by both workflow executors and spec_orchestrator.py
# ---------------------------------------------------------------------------

def _extract_clarification_markers(spec_text: str) -> List[str]:
    """Return all unique NEEDS CLARIFICATION markers in appearance order."""
    seen: set = set()
    markers: List[str] = []
    for marker in re.findall(r"\[NEEDS CLARIFICATION:(.*?)\]", spec_text, flags=re.IGNORECASE):
        question = marker.strip()
        if question and question not in seen:
            seen.add(question)
            markers.append(question)
    return markers


def _replace_clarification(spec_text: str, question: str, answer: str) -> str:
    """Replace one clarification marker with the supplied answer."""
    pattern = re.compile(
        r"\[NEEDS CLARIFICATION:\s*" + re.escape(question) + r"\s*\]",
        flags=re.IGNORECASE,
    )
    return pattern.sub(answer.strip(), spec_text, count=1)


def _format_assumptions_markdown(assumptions_log: List[Dict[str, str]]) -> str:
    """Format assumption records into a markdown document."""
    lines = [
        "# Assumptions",
        "",
        "Generated after unresolved clarification items persisted beyond iterative Q&A rounds.",
        "",
    ]
    for idx, item in enumerate(assumptions_log, 1):
        lines.extend([
            f"## A{idx:03d}",
            f"- Question: {item['question']}",
            f"- Assumption: {item['assumption']}",
            f"- Rationale: {item['rationale']}",
            "",
        ])
    return "\n".join(lines)


async def _generate_assumptions(
    code_generator: "CodeGenerator",
    spec_text: str,
    unresolved_questions: List[str],
) -> Dict[str, str]:
    """Generate meaningful assumptions for unresolved clarification questions."""
    numbered = "\n".join(f"{idx + 1}. {q}" for idx, q in enumerate(unresolved_questions))
    prompt = f"""You are helping finalize a product specification.

Given this spec:
{spec_text}

Unresolved clarification questions:
{numbered}

Provide meaningful assumptions for each unresolved item.
Return STRICT JSON only with this structure:
{{
  "assumptions": [
    {{"question": "...", "assumption": "...", "rationale": "..."}}
  ]
}}""".strip()
    raw = await code_generator.generate(prompt)
    try:
        start = raw.find("{")
        end = raw.rfind("}")
        payload = json.loads(raw[start:end + 1])
        assumptions: Dict[str, str] = {}
        for item in payload.get("assumptions", []):
            question = str(item.get("question", "")).strip()
            assumption = str(item.get("assumption", "")).strip()
            if question and assumption:
                assumptions[question] = assumption
        if assumptions:
            return assumptions
    except Exception:
        pass
    return {q: f"Assume a standard, business-safe default for: {q}." for q in unresolved_questions}


def _extract_code_blocks(markdown_content: str) -> List[Dict[str, str]]:
    """Extract fenced code blocks from markdown, returning language, filename, and code."""
    code_blocks = []
    lines = markdown_content.split('\n')
    i = 0
    while i < len(lines):
        line = lines[i].strip()
        if line.startswith('```'):
            lang = line[3:].strip()
            filename = None
            if i > 0:
                prev_line = lines[i - 1].strip()
                if prev_line.startswith('**File**:') or prev_line.startswith('File:'):
                    filename = prev_line.split(':', 1)[1].strip()
            code_lines = []
            i += 1
            while i < len(lines) and not lines[i].strip().startswith('```'):
                code_lines.append(lines[i])
                i += 1
            code_blocks.append({'language': lang, 'filename': filename, 'code': '\n'.join(code_lines)})
        i += 1
    return code_blocks


def _prompt_md_files_review(spec_dir: Path) -> None:
    """List generated Markdown files and ask the user to confirm before implementation.

    Raises RuntimeError if the user declines, cancelling the workflow.
    """
    md_files = sorted(spec_dir.glob("*.md"))
    print(f"\n{'='*60}")
    print("REVIEW GENERATED MARKDOWN FILES")
    print(f"{'='*60}")
    if md_files:
        print(f"Location: {spec_dir}\n")
        for f in md_files:
            print(f"  • {f.name}")
    else:
        print(f"  (no .md files found in {spec_dir})")
    print(f"\nPlease review the files above before implementation begins.")
    print(f"{'='*60}")
    while True:
        answer = input("Are all MD files correct? Proceed with implementation? (yes/no): ").strip().lower()
        if answer in {"yes", "y"}:
            print("[OK] Confirmed. Starting implementation...\n")
            return
        if answer in {"no", "n"}:
            raise RuntimeError("Implementation cancelled: user requested to review/fix MD files first")
        print("Please enter 'yes' or 'no'")


# ---------------------------------------------------------------------------
# Base executor — shared CodeGenerator lifecycle for all workflow executors
# ---------------------------------------------------------------------------

class _AgentExecutor(Executor):
    """Provides shared CodeGenerator init and teardown. All workflow executors extend this."""

    def __init__(self, agent_type: str, id: str):
        super().__init__(id=id)
        self.agent_type = agent_type
        self.code_generator: Optional[CodeGenerator] = None

    async def _ensure_generator(self) -> None:
        """Lazily initialize the CodeGenerator on first use."""
        if self.code_generator is None:
            self.code_generator = CodeGenerator(
                agent_type=self.agent_type,
                context_provider=_make_provider(self.agent_type),
            )
            await self.code_generator._ensure_started()

    async def cleanup(self) -> None:
        if self.code_generator:
            await self.code_generator.close()


class LoadAndRouteExecutor(_AgentExecutor):
    """
    Entry-point executor that loads context files and routes the workflow
    to the appropriate phase based on which files already exist:

    - Neither plan.md nor tasks.md exist  → full flow (generate plan → tasks → code)
    - Only plan.md exists                 → resume from tasks (generate tasks → approval → code)
    - Both plan.md and tasks.md exist     → skip straight to code generation (no approval needed)
    """

    def __init__(self, agent_type: str, id: str = "load_context"):
        super().__init__(agent_type, id)

    async def _generate_spec(self, paths: ArtifactPaths, user_input: str) -> str:
        """Generate a spec document from user input using the selected agent template."""
        await self._ensure_generator()
        prompt = get_spec_prompt(
            user_input=user_input,
            template_dir=get_template_dir(self.agent_type),
            command_dir=get_command_dir(self.agent_type),
        )
        print("\n[...] Generating specification from user input...")
        spec_text = await self.code_generator.generate_spec(prompt)
        if not spec_text.strip():
            raise RuntimeError("Generated spec content is empty")
        paths.spec_dir.mkdir(parents=True, exist_ok=True)
        paths.spec_file.write_text(spec_text, encoding="utf-8")
        print(f"[OK] Spec generated and saved to: {paths.spec_file}")
        return spec_text

    async def _resolve_spec_clarifications(
        self,
        paths: ArtifactPaths,
        spec_text: str,
    ) -> str:
        """
        Resolve clarification markers via terminal Q&A.

        Targets ~3 interactive rounds; after that, fills remaining markers using
        generated assumptions and asks for explicit user approval.
        """
        round_number = 1
        assumptions_log: List[Dict[str, str]] = []

        while True:
            markers = _extract_clarification_markers(spec_text)
            if not markers:
                break

            print(f"\n[CLARIFY] Round {round_number}: {len(markers)} open clarification items")
            if round_number <= 3:
                for question in markers:
                    print(f"\n[QUESTION] {question}")
                    answer = input("Answer (leave blank to defer): ").strip()
                    if answer:
                        spec_text = _replace_clarification(spec_text, question, answer)
            else:
                print("\n[INFO] Clarification round target exceeded; generating assumptions for unresolved items...")
                await self._ensure_generator()
                assumptions = await _generate_assumptions(self.code_generator, spec_text, markers)
                for question in markers:
                    assumption = assumptions.get(question, f"Assume standard default: {question}")
                    spec_text = _replace_clarification(spec_text, question, assumption)
                    assumptions_log.append({
                        "question": question,
                        "assumption": assumption,
                        "rationale": "Applied after iterative clarification rounds to unblock planning.",
                    })
                break

            round_number += 1

        paths.spec_file.write_text(spec_text, encoding="utf-8")

        if assumptions_log:
            paths.assumptions_file.write_text(_format_assumptions_markdown(assumptions_log), encoding="utf-8")
            print(f"[OK] Assumptions recorded at: {paths.assumptions_file}")
            print("\n[APPROVAL REQUIRED] Review assumptions before planning:")
            while True:
                approve = input("Approve assumptions? (yes/no): ").strip().lower()
                if approve in {"yes", "y"}:
                    break
                if approve in {"no", "n"}:
                    raise RuntimeError("Workflow cancelled: assumptions were rejected by user")
                print("Please enter 'yes' or 'no'")

        return spec_text

    @handler
    async def load(
        self,
        input_data: Dict[str, str],
        ctx: WorkflowContext[Union[ContextData, PlanData, TasksData]]
    ) -> None:
        """
        Load constitution/spec and route to the correct phase.

        Args:
            input_data: Dict with 'base_dir' and 'tech_stack'
            ctx: Workflow context
        """
        base_dir = input_data.get('base_dir', '.')
        tech_stack = input_data.get('tech_stack', 'Python 3.10+')
        base_path = Path(base_dir)

        print(f"\n{'='*60}")
        print("PHASE 1: Loading Context")
        print(f"{'='*60}")
        print(f"Base Directory: {base_path}")
        paths = _resolve_artifact_paths(base_path)
        paths.spec_dir.mkdir(parents=True, exist_ok=True)
        paths.code_dir.mkdir(parents=True, exist_ok=True)

        # Read constitution
        constitution_path = base_path / "constitution.md"
        if not constitution_path.exists():
            raise FileNotFoundError(f"Constitution not found: {constitution_path}")
        constitution = constitution_path.read_text(encoding='utf-8')
        print(f"[OK] Loaded constitution ({len(constitution)} chars)")

        # Load or generate spec from output/spec/spec.md
        spec_is_new = not paths.spec_file.exists()
        if spec_is_new:
            print(f"[INFO] Spec not found at: {paths.spec_file}")
            user_input = ""
            while not user_input.strip():
                user_input = input("Describe what you want to build: ").strip()
                if not user_input:
                    print("Please provide a non-empty feature description.")
            spec = await self._generate_spec(paths, user_input)
        else:
            spec = paths.spec_file.read_text(encoding="utf-8")
            print(f"[OK] Loaded specification ({len(spec)} chars) from: {paths.spec_file}")

        spec = await self._resolve_spec_clarifications(paths, spec)
        print(f"[OK] Specification ready ({len(spec)} chars)")

        # Build base context; load plan-phase companion docs from disk if present
        context_data = ContextData(
            constitution=constitution,
            spec=spec,
            base_dir=base_path,
            tech_stack=tech_stack,
            research=paths.research_file.read_text(encoding="utf-8") if paths.research_file.exists() else "",
            data_model=paths.data_model_file.read_text(encoding="utf-8") if paths.data_model_file.exists() else "",
            quickstart=paths.quickstart_file.read_text(encoding="utf-8") if paths.quickstart_file.exists() else "",
            contracts=paths.contracts_file.read_text(encoding="utf-8") if paths.contracts_file.exists() else "",
        )

        # When spec was just created, force full plan/tasks regeneration
        if spec_is_new:
            print("[INFO] Spec was generated this run — forcing plan/tasks regeneration.")
            plan_exists = False
            tasks_exists = False
        else:
            plan_exists = paths.plan_file.exists()
            tasks_exists = paths.tasks_file.exists()

        if plan_exists and tasks_exists:
            # ── RESUME: both files present → skip straight to code generation ──
            plan = paths.plan_file.read_text(encoding='utf-8')
            tasks = paths.tasks_file.read_text(encoding='utf-8')
            task_count = tasks.count('- [ ] T')
            print(f"[RESUME] Found existing plan.md ({len(plan)} chars) and tasks.md ({len(tasks)} chars)")
            print(f"[RESUME] {task_count} tasks detected — skipping plan/task generation and approval")
            print(f"[RESUME] Proceeding directly to code generation...")
            tasks_data = TasksData(
                tasks=tasks,
                task_count=task_count,
                plan=plan,
                context=context_data
            )
            await ctx.send_message(tasks_data)

        elif plan_exists:
            # ── RESUME: plan exists but no tasks → generate tasks then approve ──
            plan = paths.plan_file.read_text(encoding='utf-8')
            print(f"[RESUME] Found existing plan.md ({len(plan)} chars) — skipping plan generation")
            print(f"[RESUME] Proceeding to task generation...")
            plan_data = PlanData(
                plan=plan,
                tech_stack=tech_stack,
                context=context_data
            )
            await ctx.send_message(plan_data)

        else:
            # ── FULL FLOW: nothing exists → start from scratch ──
            print("[INFO] No existing plan or tasks found — starting full workflow")
            await ctx.send_message(context_data)

class GeneratePlanExecutor(_AgentExecutor):
    """Executor that generates the implementation plan using CodeGenerator."""

    def __init__(self, agent_type: str, id: str = "generate_plan"):
        super().__init__(agent_type, id)

    @handler
    async def generate_plan(
        self,
        context: ContextData,
        ctx: WorkflowContext[PlanData]
    ) -> None:
        """
        Generate implementation plan from context.
        
        Args:
            context: Loaded constitution and spec
            ctx: Workflow context
        """
        await self._ensure_generator()
        
        # Get tech_stack from context data
        tech_stack = context.tech_stack
        
        print(f"\n{'='*60}")
        print("PHASE 2: Generating Implementation Plan")
        print(f"{'='*60}")
        print(f"Agent: {self.agent_type}")
        print(f"Tech Stack: {tech_stack}")
        
        # Generate prompt
        prompt = get_plan_prompt(
            context.constitution,
            context.spec,
            tech_stack,
            template_dir=get_template_dir(self.agent_type),
            command_dir=get_command_dir(self.agent_type),
        )

        # Generate plan
        print("\n[...] Generating plan (this may take a moment)...")
        plan = await self.code_generator.generate_plan(prompt)
        
        print(f"[OK] Plan generated ({len(plan)} chars)")

        # Save generated plan under output/spec
        paths = _resolve_artifact_paths(context.base_dir)
        paths.spec_dir.mkdir(parents=True, exist_ok=True)
        paths.plan_file.write_text(plan, encoding='utf-8')
        print(f"[OK] Plan saved to: {paths.plan_file}")

        # Generate all plan-phase companion documents
        updated_context = await self._generate_plan_phase_docs(context, paths, plan)

        # Send plan data with enriched context to next executor
        plan_data = PlanData(plan=plan, tech_stack=tech_stack, context=updated_context)
        await ctx.send_message(plan_data)

    async def _generate_plan_phase_docs(
        self,
        context: ContextData,
        paths: ArtifactPaths,
        plan: str,
    ) -> ContextData:
        """Generate research, data-model, quickstart, and contracts alongside plan.md."""
        print(f"\n{'='*60}")
        print("PHASE 2 (companion): Plan-Phase Documents")
        print(f"{'='*60}")

        # Research (Phase 0 — uses spec + tech_stack)
        print("\n[...] Generating research.md...")
        research = await self.code_generator.generate(
            get_research_prompt(context.tech_stack, context.spec, command_dir=get_command_dir(self.agent_type))
        )
        paths.research_file.write_text(research, encoding="utf-8")
        print(f"[OK] Research saved to: {paths.research_file}")

        # Data model (uses spec + plan)
        print("\n[...] Generating data-model.md...")
        data_model = await self.code_generator.generate(
            get_data_model_prompt(context.spec, plan)
        )
        paths.data_model_file.write_text(data_model, encoding="utf-8")
        print(f"[OK] Data model saved to: {paths.data_model_file}")

        # Quickstart (uses constitution + spec + plan)
        print("\n[...] Generating quickstart.md...")
        quickstart = await self.code_generator.generate(
            get_quickstart_prompt(context.constitution, context.spec, plan)
        )
        paths.quickstart_file.write_text(quickstart, encoding="utf-8")
        print(f"[OK] Quickstart saved to: {paths.quickstart_file}")

        # API contracts (uses constitution + spec + plan)
        print("\n[...] Generating contracts.md...")
        contracts = await self.code_generator.generate(
            get_contracts_prompt(context.constitution, context.spec, plan)
        )
        paths.contracts_file.write_text(contracts, encoding="utf-8")
        print(f"[OK] Contracts saved to: {paths.contracts_file}")

        # Return a new ContextData with all companion docs attached
        from dataclasses import replace as dc_replace
        return dc_replace(
            context,
            research=research,
            data_model=data_model,
            quickstart=quickstart,
            contracts=contracts,
        )


class GenerateTasksExecutor(_AgentExecutor):
    """
    Executor that generates task breakdown and requests human approval.

    This executor implements the human-in-the-loop approval gate.
    """

    def __init__(self, agent_type: str, id: str = "generate_tasks"):
        super().__init__(agent_type, id)
        self._tasks_data: Optional[TasksData] = None

    @handler
    async def generate_tasks(
        self,
        plan_data: PlanData,
        ctx: WorkflowContext[str]
    ) -> None:
        """
        Generate task breakdown from plan and request human approval.
        
        Args:
            plan_data: Generated plan
            ctx: Workflow context
        """
        await self._ensure_generator()
        
        # Get context from plan_data
        context: ContextData = plan_data.context
        
        print(f"\n{'='*60}")
        print("PHASE 3: Generating Task Breakdown")
        print(f"{'='*60}")
        print(f"Agent: {self.agent_type}")
        
        # Generate prompt — include all plan-phase companion docs as context
        prompt = get_tasks_prompt(
            context.constitution,
            context.spec,
            plan_data.plan,
            template_dir=get_template_dir(self.agent_type),
            command_dir=get_command_dir(self.agent_type),
            research=context.research,
            data_model=context.data_model,
            contracts=context.contracts,
        )

        # Generate tasks
        print("\n[...] Breaking down plan into tasks...")
        tasks = await self.code_generator.generate_tasks(prompt)
        
        # Count tasks
        task_count = tasks.count('- [ ] T')
        print(f"[OK] Generated {task_count} tasks ({len(tasks)} chars)")
        
        # Save generated tasks under output/spec
        tasks_file = _resolve_artifact_paths(context.base_dir).tasks_file
        tasks_file.parent.mkdir(parents=True, exist_ok=True)
        tasks_file.write_text(tasks, encoding='utf-8')
        print(f"[OK] Tasks saved to: {tasks_file}")
        
        # Create tasks data for next executor
        tasks_data = TasksData(
            tasks=tasks,
            task_count=task_count,
            plan=plan_data.plan,
            context=context
        )
        # Create approval request
        # Show first 500 chars of tasks as preview
        preview_length = min(500, len(tasks))
        tasks_preview = tasks[:preview_length]
        if len(tasks) > preview_length:
            tasks_preview += "\n... (truncated)"
        
        approval_request = ApprovalRequest(
            message=f"Generated {task_count} tasks. Please review output/spec/tasks.md and approve to proceed with implementation.",
            tasks_preview=tasks_preview,
            task_count=task_count
        )
        
        print(f"\n{'='*60}")
        print("HUMAN APPROVAL REQUIRED")
        print(f"{'='*60}")
        print(f"Task Count: {task_count}")
        print(f"Tasks File: {tasks_file}")
        print(f"\nPreview:\n{tasks_preview}")
        print(f"{'='*60}")
        
        # Request human approval (this pauses the workflow)
        await ctx.request_info(
            request_data=approval_request,
            response_type=bool,  # Expecting True/False response
        )
        
        # Store tasks_data to send after approval
        self._tasks_data = tasks_data
    
    @response_handler
    async def on_approval_response(
        self,
        original_request: ApprovalRequest,
        approved: bool,
        ctx: WorkflowContext[TasksData],
    ) -> None:
        """
        Handle human approval response.
        
        Args:
            original_request: The approval request sent
            approved: True if approved, False if rejected
            ctx: Workflow context
        """
        if approved:
            print("\n[OK] Tasks approved. Proceeding to implementation...")
            # Send tasks data to implementation executor
            await ctx.send_message(self._tasks_data)
        else:
            print("\n[X] Tasks rejected. Workflow terminated.")
            # Yield output and stop workflow
            await ctx.yield_output("Workflow cancelled by user")
            # Note: The workflow will complete when there's no more work
    
class ExecuteImplementationExecutor(_AgentExecutor):
    """
    Executor that generates the final implementation code.

    This executor runs only after human approval.
    """

    def __init__(self, agent_type: str, id: str = "execute_implementation"):
        super().__init__(agent_type, id)

    @handler
    async def run_implementation(
        self,
        tasks_data: TasksData,
        ctx: WorkflowContext[ImplementationData]
    ) -> None:
        """
        Execute implementation after approval.
        
        Args:
            tasks_data: Tasks data including context, plan, and tasks
            ctx: Workflow context
        """
        await self._ensure_generator()
        
        # Get all needed data from tasks_data
        context = tasks_data.context
        plan = tasks_data.plan
        tasks = tasks_data.tasks
        
        print(f"\n{'='*60}")
        print("PHASE 4: Executing Implementation (task-by-task)")
        print(f"{'='*60}")
        print(f"Agent: {self.agent_type}")

        # Create output directory for generated code files
        paths = _resolve_artifact_paths(context.base_dir)
        paths.code_dir.mkdir(parents=True, exist_ok=True)

        # Ask user to confirm all generated MD files look correct before proceeding
        _prompt_md_files_review(paths.spec_dir)

        # Parse tasks into individual file-level items
        task_items = parse_task_items(tasks)
        total = len(task_items)
        print(f"\n[...] Implementing {total} files individually...")

        all_implementations: List[str] = []
        generated_files: List[str] = []

        for idx, task_item in enumerate(task_items, 1):
            print(f"\n[{idx}/{total}] {task_item['id']}: {task_item['file_path']}")

            task_prompt = get_implement_single_task_prompt(
                context.constitution,
                context.spec,
                plan,
                tasks,
                task_item,
                research=context.research,
                data_model=context.data_model,
                quickstart=context.quickstart,
                contracts=context.contracts,
                command_dir=get_command_dir(self.agent_type),
            )

            try:
                task_impl = await self.code_generator.generate(task_prompt)
                all_implementations.append(
                    f"## {task_item['id']}: {task_item['description']}\n\n{task_impl}"
                )

                # Determine save path from task's declared file_path
                file_path = Path(task_item["file_path"])
                if file_path.parent != Path("."):
                    output_path = paths.code_dir / file_path.parent
                else:
                    output_path = paths.code_dir / "src"
                output_path.mkdir(parents=True, exist_ok=True)

                # Extract first code block from response and write it
                code_blocks = _extract_code_blocks(task_impl)
                if code_blocks:
                    saved_path = output_path / file_path.name
                    saved_path.write_text(code_blocks[0]["code"], encoding="utf-8")
                    generated_files.append(str(saved_path))
                    print(f"  [OK] Written: {saved_path}")
                else:
                    print(f"  [WARN] No code block in response for {task_item['file_path']}")

            except Exception as exc:
                print(f"  [ERROR] {task_item['id']} failed: {exc}")
                all_implementations.append(
                    f"## {task_item['id']}: {task_item['description']}\n\n**ERROR**: {exc}"
                )

        # Save combined implementation log
        implementation = "\n\n---\n\n".join(all_implementations)
        impl_file = paths.implementation_file
        impl_file.parent.mkdir(parents=True, exist_ok=True)
        impl_file.write_text(implementation, encoding="utf-8")
        print(f"\n[OK] Implementation log saved to: {impl_file}")

        print(f"\n[OK] Implementation complete!")
        print(f"  Generated {len(generated_files)} code files")

        # Yield final output
        result = ImplementationData(
            implementation=implementation,
            generated_files=generated_files,
            file_count=len(generated_files),
        )

        await ctx.yield_output(result)


def create_spec_workflow(
    base_dir: str,
    agent_type: str,
    tech_stack: str = "Python 3.10+"
) -> Any:
    """
    Create the spec-driven development workflow.
    
    Args:
        base_dir: Directory containing constitution.md and spec.md
        agent_type: Agent type ("github_copilot" or "claude")
        tech_stack: Technology stack description
    
    Returns:
        Configured workflow ready to run
    """
    # Create executors
    load_and_route = LoadAndRouteExecutor(agent_type=agent_type)
    generate_plan = GeneratePlanExecutor(agent_type=agent_type)
    generate_tasks = GenerateTasksExecutor(agent_type=agent_type)
    execute_implementation = ExecuteImplementationExecutor(agent_type=agent_type)

    # Build workflow.
    # load_and_route has three possible output types, so we add edges to all
    # potential targets.  The framework dispatches each message to the executor
    # whose @handler type-annotation matches.
    #
    #   ContextData  → generate_plan  (full flow)
    #   PlanData     → generate_tasks (resume from plan)
    #   TasksData    → execute_implementation (resume from both files)
    workflow = (
        WorkflowBuilder(start_executor=load_and_route)
        .add_edge(load_and_route, generate_plan)          # full flow: ContextData
        .add_edge(load_and_route, generate_tasks)         # resume: plan only
        .add_edge(load_and_route, execute_implementation) # resume: plan + tasks
        .add_edge(generate_plan, generate_tasks)
        .add_edge(generate_tasks, execute_implementation)
    ).build()
    
    return workflow


async def run_spec_workflow(
    base_dir: str,
    agent_type: str = "claude",
    tech_stack: str = "Python 3.10+"
) -> Optional[ImplementationData]:
    """
    Run the complete spec-driven development workflow with human approval.
    
    This function orchestrates the workflow and handles human-in-the-loop
    interaction for task approval.
    
    Args:
        base_dir: Directory containing constitution.md and spec.md
        agent_type: Agent type ("github_copilot" or "claude")
        tech_stack: Technology stack description
    
    Returns:
        ImplementationData with generated files, or None if workflow was cancelled
    
    Example:
        >>> result = await run_spec_workflow(
        ...     base_dir="./co-pilot",
        ...     agent_type="github_copilot",
        ...     tech_stack="Python 3.10+ with FastAPI"
        ... )
        >>> if result:
        ...     print(f"Generated {result.file_count} files")
    """
    print(f"\n{'='*70}")
    print("SPEC-DRIVEN DEVELOPMENT WORKFLOW")
    print(f"{'='*70}")
    print(f"Agent: {agent_type}")
    print(f"Base Directory: {base_dir}")
    print(f"Tech Stack: {tech_stack}")
    print(f"{'='*70}")
    
    # Create workflow
    workflow = create_spec_workflow(
        base_dir=base_dir,
        agent_type=agent_type,
        tech_stack=tech_stack
    )
    
    # Initialize result variable to track workflow output
    result: Optional[ImplementationData] = None
    cancelled = False
    
    # Start workflow with base_dir and tech_stack as input
    # The workflow will pause at the approval gate
    stream = workflow.run(
        message={'base_dir': base_dir, 'tech_stack': tech_stack},
        stream=True
    )
    
    # Process events and handle approval requests
    pending_responses, result_data, was_cancelled = await _process_event_stream(stream)
    if result_data:
        result = result_data
    if was_cancelled:
        cancelled = True
    
    # Continue workflow with approval responses
    while pending_responses is not None:
        stream = workflow.run(stream=True, responses=pending_responses)
        pending_responses, result_data, was_cancelled = await _process_event_stream(stream)
        if result_data:
            result = result_data
        if was_cancelled:
            cancelled = True
    
    # The workflow should have yielded the final ImplementationData
    # For now, we'll retrieve it from the last output event
    # In a real implementation, you'd collect outputs from events
    
    print(f"\n{'='*70}")
    if cancelled:
        print("WORKFLOW CANCELLED BY USER")
    else:
        print("WORKFLOW COMPLETE!")
    print(f"{'='*70}\n")
    
    # Return the captured result (None if cancelled)
    return result


async def _process_event_stream(
    stream: AsyncIterable[WorkflowEvent]
) -> tuple[Optional[Dict[str, Any]], Optional[ImplementationData], bool]:
    """
    Process workflow events and collect human approval requests.
    
    Args:
        stream: Stream of workflow events
    
    Returns:
        Tuple of:
        - Dict of request_id -> response (None if no pending requests)
        - ImplementationData if yielded by workflow (None otherwise)
        - bool indicating if workflow was cancelled by user
    """
    requests: List[tuple[str, ApprovalRequest]] = []
    result_data: Optional[ImplementationData] = None
    cancelled = False
    event_count = 0
    
    async for event in stream:
        event_count += 1

        # Surface executor failures immediately so they are not silently swallowed
        if event.type == "executor_failed":
            error_msg = str(event.details) if hasattr(event, 'details') and event.details else "unknown error"
            print(f"\n[EXECUTOR FAILED] {event.executor_id}: {error_msg}")
            # Re-raise so the caller sees the real error instead of a misleading RuntimeError
            raise RuntimeError(f"Executor '{event.executor_id}' failed: {error_msg}")

        # Handle info requests (approval gates)
        if event.type == "request_info" and isinstance(event.data, ApprovalRequest):
            requests.append((event.request_id, event.data))

        # Handle output events (progress messages)
        elif event.type == "output":
            if isinstance(event.data, str):
                print(f"  [{event.executor_id}] {event.data}")
                # Check if workflow was cancelled
                if "cancelled" in event.data.lower():
                    cancelled = True
            elif isinstance(event.data, ImplementationData):
                result_data = event.data

    print(f"[STREAM] {event_count} events processed, pending_approvals={len(requests)}, has_result={result_data is not None}")
    
    # If there are pending approval requests, collect responses
    if requests:
        responses: Dict[str, Any] = {}
        
        for request_id, request in requests:
            print(f"\n{'='*60}")
            print(request.message)
            print(f"{'='*60}")
            
            # Get user input
            while True:
                user_input = input("\nApprove? (yes/no): ").strip().lower()
                if user_input in ['yes', 'y']:
                    responses[request_id] = True
                    break
                elif user_input in ['no', 'n']:
                    responses[request_id] = False
                    cancelled = True
                    break
                else:
                    print("Please enter 'yes' or 'no'")
        
        return responses, result_data, cancelled
    
    return None, result_data, cancelled


# Example usage
if __name__ == "__main__":
    import sys
    
    async def main():
        """Example of running the workflow."""
        base_dir = sys.argv[1] if len(sys.argv) > 1 else "./co-pilot"
        agent_type = sys.argv[2] if len(sys.argv) > 2 else "github_copilot"
        tech_stack = sys.argv[3] if len(sys.argv) > 3 else "Python 3.10+"
        
        result = await run_spec_workflow(
            base_dir=base_dir,
            agent_type=agent_type,
            tech_stack=tech_stack
        )
        
        if result:
            print(f"\n[OK] Generated {result.file_count} code files")
            print(f"[OK] Spec artifacts: {Path(base_dir) / 'output' / 'spec'}")
            print(f"[OK] Code output directory: {Path(base_dir) / 'output' / 'code'}")
        else:
            print(f"\n[INFO] Workflow was cancelled. No files were generated.")
    
    asyncio.run(main())
