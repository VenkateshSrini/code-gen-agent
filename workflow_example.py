"""
Example: Running Spec-Driven Development Workflow with Human Approval

This example demonstrates how to use the Microsoft Agent Framework-based
workflow with human-in-the-loop approval gate.

The workflow will:
1. Load context (constitution.md, spec.md)
2. Generate implementation plan
3. Generate task breakdown
4. **PAUSE for human approval** - You review tasks.md and approve/reject
5. Generate implementation code (only if approved)

Usage:
    python workflow_example.py [base_dir] [agent_type] [tech_stack]

Examples:
    # Use GitHub Copilot
    python workflow_example.py ./co-pilot github_copilot "Python 3.10+"
    
    # Use Claude
    python workflow_example.py ./anthropic claude "Python 3.10+ with FastAPI"
"""

import asyncio
import sys
import os
from pathlib import Path

# Fix Windows console encoding issues
if sys.platform == 'win32':
    try:
        sys.stdout.reconfigure(encoding='utf-8')
        sys.stderr.reconfigure(encoding='utf-8')
    except:
        pass

from spec_orchestrator import SpecOrchestrator


async def main():
    """Run the workflow example."""
    # Parse command line arguments
    base_dir = sys.argv[1] if len(sys.argv) > 1 else "./co-pilot"
    agent_type = sys.argv[2] if len(sys.argv) > 2 else None  # Auto-detect
    tech_stack = sys.argv[3] if len(sys.argv) > 3 else "Python 3.14"
    
    print("="*70)
    print("SPEC-DRIVEN DEVELOPMENT WITH HUMAN APPROVAL")
    print("="*70)
    print(f"Base Directory: {base_dir}")
    print(f"Agent Type: {agent_type or 'auto-detect'}")
    print(f"Tech Stack: {tech_stack}")
    print("="*70)
    
    # Verify base directory exists
    base_path = Path(base_dir)
    if not base_path.exists():
        print(f"\n[ERROR] Error: Base directory not found: {base_dir}")
        print("Please create the directory and add:")
        print("  - constitution.md (coding standards and principles)")
        print("  - spec.md (feature specification)")
        return 1
    
    # Verify required files exist
    constitution_file = base_path / "constitution.md"
    spec_file = base_path / "spec.md"
    
    if not constitution_file.exists():
        print(f"\n[ERROR] constitution.md not found in {base_dir}")
        return 1
    
    if not spec_file.exists():
        print(f"\n[ERROR] spec.md not found in {base_dir}")
        return 1
    
    print(f"\n[OK] Found constitution.md")
    print(f"[OK] Found spec.md")
    
    # Create orchestrator (auto-detect agent type from directory name)
    orchestrator = SpecOrchestrator(base_dir=base_dir, agent_type=agent_type)
    
    try:
        # Use async context manager to handle agent lifecycle
        async with orchestrator:
            print(f"\n[OK] Using agent: {orchestrator.agent_type}")
            
            # Run workflow with human approval gate
            print("\n" + "="*70)
            print("STARTING WORKFLOW")
            print("="*70)
            print("\nThe workflow will pause after generating tasks.")
            print("You will be asked to review tasks.md and approve before implementation.")
            print("\nPress Ctrl+C at any time to cancel.")
            print("="*70)
            
            # Skip input prompt if stdin is not available (e.g., when run from automation)
            try:
                input("\nPress Enter to start...")
            except (EOFError, OSError):
                print("\n(Non-interactive mode detected, starting immediately...)")
            
            # Execute the workflow
            result = await orchestrator.run_workflow_with_approval(
                tech_stack=tech_stack
            )
            
            # Check if workflow was cancelled
            if result.get('cancelled', False):
                print("\n" + "="*70)
                print("WORKFLOW CANCELLED")
                print("="*70)
                print("\nThe workflow was cancelled during the approval gate.")
                print("No implementation files were generated.")
                print(f"\nGenerated artifacts (in {base_path}):")
                print("  - plan.md (implementation plan)")
                print("  - tasks.md (task breakdown)")
                print("\n" + "="*70)
                return 0
            
            # Display results
            print("\n" + "="*70)
            print("SUCCESS!")
            print("="*70)
            print(f"\n[OK] Generated {result['file_count']} code files")
            print(f"\nMarkdown files: {base_path}")
            print(f"Code files: {base_path / 'outputs'}")
            print("\nGenerated files:")
            for file_path in result['generated_files']:
                print(f"  - {file_path}")
            
            print("\nGenerated artifacts:")
            print("  - plan.md (implementation plan)")
            print("  - tasks.md (task breakdown)")
            print("  - implementation.md (full implementation)")
            if result['file_count'] > 0:
                print(f"  - outputs/ ({result['file_count']} code files extracted)")
            else:
                print("  - outputs/ (no code files extracted - check tasks.md format)")
            
            print("\n" + "="*70)
            print("You can now review and test the generated code!")
            print("="*70)
            
            return 0
    
    except KeyboardInterrupt:
        print("\n\n[WARN] Workflow cancelled by user")
        return 130  # Standard exit code for Ctrl+C
    
    except FileNotFoundError as e:
        print(f"\n[ERROR] {e}")
        return 1
    
    except Exception as e:
        print(f"\n[ERROR] Unexpected error: {e}")
        import traceback
        traceback.print_exc()
        return 1


if __name__ == "__main__":
    exit_code = asyncio.run(main())
    sys.exit(exit_code)
