"""
Spec Workflow Examples

Demonstrates how to use the SpecOrchestrator for spec-driven development.
Run examples to generate plans, tasks, and implementation from specifications.
"""

import asyncio
from pathlib import Path
from spec_orchestrator import SpecOrchestrator
from spec_validator import validate_workflow


async def example_1_full_workflow_copilot():
    """
    Example 1: Full workflow with GitHub Copilot
    
    Runs complete workflow: plan → tasks → implementation
    """
    print("\n" + "="*70)
    print("EXAMPLE 1: Full Workflow with GitHub Copilot")
    print("="*70 + "\n")
    
    try:
        async with SpecOrchestrator("document/co-pilot", "github_copilot") as orchestrator:
            results = await orchestrator.run_full_workflow(
                tech_stack="""
                Python with FastAPI framework
                PostgreSQL database with SQLAlchemy ORM
                Redis for caching
                JWT authentication
                RESTful API architecture
                Docker containerization
                """,
                include_research=True,
                include_data_model=True
            )
            
            print("\n✓ Workflow completed successfully!")
            print(f"  Generated {results['file_count']} code files")
            
    except FileNotFoundError as e:
        print(f"\n✗ Error: {e}")
        print("  Make sure 'document/co-pilot/constitution.md' and 'document/co-pilot/spec.md' exist")
    except Exception as e:
        print(f"\n✗ Unexpected error: {e}")


async def example_2_full_workflow_claude():
    """
    Example 2: Full workflow with Claude
    
    Runs complete workflow using Claude agent
    """
    print("\n" + "="*70)
    print("EXAMPLE 2: Full Workflow with Claude")
    print("="*70 + "\n")
    
    try:
        async with SpecOrchestrator("document/anthropic", "claude") as orchestrator:
            results = await orchestrator.run_full_workflow(
                tech_stack="""
                React with TypeScript
                Supabase backend (PostgreSQL + Auth)
                TailwindCSS for styling
                Vite build tool
                Vercel deployment
                """,
                include_research=False,
                include_data_model=True
            )
            
            print("\n✓ Workflow completed successfully!")
            print(f"  Generated {results['file_count']} code files")
            
    except FileNotFoundError as e:
        print(f"\n✗ Error: {e}")
        print("  Make sure 'document/anthropic/constitution.md' and 'document/anthropic/spec.md' exist")
    except Exception as e:
        print(f"\n✗ Unexpected error: {e}")


async def example_3_phase_by_phase():
    """
    Example 3: Phase-by-phase execution with review points
    
    Demonstrates executing each phase separately with manual review.
    """
    print("\n" + "="*70)
    print("EXAMPLE 3: Phase-by-Phase Execution")
    print("="*70 + "\n")
    
    try:
        orchestrator = SpecOrchestrator("document/co-pilot", "github_copilot")
        await orchestrator.start()
        
        # Phase 1: Load context
        print("\n📚 Phase 1: Loading Context")
        await orchestrator.load_context()
        input("\nPress Enter to continue to Plan generation...")
        
        # Phase 2: Generate plan
        print("\n📋 Phase 2: Generating Plan")
        plan = await orchestrator.generate_plan(
            tech_stack="Python FastAPI with PostgreSQL and Redis"
        )
        print(f"\nPlan preview (first 200 chars):\n{plan[:200]}...")
        input("\nPress Enter to continue to Tasks generation...")
        
        # Phase 3: Generate tasks
        print("\n✅ Phase 3: Generating Tasks")
        tasks = await orchestrator.generate_tasks()
        
        # Count tasks
        task_count = tasks.count('- [ ] T')
        print(f"\nGenerated {task_count} tasks")
        input("\nPress Enter to continue to Implementation...")
        
        # Phase 4: Execute implementation
        print("\n🔨 Phase 4: Executing Implementation")
        print("(This will take several minutes...)")
        
        implementation = await orchestrator.execute_implementation()
        
        print(f"\n✓ Implementation complete!")
        print(f"  Generated {implementation['file_count']} files")
        
        await orchestrator.stop()
        
    except Exception as e:
        print(f"\n✗ Error: {e}")


async def example_4_plan_only():
    """
    Example 4: Generate plan only
    
    Useful for reviewing architecture before proceeding.
    """
    print("\n" + "="*70)
    print("EXAMPLE 4: Generate Plan Only")
    print("="*70 + "\n")
    
    try:
        async with SpecOrchestrator("document/co-pilot") as orchestrator:
            await orchestrator.load_context()
            
            plan = await orchestrator.generate_plan(
                tech_stack="""
                Go with Gin framework
                MongoDB database
                GraphQL API
                Docker and Kubernetes
                """
            )
            
            print("\n✓ Plan generated!")
            print(f"  Length: {len(plan)} characters")
            print(f"  Saved to: document/co-pilot/plan.md")
            
    except Exception as e:
        print(f"\n✗ Error: {e}")


async def example_5_validate_workflow():
    """
    Example 5: Validate generated artifacts
    
    Demonstrates using the validator to check workflow outputs.
    """
    print("\n" + "="*70)
    print("EXAMPLE 5: Validate Workflow Artifacts")
    print("="*70 + "\n")
    
    # Validate document/co-pilot outputs
    print("Validating document/co-pilot workflow...")
    results = validate_workflow(Path("document/co-pilot"))
    
    print(f"\nValidation Results:")
    print(f"  Overall Valid: {results['overall_valid']}")
    
    if results['constitution']['exists']:
        print(f"  ✓ Constitution found ({results['constitution']['principles_count']} principles)")
    else:
        print(f"  ✗ Constitution missing")
    
    if results['spec']['exists']:
        print(f"  ✓ Specification found")
    else:
        print(f"  ✗ Specification missing")
    
    if results['plan'] and results['plan']['exists']:
        print(f"  ✓ Plan generated")
        sections = results['plan']['sections']
        valid_sections = sum(1 for v in sections.values() if v)
        print(f"    - {valid_sections}/{len(sections)} required sections present")
    else:
        print(f"  ✗ Plan not generated")
    
    if results['tasks'] and results['tasks']['exists']:
        print(f"  ✓ Tasks generated")
        task_format = results['tasks']['format']
        print(f"    - {task_format['total_tasks']} total tasks")
        print(f"    - {task_format['tasks_with_ids']} with IDs")
        print(f"    - {task_format['parallel_tasks']} parallelizable")
        
        if task_format['errors']:
            print(f"    ⚠ {len(task_format['errors'])} errors found")
            for error in task_format['errors'][:3]:
                print(f"      - {error}")
    else:
        print(f"  ✗ Tasks not generated")
    
    if results['implementation'] and results['implementation']['exists']:
        print(f"  ✓ Implementation generated")
        code_blocks = results['implementation']['code_blocks']
        print(f"    - {code_blocks['total_code_blocks']} code blocks")
        print(f"    - {code_blocks['blocks_with_file_paths']} with file paths")
        print(f"    - Languages: {', '.join(code_blocks['languages_found'])}")
    else:
        print(f"  ✗ Implementation not generated")


async def example_6_compare_agents():
    """
    Example 6: Compare outputs from both agents
    
    Run same spec through both Claude and Copilot for comparison.
    """
    print("\n" + "="*70)
    print("EXAMPLE 6: Compare Claude vs GitHub Copilot")
    print("="*70 + "\n")
    
    tech_stack = """
    Python with Flask
    SQLite database
    Simple REST API
    Minimal dependencies
    """
    
    # Note: This example requires identical constitution.md and spec.md
    # in both document/co-pilot/ and document/anthropic/ directories
    
    print("This example would generate plans using both agents.")
    print("Requires identical specs in both document/co-pilot/ and document/anthropic/ directories.")
    print("\nTo run:")
    print("1. Copy constitution.md and spec.md to both directories")
    print("2. Run full workflow for each agent")
    print("3. Compare the outputs (.md files will be in the same directory as spec.md)")


async def example_7_custom_tech_stack():
    """
    Example 7: Custom/unusual tech stack
    
    Demonstrates flexibility with different technology choices.
    """
    print("\n" + "="*70)
    print("EXAMPLE 7: Custom Tech Stack")
    print("="*70 + "\n")
    
    try:
        async with SpecOrchestrator("document/co-pilot") as orchestrator:
            await orchestrator.load_context()
            
            # Generate plan with unusual tech stack
            plan = await orchestrator.generate_plan(
                tech_stack="""
                Rust with Actix-web framework
                PostgreSQL with Diesel ORM
                Redis for session management
                GraphQL API using async-graphql
                WebAssembly for frontend
                Docker multi-stage builds
                Kubernetes deployment
                Prometheus monitoring
                """
            )
            
            print("\n✓ Plan generated for custom stack!")
            
    except Exception as e:
        print(f"\n✗ Error: {e}")


async def main():
    """
    Main function to run examples.
    
    Uncomment the example you want to run.
    """
    print("\n" + "="*70)
    print("SPEC-DRIVEN DEVELOPMENT WORKFLOW EXAMPLES")
    print("="*70)
    
    # Choose which example to run
    print("\nAvailable Examples:")
    print("1. Full workflow with GitHub Copilot")
    print("2. Full workflow with Claude")
    print("3. Phase-by-phase execution with reviews")
    print("4. Generate plan only")
    print("5. Validate workflow artifacts")
    print("6. Compare agents (info only)")
    print("7. Custom tech stack")
    
    print("\nNote: Examples require constitution.md and spec.md in respective directories")
    print("      (document/co-pilot/ for GitHub Copilot, document/anthropic/ for Claude)")
    
    choice = input("\nEnter example number to run (1-7), or 'all' for validation only: ").strip()
    
    if choice == '1':
        await example_1_full_workflow_copilot()
    elif choice == '2':
        await example_2_full_workflow_claude()
    elif choice == '3':
        await example_3_phase_by_phase()
    elif choice == '4':
        await example_4_plan_only()
    elif choice == '5':
        await example_5_validate_workflow()
    elif choice == '6':
        await example_6_compare_agents()
    elif choice == '7':
        await example_7_custom_tech_stack()
    elif choice.lower() == 'all':
        await example_5_validate_workflow()
    else:
        print("\nInvalid choice. Running validation example...")
        await example_5_validate_workflow()
    
    print("\n" + "="*70)
    print("EXAMPLES COMPLETE")
    print("="*70 + "\n")


if __name__ == "__main__":
    # Run the examples
    asyncio.run(main())
