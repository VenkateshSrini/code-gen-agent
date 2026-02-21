"""Test plan generation with BOTH Claude and GitHub Copilot agents."""
import asyncio
import os
from pathlib import Path
from code_generator import CodeGenerator
from spec_templates import get_plan_prompt

async def test_agent(agent_type: str, output_file: Path):
    """Test plan generation with specific agent."""
    print(f"\n{'='*70}")
    print(f"Testing {agent_type.upper()} Agent")
    print(f"{'='*70}")
    
    # Read spec files
    base_dir = Path("co-pilot")
    constitution = (base_dir / "constitution.md").read_text(encoding='utf-8')
    spec = (base_dir / "spec.md").read_text(encoding='utf-8')
    
    print(f"✓ Loaded constitution ({len(constitution)} chars)")
    print(f"✓ Loaded spec ({len(spec)} chars)")
    
    # Generate prompt
    prompt = get_plan_prompt(constitution, spec, "Python 3.14")
    print(f"✓ Generated prompt ({len(prompt)} chars)\n")
    
    print("Generating plan...")
    
    try:
        async with CodeGenerator(agent_type=agent_type) as generator:
            plan = await generator.generate(prompt)
            
            print(f"\n✓ Generated plan: {len(plan)} chars")
            
            # Count lines
            line_count = plan.count('\n') + 1
            print(f"✓ Line count: {line_count}")
            
            # Save to file
            output_file.write_text(plan, encoding='utf-8')
            print(f"✓ Saved to: {output_file}")
            
            # Show preview
            print(f"\nFirst 500 chars:")
            print(plan[:500])
            print("\n...")
            
            if len(plan) > 1000:
                print(f"\nLast 300 chars:")
                print(plan[-300:])
            
            return {
                'agent': agent_type,
                'chars': len(plan),
                'lines': line_count,
                'file': str(output_file)
            }
            
    except Exception as e:
        print(f"\n✗ Error: {e}")
        import traceback
        traceback.print_exc()
        return {
            'agent': agent_type,
            'error': str(e)
        }

async def main():
    """Test both agents."""
    print("="*70)
    print("TESTING BOTH AGENTS: CLAUDE AND GITHUB COPILOT")
    print("="*70)
    
    results = []
    
    # # Test Claude
    # claude_result = await test_agent("claude", Path("co-pilot/plan_claude.md"))
    # results.append(claude_result)
    
    # # Give a moment between tests
    # await asyncio.sleep(2)
    
    # Test GitHub Copilot
    copilot_result = await test_agent("github_copilot", Path("co-pilot/plan_copilot.md"))
    results.append(copilot_result)
    
    # Summary
    print(f"\n\n{'='*70}")
    print("COMPARISON SUMMARY")
    print(f"{'='*70}\n")
    
    for result in results:
        if 'error' in result:
            print(f"{result['agent'].upper()}: ERROR - {result['error']}")
        else:
            print(f"{result['agent'].upper()}:")
            print(f"  File: {result['file']}")
            print(f"  Size: {result['chars']} chars, {result['lines']} lines")
            print()
    
    print(f"{'='*70}")

if __name__ == "__main__":
    asyncio.run(main())
