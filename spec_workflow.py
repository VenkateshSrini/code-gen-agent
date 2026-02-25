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
from spec_templates import (
    get_plan_prompt,
    get_tasks_prompt,
    get_implement_prompt,
    get_template_dir,
    parse_task_items,
    get_implement_single_task_prompt,
)


@dataclass
class ContextData:
    """Data structure for loaded context files."""
    constitution: str
    spec: str
    base_dir: Path
    tech_stack: str = "Python 3.10+"


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


class LoadAndRouteExecutor(Executor):
    """
    Entry-point executor that loads context files and routes the workflow
    to the appropriate phase based on which files already exist:

    - Neither plan.md nor tasks.md exist  → full flow (generate plan → tasks → code)
    - Only plan.md exists                 → resume from tasks (generate tasks → approval → code)
    - Both plan.md and tasks.md exist     → skip straight to code generation (no approval needed)
    """

    def __init__(self, id: str = "load_context"):
        super().__init__(id=id)

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

        # Read constitution
        constitution_path = base_path / "constitution.md"
        if not constitution_path.exists():
            raise FileNotFoundError(f"Constitution not found: {constitution_path}")
        constitution = constitution_path.read_text(encoding='utf-8')
        print(f"[OK] Loaded constitution ({len(constitution)} chars)")

        # Read spec
        spec_path = base_path / "spec.md"
        if not spec_path.exists():
            raise FileNotFoundError(f"Spec not found: {spec_path}")
        spec = spec_path.read_text(encoding='utf-8')
        print(f"[OK] Loaded specification ({len(spec)} chars)")

        # Build base context (always needed)
        context_data = ContextData(
            constitution=constitution,
            spec=spec,
            base_dir=base_path,
            tech_stack=tech_stack
        )

        plan_path = base_path / "plan.md"
        tasks_path = base_path / "tasks.md"
        plan_exists = plan_path.exists()
        tasks_exists = tasks_path.exists()

        if plan_exists and tasks_exists:
            # ── RESUME: both files present → skip straight to code generation ──
            plan = plan_path.read_text(encoding='utf-8')
            tasks = tasks_path.read_text(encoding='utf-8')
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
            plan = plan_path.read_text(encoding='utf-8')
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


class GeneratePlanExecutor(Executor):
    """
    Executor that generates the implementation plan using CodeGenerator.
    """
    
    def __init__(self, agent_type: str, id: str = "generate_plan"):
        super().__init__(id=id)
        self.agent_type = agent_type
        self.code_generator: Optional[CodeGenerator] = None
    
    async def _ensure_generator(self):
        """Initialize code generator if not already started."""
        if self.code_generator is None:
            self.code_generator = CodeGenerator(agent_type=self.agent_type)
            await self.code_generator._ensure_started()
    
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
        )

        # Generate plan using CodeGenerator
        print("\n[...] Generating plan (this may take a moment)...")
        plan = await self.code_generator.generate(prompt)
        
        print(f"[OK] Plan generated ({len(plan)} chars)")
        
        # Save plan to file (same directory as spec.md)
        plan_file = context.base_dir / "plan.md"
        plan_file.write_text(plan, encoding='utf-8')
        print(f"[OK] Plan saved to: {plan_file}")
        
        # Send plan data with full context to next executor
        plan_data = PlanData(plan=plan, tech_stack=tech_stack, context=context)
        await ctx.send_message(plan_data)
    
    async def cleanup(self):
        """Cleanup code generator on executor shutdown."""
        if self.code_generator:
            await self.code_generator.close()


class GenerateTasksExecutor(Executor):
    """
    Executor that generates task breakdown and requests human approval.
    
    This executor implements the human-in-the-loop approval gate.
    """
    
    def __init__(self, agent_type: str, id: str = "generate_tasks"):
        super().__init__(id=id)
        self.agent_type = agent_type
        self.code_generator: Optional[CodeGenerator] = None
        self._tasks_data: Optional[TasksData] = None  # Store for approval response
    
    async def _ensure_generator(self):
        """Initialize code generator if not already started."""
        if self.code_generator is None:
            self.code_generator = CodeGenerator(agent_type=self.agent_type)
            await self.code_generator._ensure_started()
    
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
        
        # Generate prompt
        prompt = get_tasks_prompt(
            context.constitution,
            context.spec,
            plan_data.plan,
            template_dir=get_template_dir(self.agent_type),
        )

        # Generate tasks using CodeGenerator
        print("\n[...] Breaking down plan into tasks...")
        tasks = await self.code_generator.generate(prompt)
        
        # Count tasks
        task_count = tasks.count('- [ ] T')
        print(f"[OK] Generated {task_count} tasks ({len(tasks)} chars)")
        
        # Save tasks to file (same directory as spec.md)
        tasks_file = context.base_dir / "tasks.md"
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
            message=f"Generated {task_count} tasks. Please review tasks.md and approve to proceed with implementation.",
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
    
    async def cleanup(self):
        """Cleanup code generator on executor shutdown."""
        if self.code_generator:
            await self.code_generator.close()


class ExecuteImplementationExecutor(Executor):
    """
    Executor that generates the final implementation code.
    
    This executor runs only after human approval.
    """
    
    def __init__(self, agent_type: str, id: str = "execute_implementation"):
        super().__init__(id=id)
        self.agent_type = agent_type
        self.code_generator: Optional[CodeGenerator] = None
    
    async def _ensure_generator(self):
        """Initialize code generator if not already started."""
        if self.code_generator is None:
            self.code_generator = CodeGenerator(agent_type=self.agent_type)
            await self.code_generator._ensure_started()
    
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

        # Create outputs directory for code files
        outputs_dir = context.base_dir / "outputs"
        outputs_dir.mkdir(parents=True, exist_ok=True)

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
            )

            try:
                task_impl = await self.code_generator.generate(task_prompt)
                all_implementations.append(
                    f"## {task_item['id']}: {task_item['description']}\n\n{task_impl}"
                )

                # Determine save path from task's declared file_path
                file_path = Path(task_item["file_path"])
                if file_path.parent != Path("."):
                    output_path = outputs_dir / file_path.parent
                else:
                    output_path = outputs_dir / "src"
                output_path.mkdir(parents=True, exist_ok=True)

                # Extract first code block from response and write it
                code_blocks = self._extract_code_blocks(task_impl)
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
        impl_file = context.base_dir / "implementation.md"
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
    
    def _extract_code_blocks(self, markdown_content: str) -> List[Dict[str, str]]:
        """
        Extract code blocks from markdown content.
        
        Returns:
            List of dicts with 'language', 'filename', 'code' keys
        """
        code_blocks = []
        lines = markdown_content.split('\n')
        i = 0
        
        while i < len(lines):
            line = lines[i].strip()
            
            # Look for code blocks with language and optional filename
            if line.startswith('```'):
                lang = line[3:].strip()
                
                # Extract filename from previous line if it looks like a file path
                filename = None
                if i > 0:
                    prev_line = lines[i-1].strip()
                    if prev_line.startswith('**File**:') or prev_line.startswith('File:'):
                        filename = prev_line.split(':', 1)[1].strip()
                
                # Collect code lines
                code_lines = []
                i += 1
                while i < len(lines) and not lines[i].strip().startswith('```'):
                    code_lines.append(lines[i])
                    i += 1
                
                code_blocks.append({
                    'language': lang,
                    'filename': filename,
                    'code': '\n'.join(code_lines)
                })
            
            i += 1
        
        return code_blocks
    
    async def cleanup(self):
        """Cleanup code generator on executor shutdown."""
        if self.code_generator:
            await self.code_generator.close()


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
    load_and_route = LoadAndRouteExecutor()
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
            print(f"[OK] Output directory: {Path(base_dir) / 'outputs'}")
        else:
            print(f"\n[INFO] Workflow was cancelled. No files were generated.")
    
    asyncio.run(main())
