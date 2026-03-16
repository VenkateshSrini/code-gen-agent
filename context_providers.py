"""
Context Providers for Code Generator Agent Skills
Injects speckit command file content into the agent context before each run.

Two concrete providers are available:
  - AnthropicCommandProvider — reads from anthropic/command/speckit.{skill}.md
  - CopilotCommandProvider   — reads from co-pilot/command/speckit.{skill}.agent.md

Usage:
    from context_providers import AnthropicCommandProvider, CopilotCommandProvider

    # For Claude agent
    provider = AnthropicCommandProvider()
    gen = CodeGenerator(agent_type="claude", context_provider=provider)

    # For GitHub Copilot agent
    provider = CopilotCommandProvider()
    gen = CodeGenerator(agent_type="github_copilot", context_provider=provider)

    # Call a dedicated wrapper method — the provider auto-loads the right file
    result = await gen.generate_plan("build a REST API for user management")
"""

import logging
import re
from pathlib import Path
from typing import Any, Optional

from agent_framework import BaseContextProvider, SessionContext, AgentSession, SupportsAgentRun

logger = logging.getLogger(__name__)


def _strip_frontmatter(content: str) -> str:
    """Remove YAML frontmatter block (---...---) from start of file, if present."""
    if content.startswith('---'):
        match = re.match(r'^---\n.*?\n---\n\n?', content, re.DOTALL)
        if match:
            return content[match.end():]
    return content

_BASE_DIR = Path(__file__).parent

# ---------------------------------------------------------------------------
# Supported skill names and their corresponding file-name fragment
# (the part between "speckit." and the extension / ".agent.md")
# ---------------------------------------------------------------------------
SUPPORTED_SKILLS = (
    "plan",
    "tasks",
    "specify",
    "implement",
    "analyze",
    "clarify",
    "constitution",
    "checklist",
    "taskstoissues",
)


class AnthropicCommandProvider(BaseContextProvider):
    """
    Context provider that loads Anthropic/Claude speckit command files.

    File pattern: anthropic/command/speckit.{skill}.md

    Set ``current_skill`` to one of the SUPPORTED_SKILLS values before
    invoking the agent.  The provider reads the corresponding file and
    injects its content as additional instructions.  ``current_skill`` is
    reset to ``None`` after injection so the skill is scoped to a single run.
    """

    def __init__(self) -> None:
        super().__init__(source_id="anthropic-command")
        self.current_skill: Optional[str] = None
        self._command_dir = _BASE_DIR / "anthropic" / "command"

    def _resolve_path(self, skill: str) -> Path:
        return self._command_dir / f"speckit.{skill}.md"

    def load_skill(self, skill: str) -> Optional[str]:
        """
        Read and return the command file content for the given skill.

        Returns the file content as a string, or None if the file is missing.
        Prints a console message so skill injection is always visible.
        """
        skill_path = self._resolve_path(skill)
        if not skill_path.exists():
            print(
                f"[AnthropicCommandProvider] WARNING: skill file not found, "
                f"skipping injection: {skill_path}"
            )
            logger.warning(
                "[AnthropicCommandProvider] Skill file not found, skipping injection: %s",
                skill_path,
            )
            return None
        content = skill_path.read_text(encoding="utf-8")
        content = _strip_frontmatter(content)
        print(f"[AnthropicCommandProvider] Injected skill '{skill}' from: {skill_path}")
        logger.debug(
            "[AnthropicCommandProvider] Injected skill '%s' from: %s",
            skill,
            skill_path,
        )
        return content

    async def before_run(
        self,
        *,
        agent: SupportsAgentRun,
        session: AgentSession,
        context: SessionContext,
        state: dict[str, Any],
    ) -> None:
        # Fallback: called by the framework if/when it starts invoking
        # context providers in its pipeline.  Direct injection via
        # load_skill() in _generate_with_skill() is the primary path.
        skill = self.current_skill
        self.current_skill = None
        if skill is None:
            return
        content = self.load_skill(skill)
        if content is not None:
            context.extend_instructions(self.source_id, content)


class CopilotCommandProvider(BaseContextProvider):
    """
    Context provider that loads GitHub Copilot speckit command files.

    File pattern: co-pilot/command/speckit.{skill}.agent.md

    Set ``current_skill`` to one of the SUPPORTED_SKILLS values before
    invoking the agent.  The provider reads the corresponding file and
    injects its content as additional instructions.  ``current_skill`` is
    reset to ``None`` after injection so the skill is scoped to a single run.
    """

    def __init__(self) -> None:
        super().__init__(source_id="copilot-command")
        self.current_skill: Optional[str] = None
        self._command_dir = _BASE_DIR / "co-pilot" / "command"

    def _resolve_path(self, skill: str) -> Path:
        return self._command_dir / f"speckit.{skill}.agent.md"

    def load_skill(self, skill: str) -> Optional[str]:
        """
        Read and return the command file content for the given skill.

        Returns the file content as a string, or None if the file is missing.
        Prints a console message so skill injection is always visible.
        """
        skill_path = self._resolve_path(skill)
        if not skill_path.exists():
            print(
                f"[CopilotCommandProvider] WARNING: skill file not found, "
                f"skipping injection: {skill_path}"
            )
            logger.warning(
                "[CopilotCommandProvider] Skill file not found, skipping injection: %s",
                skill_path,
            )
            return None
        content = skill_path.read_text(encoding="utf-8")
        content = _strip_frontmatter(content)
        print(f"[CopilotCommandProvider] Injected skill '{skill}' from: {skill_path}")
        logger.debug(
            "[CopilotCommandProvider] Injected skill '%s' from: %s",
            skill,
            skill_path,
        )
        return content

    async def before_run(
        self,
        *,
        agent: SupportsAgentRun,
        session: AgentSession,
        context: SessionContext,
        state: dict[str, Any],
    ) -> None:
        # Fallback: called by the framework if/when it starts invoking
        # context providers in its pipeline.  Direct injection via
        # load_skill() in _generate_with_skill() is the primary path.
        skill = self.current_skill
        self.current_skill = None
        if skill is None:
            return
        content = self.load_skill(skill)
        if content is not None:
            context.extend_instructions(self.source_id, content)
