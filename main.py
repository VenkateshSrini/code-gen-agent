"""
Spec-Driven Development — Entry Point

Runs the full workflow:
  1. Load constitution.md + spec.md
  2. Generate: research → plan → data-model → quickstart → contracts
  3. Generate: tasks (human approval gate)
  4. Execute: implementation (file-by-file code generation)

Configuration via environment variables (or .env file):
  AGENT_TYPE          - "github_copilot" (default) or "claude"
  BASE_DIR            - project folder containing constitution.md / spec.md
                        (default: "co-pilot")
  TECH_STACK          - technology description forwarded to every prompt
                        (default: "Python 3.10+")
  GITHUB_COPILOT_MODEL / CLAUDE_MODEL  - override the LLM model if needed
"""

import os
import asyncio
from pathlib import Path
from dotenv import load_dotenv

from spec_orchestrator import SpecOrchestrator

load_dotenv(override=True)


def _banner(title: str, width: int = 70) -> None:
    print(f"\n{'='*width}")
    print(title)
    print(f"{'='*width}")


async def main() -> None:
    agent_type = os.getenv("AGENT_TYPE", "github_copilot").lower()
    base_dir   = os.getenv("BASE_DIR", "co-pilot")
    tech_stack = os.getenv("TECH_STACK", "Python 3.14")

    _banner("SPEC-DRIVEN DEVELOPMENT — FULL WORKFLOW")
    print(f"  Agent     : {agent_type}")
    print(f"  Base dir  : {base_dir}")
    print(f"  Tech stack: {tech_stack}")

    base_path = Path(base_dir)
    if not base_path.exists():
        print(f"\n[ERROR] Base directory not found: {base_path.resolve()}")
        print("  Set BASE_DIR in your .env file or environment.")
        return

    if not (base_path / "constitution.md").exists():
        print(f"\n[ERROR] Required file missing: {base_path / 'constitution.md'}")
        print("  Create constitution.md before running the workflow.")
        return

    if not (base_path / "spec.md").exists():
        print(f"\n[INFO] spec.md not found — workflow will prompt for a feature description and generate it.")

    async with SpecOrchestrator(base_dir=base_dir, agent_type=agent_type) as orchestrator:
        try:
            results = await orchestrator.run_full_workflow(tech_stack=tech_stack)
        except RuntimeError as exc:
            # Workflow cancelled by user (e.g. assumptions rejected)
            print(f"\n[CANCELLED] {exc}")
            return
        except Exception as exc:
            print(f"\n[ERROR] Workflow failed: {exc}")
            import traceback
            traceback.print_exc()
            return

    _banner("DONE")
    spec_dir = base_path / "output" / "spec"
    code_dir = base_path / "output" / "code"
    print(f"  Markdown artifacts : {spec_dir}")
    print(f"  Generated code     : {code_dir}")
    print(f"  Code files written : {results.get('file_count', 0)}")


if __name__ == "__main__":
    asyncio.run(main())
