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
from pathlib import Path

from spec_orchestrator import SpecOrchestrator


async def main():
    """Run the workflow example."""
    # Parse command line arguments
    base_dir = sys.argv[1] if len(sys.argv) > 1 else "./co-pilot"
    agent_type = sys.argv[2] if len(sys.argv) > 2 else None  # Auto-detect
    tech_stack = sys.argv[3] if len(sys.argv) > 3 else "Python 3.10+"
    
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
        print(f"\n❌ Error: Base directory not found: {base_dir}")
        print("Please create the directory and add:")
        print("  - constitution.md (coding standards and principles)")
        print("  - spec.md (feature specification)")
        return 1
    
    # Verify required files exist
    constitution_file = base_path / "constitution.md"
    spec_file = base_path / "spec.md"
    
    if not constitution_file.exists():
        print(f"\n❌ Error: constitution.md not found in {base_dir}")
        return 1
    
    if not spec_file.exists():
        print(f"\n❌ Error: spec.md not found in {base_dir}")
        return 1
    
    print(f"\n✓ Found constitution.md")
    print(f"✓ Found spec.md")
    
    # Create orchestrator (auto-detect agent type from directory name)
    orchestrator = SpecOrchestrator(base_dir=base_dir, agent_type=agent_type)
    
    try:
        # Use async context manager to handle agent lifecycle
        async with orchestrator:
            print(f"\n✓ Using agent: {orchestrator.agent_type}")
            
            # Run workflow with human approval gate
            print("\n" + "="*70)
            print("STARTING WORKFLOW")
            print("="*70)
            print("\nThe workflow will pause after generating tasks.")
            print("You will be asked to review tasks.md and approve before implementation.")
            print("\nPress Ctrl+C at any time to cancel.")
            print("="*70)
            
            input("\nPress Enter to start...")
            
            # Execute the workflow
            result = await orchestrator.run_workflow_with_approval(
                tech_stack=tech_stack
            )
            
            # Display results
            print("\n" + "="*70)
            print("SUCCESS!")
            print("="*70)
            print(f"\n✓ Generated {result['file_count']} code files")
            print(f"\nOutput directory: {base_path / 'outputs'}")
            print("\nGenerated files:")
            for file_path in result['generated_files']:
                print(f"  - {file_path}")
            
            print("\nGenerated artifacts:")
            print("  - outputs/plan.md (implementation plan)")
            print("  - outputs/tasks.md (task breakdown)")
            print("  - outputs/implementation.md (full implementation)")
            print("  - outputs/src/ (extracted code files)")
            
            print("\n" + "="*70)
            print("You can now review and test the generated code!")
            print("="*70)
            
            return 0
    
    except KeyboardInterrupt:
        print("\n\n⚠️  Workflow cancelled by user")
        return 130  # Standard exit code for Ctrl+C
    
    except FileNotFoundError as e:
        print(f"\n❌ Error: {e}")
        return 1
    
    except Exception as e:
        print(f"\n❌ Unexpected error: {e}")
        import traceback
        traceback.print_exc()
        return 1


if __name__ == "__main__":
    exit_code = asyncio.run(main())
    sys.exit(exit_code)
