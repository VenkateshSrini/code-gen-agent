"""
Spec Kit Orchestrator Module

Provides a stateful orchestrator that executes spec-driven development workflow
using CodeGenerator agents (Claude or GitHub Copilot) with Microsoft Agent Framework.

This module now uses the Microsoft Agent Framework's WorkflowBuilder for proper
workflow orchestration with human-in-the-loop approval gates.
"""

import os
import asyncio
from pathlib import Path
from typing import Optional, Dict, Any, List
from datetime import datetime

from code_generator import CodeGenerator
from spec_templates import (
    get_plan_prompt,
    get_tasks_prompt,
    get_implement_prompt,
    get_research_prompt,
    get_data_model_prompt
)

# Import the Microsoft Agent Framework workflow
from spec_workflow import run_spec_workflow, ImplementationData


class ContextManager:
    """Handles file I/O and context management for the orchestrator."""
    
    def __init__(self, base_dir: Path):
        """
        Initialize context manager.
        
        Args:
            base_dir: Base directory containing constitution.md and spec.md
        """
        self.base_dir = Path(base_dir)
        # outputs_dir used only for code files, not .md files
        self.outputs_dir = self.base_dir / "outputs"
    
    def read_file(self, filename: str) -> str:
        """Read a file from the base directory."""
        filepath = self.base_dir / filename
        if not filepath.exists():
            raise FileNotFoundError(f"Required file not found: {filepath}")
        return filepath.read_text(encoding='utf-8')
    
    def write_file(self, filename: str, content: str, subdir: Optional[str] = None):
        """
        Write content to a file.
        
        .md files are written to base_dir (same as spec.md).
        Other files go to outputs/ subdirectory.
        
        Args:
            filename: Name of the file
            content: Content to write
            subdir: Optional subdirectory within outputs
        """
        # Write .md files to base_dir (same directory as spec.md)
        if filename.endswith('.md'):
            filepath = self.base_dir / filename
        elif subdir:
            output_path = self.outputs_dir / subdir
            output_path.mkdir(parents=True, exist_ok=True)
            filepath = output_path / filename
        else:
            self.outputs_dir.mkdir(parents=True, exist_ok=True)
            filepath = self.outputs_dir / filename
        
        filepath.write_text(content, encoding='utf-8')
        return filepath
    
    def file_exists(self, filename: str, subdir: Optional[str] = None) -> bool:
        """Check if a file exists."""
        # .md files are in base_dir
        if filename.endswith('.md') and not subdir:
            filepath = self.base_dir / filename
        elif subdir:
            filepath = self.outputs_dir / subdir / filename
        else:
            filepath = self.outputs_dir / filename
        return filepath.exists()
    
    def read_output(self, filename: str, subdir: Optional[str] = None) -> str:
        """Read a previously generated output file."""
        # .md files are in base_dir
        if filename.endswith('.md') and not subdir:
            filepath = self.base_dir / filename
        elif subdir:
            filepath = self.outputs_dir / subdir / filename
        else:
            filepath = self.outputs_dir / filename
        
        if not filepath.exists():
            raise FileNotFoundError(f"Output file not found: {filepath}")
        return filepath.read_text(encoding='utf-8')
    
    def extract_code_blocks(self, markdown_content: str) -> List[Dict[str, str]]:
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


class SpecOrchestrator:
    """
    Orchestrates the spec-driven development workflow.
    
    Executes phases: constitution -> spec -> plan -> tasks -> implement
    Each phase reads outputs from previous phases.
    """
    
    def __init__(self, base_dir: str, agent_type: Optional[str] = None):
        """
        Initialize the orchestrator.
        
        Args:
            base_dir: Directory containing constitution.md and spec.md
                     ("co-pilot" or "anthropic")
            agent_type: Agent type ("github_copilot" or "claude")
                       If None, auto-detect from directory name
        """
        self.base_dir = Path(base_dir)
        
        # Auto-detect agent type from directory name
        if agent_type is None:
            dir_name = self.base_dir.name.lower()
            if 'copilot' in dir_name or 'co-pilot' in dir_name:
                agent_type = 'github_copilot'
            elif 'claude' in dir_name or 'anthropic' in dir_name:
                agent_type = 'claude'
            else:
                raise ValueError(
                    f"Cannot auto-detect agent type from directory '{dir_name}'. "
                    "Use 'co-pilot' or 'anthropic', or specify agent_type explicitly."
                )
        
        self.agent_type = agent_type
        self.context_manager = ContextManager(self.base_dir)
        self.code_generator: Optional[CodeGenerator] = None
        
        # State tracking
        self.constitution: Optional[str] = None
        self.spec: Optional[str] = None
        self.plan: Optional[str] = None
        self.tasks: Optional[str] = None
        self.research: Optional[str] = None
        self.data_model: Optional[str] = None
        
        self._started = False
    
    async def start(self):
        """Initialize the code generator agent."""
        if not self._started:
            self.code_generator = CodeGenerator(agent_type=self.agent_type)
            await self.code_generator._ensure_started()
            self._started = True
    
    async def stop(self):
        """Stop the code generator agent."""
        if self._started and self.code_generator:
            await self.code_generator.close()
            self._started = False
    
    async def __aenter__(self):
        """Support async context manager."""
        await self.start()
        return self
    
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """Cleanup on exit."""
        await self.stop()
        return False
    
    async def load_context(self) -> Dict[str, str]:
        """
        Load constitution and specification from files.
        
        Returns:
            Dict with 'constitution' and 'spec' keys
        """
        try:
            self.constitution = self.context_manager.read_file("constitution.md")
            print(f"[OK] Loaded constitution ({len(self.constitution)} chars)")
        except FileNotFoundError as e:
            print(f"[FAIL] {e}")
            raise
        
        try:
            self.spec = self.context_manager.read_file("spec.md")
            print(f"[OK] Loaded specification ({len(self.spec)} chars)")
        except FileNotFoundError as e:
            print(f"[FAIL] {e}")
            raise
        
        return {
            'constitution': self.constitution,
            'spec': self.spec
        }
    
    async def generate_plan(self, tech_stack: str, save: bool = True) -> str:
        """
        Generate implementation plan (Phase 3).
        
        Args:
            tech_stack: Technology stack and architecture description
            save: Whether to save the plan to file
            
        Returns:
            Generated plan as markdown string
        """
        if not self._started:
            await self.start()
        
        if not self.constitution or not self.spec:
            await self.load_context()
        
        print(f"\n{'='*60}")
        print("PHASE 3: Generating Implementation Plan")
        print(f"{'='*60}")
        print(f"Agent: {self.agent_type}")
        print(f"Tech Stack: {tech_stack}")
        
        # Generate prompt
        prompt = get_plan_prompt(self.constitution, self.spec, tech_stack)
        
        # Generate plan
        print("\n[...] Generating plan (this may take a moment)...")
        plan_response = await self.code_generator.generate(prompt)
        
        self.plan = plan_response
        
        if save:
            filepath = self.context_manager.write_file("plan.md", self.plan)
            print(f"[OK] Plan saved to: {filepath}")
        
        print(f"[OK] Plan generated ({len(self.plan)} chars)")
        
        return self.plan
    
    async def generate_research(self, tech_stack: str, save: bool = True) -> str:
        """
        Generate research document (Phase 0 - optional).
        
        Args:
            tech_stack: Technology stack to research
            save: Whether to save to file
            
        Returns:
            Generated research document
        """
        if not self._started:
            await self.start()
        
        if not self.spec:
            await self.load_context()
        
        print(f"\n{'='*60}")
        print("PHASE 0: Generating Research Document")
        print(f"{'='*60}")
        
        prompt = get_research_prompt(tech_stack, self.spec)
        
        print("\n[...] Researching technologies...")
        research_response = await self.code_generator.generate(prompt)
        
        self.research = research_response
        
        if save:
            filepath = self.context_manager.write_file("research.md", self.research)
            print(f"[OK] Research saved to: {filepath}")
        
        return self.research
    
    async def generate_data_model(self, save: bool = True) -> str:
        """
        Generate data model document (Phase 1 - optional).
        
        Args:
            save: Whether to save to file
            
        Returns:
            Generated data model document
        """
        if not self._started:
            await self.start()
        
        if not self.spec or not self.plan:
            raise ValueError("Must have spec and plan before generating data model")
        
        print(f"\n{'='*60}")
        print("PHASE 1: Generating Data Model")
        print(f"{'='*60}")
        
        prompt = get_data_model_prompt(self.spec, self.plan)
        
        print("\n[...] Generating data model...")
        data_model_response = await self.code_generator.generate(prompt)
        
        self.data_model = data_model_response
        
        if save:
            filepath = self.context_manager.write_file("data-model.md", self.data_model)
            print(f"[OK] Data model saved to: {filepath}")
        
        return self.data_model
    
    async def generate_tasks(self, save: bool = True) -> str:
        """
        Generate task breakdown (Phase 4).
        
        Args:
            save: Whether to save tasks to file
            
        Returns:
            Generated tasks as markdown string
        """
        if not self._started:
            await self.start()
        
        if not self.plan:
            raise ValueError("Must generate plan before generating tasks")
        
        print(f"\n{'='*60}")
        print("PHASE 4: Generating Task Breakdown")
        print(f"{'='*60}")
        
        # Generate prompt
        prompt = get_tasks_prompt(self.constitution, self.spec, self.plan)
        
        # Generate tasks
        print("\n[...] Breaking down plan into tasks...")
        tasks_response = await self.code_generator.generate(prompt)
        
        self.tasks = tasks_response
        
        if save:
            filepath = self.context_manager.write_file("tasks.md", self.tasks)
            print(f"[OK] Tasks saved to: {filepath}")
        
        # Extract task count
        task_count = self.tasks.count('- [ ] T')
        print(f"[OK] Generated {task_count} tasks")
        
        return self.tasks
    
    async def execute_implementation(self, save_code: bool = True) -> Dict[str, Any]:
        """
        Execute implementation phase (Phase 5).
        
        Args:
            save_code: Whether to save generated code to files
            
        Returns:
            Dict with implementation results and generated files
        """
        if not self._started:
            await self.start()
        
        if not self.tasks:
            raise ValueError("Must generate tasks before implementation")
        
        print(f"\n{'='*60}")
        print("PHASE 5: Executing Implementation")
        print(f"{'='*60}")
        
        # Generate prompt
        prompt = get_implement_prompt(
            self.constitution,
            self.spec,
            self.plan,
            self.tasks
        )
        
        # Generate implementation
        print("\n[...] Implementing all tasks (this will take several minutes)...")
        implementation_response = await self.code_generator.generate(prompt)
        
        # Save full implementation output
        filepath = self.context_manager.write_file(
            "implementation.md",
            implementation_response
        )
        print(f"[OK] Full implementation saved to: {filepath}")
        
        # Extract and save individual code files
        generated_files = []
        if save_code:
            print("\n Extracting code files...")
            code_blocks = self.context_manager.extract_code_blocks(implementation_response)
            
            for block in code_blocks:
                if block['filename']:
                    # Determine subdirectory from path
                    file_path = Path(block['filename'])
                    
                    # Save to src/ subdirectory
                    saved_path = self.context_manager.write_file(
                        file_path.name,
                        block['code'],
                        subdir=str(file_path.parent) if file_path.parent != Path('.') else 'src'
                    )
                    generated_files.append(str(saved_path))
                    print(f"  [OK] {block['filename']}")
        
        print(f"\n[OK] Implementation complete!")
        print(f"  Generated {len(generated_files)} code files")
        
        return {
            'implementation': implementation_response,
            'generated_files': generated_files,
            'file_count': len(generated_files)
        }
    
    async def run_full_workflow(
        self,
        tech_stack: str,
        include_research: bool = False,
        include_data_model: bool = False
    ) -> Dict[str, Any]:
        """
        Execute the complete workflow from plan to implementation.
        
        Args:
            tech_stack: Technology stack and architecture description
            include_research: Whether to generate research document
            include_data_model: Whether to generate data model
            
        Returns:
            Dict with all generated artifacts
        """
        if not self._started:
            await self.start()
        
        print(f"\n{'='*70}")
        print("SPEC-DRIVEN DEVELOPMENT WORKFLOW")
        print(f"{'='*70}")
        print(f"Agent: {self.agent_type}")
        print(f"Base Directory: {self.base_dir}")
        print(f"Timestamp: {datetime.now().isoformat()}")
        print(f"{'='*70}")
        
        # Load context
        print("\n Loading Context...")
        await self.load_context()
        
        results = {
            'constitution': self.constitution,
            'spec': self.spec,
            'agent_type': self.agent_type
        }
        
        # Optional: Generate research
        if include_research:
            research = await self.generate_research(tech_stack)
            results['research'] = research
        
        # Generate plan
        plan = await self.generate_plan(tech_stack)
        results['plan'] = plan
        
        # Optional: Generate data model
        if include_data_model:
            data_model = await self.generate_data_model()
            results['data_model'] = data_model
        
        # Generate tasks
        tasks = await self.generate_tasks()
        results['tasks'] = tasks
        
        # Execute implementation
        implementation_result = await self.execute_implementation()
        results.update(implementation_result)
        
        print(f"\n{'='*70}")
        print("WORKFLOW COMPLETE!")
        print(f"{'='*70}")
        print("Generated artifacts:")
        print(f"  [OK] plan.md")
        print(f"  [OK] tasks.md")
        print(f"  [OK] implementation.md")
        if include_research:
            print(f"  [OK] research.md")
        if include_data_model:
            print(f"  [OK] data-model.md")
        print(f"  [OK] {results['file_count']} code files")
        print(f"\nMarkdown files location: {self.base_dir}")
        print(f"Code files location: {self.context_manager.outputs_dir}")
        print(f"{'='*70}\n")
        
        return results
    
    async def run_workflow_with_approval(
        self,
        tech_stack: str = "Python 3.10+"
    ) -> Dict[str, Any]:
        """
        Execute the workflow using Microsoft Agent Framework with human approval gate.
        
        This method uses the WorkflowBuilder-based implementation with human-in-the-loop
        approval before the implementation phase, as per Microsoft Agent Framework best practices.
        
        Workflow Phases:
        1. Load Context (constitution.md, spec.md)
        2. Generate Plan
        3. Generate Tasks
        4. **Human Approval Gate** - Review and approve tasks
        5. Execute Implementation (only if approved)
        
        Args:
            tech_stack: Technology stack and architecture description
            
        Returns:
            Dict with implementation results including:
                - implementation: Full implementation markdown
                - generated_files: List of generated file paths
                - file_count: Number of files generated
        
        Example:
            >>> orchestrator = SpecOrchestrator("./co-pilot")
            >>> async with orchestrator:
            ...     result = await orchestrator.run_workflow_with_approval(
            ...         tech_stack="Python 3.10+ with FastAPI"
            ...     )
            >>> print(f"Generated {result['file_count']} files")
        """
        print(f"\n{'='*70}")
        print("MICROSOFT AGENT FRAMEWORK WORKFLOW")
        print(f"{'='*70}")
        print(f"Agent: {self.agent_type}")
        print(f"Base Directory: {self.base_dir}")
        print(f"Tech Stack: {tech_stack}")
        print(f"Timestamp: {datetime.now().isoformat()}")
        print(f"{'='*70}")
        print("\n[WARN]  This workflow includes a HUMAN APPROVAL GATE after task generation.")
        print("    You will be prompted to review and approve tasks before implementation.")
        print(f"{'='*70}\n")
        
        # Run the Microsoft Agent Framework workflow
        result: Optional[ImplementationData] = await run_spec_workflow(
            base_dir=str(self.base_dir),
            agent_type=self.agent_type,
            tech_stack=tech_stack
        )
        
        # Handle cancelled workflow
        if result is None:
            print("\n[INFO] Workflow was cancelled by user during approval gate.")
            return {
                'implementation': '',
                'generated_files': [],
                'file_count': 0,
                'agent_type': self.agent_type,
                'tech_stack': tech_stack,
                'cancelled': True
            }
        
        # Convert ImplementationData to dict for compatibility
        return {
            'implementation': result.implementation,
            'generated_files': result.generated_files,
            'file_count': result.file_count,
            'agent_type': self.agent_type,
            'tech_stack': tech_stack,
            'cancelled': False
        }
    
    async def validate_workflow(self) -> Dict[str, bool]:
        """
        Validate that all required files are present and properly formatted.
        
        Returns:
            Dict with validation results for each artifact
        """
        validations = {}
        
        # Check required input files
        validations['constitution_exists'] = self.base_dir.joinpath('constitution.md').exists()
        validations['spec_exists'] = self.base_dir.joinpath('spec.md').exists()
        
        # Check generated files (.md files are now in base_dir, not outputs_dir)
        validations['plan_generated'] = self.base_dir.joinpath('plan.md').exists()
        validations['tasks_generated'] = self.base_dir.joinpath('tasks.md').exists()
        validations['implementation_generated'] = self.base_dir.joinpath('implementation.md').exists()
        
        # Check if tasks follow proper format
        if validations['tasks_generated']:
            tasks_content = self.context_manager.read_output('tasks.md')
            validations['tasks_have_checkboxes'] = '- [ ]' in tasks_content
            validations['tasks_have_ids'] = ' T0' in tasks_content
        
        return validations

