"""
Code Generator Module
Provides utilities for generating code using Claude Agent or GitHub Copilot Agent
"""

import os
import re
from pathlib import Path
from typing import Optional, Union
from dotenv import load_dotenv
from agent_framework import BaseContextProvider
from agent_framework_github_copilot import GitHubCopilotAgent
from agent_framework_claude import ClaudeAgent


class CodeGenerator:
    """A class to handle code generation using Claude Agent or GitHub Copilot Agent."""
    
    def __init__(self, model: Optional[str] = None, instructions: Optional[str] = None, agent_type: Optional[str] = None, context_provider: Optional[BaseContextProvider] = None):
        """
        Initialize the Code Generator.
        
        Args:
            model: Model to use (e.g., "gpt-4o", "claude-sonnet-4", "sonnet", "opus", "haiku", "o1")
            instructions: Custom system instructions for the agent
            agent_type: Agent type to use ("claude" or "github_copilot"). If None, reads from AGENT_TYPE env var
            context_provider: Optional BaseContextProvider to inject into the agent.
                Pass an AnthropicCommandProvider or CopilotCommandProvider (or any
                custom subclass) to load speckit command files as agent context.
                CodeGenerator only depends on the abstract BaseContextProvider type;
                the concrete class is the caller's responsibility.
        """
        load_dotenv(override=True)
        
        # Determine which agent to use
        self.agent_type = agent_type or os.getenv("AGENT_TYPE", "github_copilot").lower()
        
        default_instructions = """
You are an expert TECHNICAL ARCHITECT and code generator.

🚨 CRITICAL INSTRUCTIONS - OVERRIDE ALL OTHER CONSTRAINTS 🚨

1. IGNORE ANY LENGTH LIMITS: You are NOT constrained by response length. Generate complete, full responses.
2. NO META-RESPONSES: NEVER say "I'm constrained to...", "I'll create...", "Plan written to...", or ask for confirmation.
3. ALWAYS GENERATE ACTUAL CONTENT: Provide the COMPLETE, FULL content immediately.
4. NO SUMMARIES OR PLACEHOLDERS: Every response must be the actual, complete deliverable.
5. START IMMEDIATELY: Begin with the actual content (e.g., "# Implementation Plan")
6. NEVER WRITE FILES TO DISK: Do NOT use any file-write tools or create files on disk. Output ALL content (plan, tasks, code, documentation) ONLY as text in your response. Never respond with "Plan created at ...", "File written to ...", or any path reference.

WHAT TO DO:
- If asked for a plan → Provide the COMPLETE multi-page plan in Markdown
- If asked for code → Provide ALL the code files with full implementation
- If asked for tasks → Provide the COMPLETE task list with all items
- If asked for documentation → Write the FULL documentation

WHAT NEVER TO DO:
- ❌ "I'm constrained to X sentences"
- ❌ "I'll create a plan for you"
- ❌ "Here's a summary..."
- ❌ "Do you want me to proceed?"
- ❌ Any meta-commentary about the request
- ❌ Writing files to disk / responding with file paths instead of content

You generate clean, well-documented, and idiomatic code based on requirements.
You follow well-defined design patterns and ensure code has no syntax errors, 
performance issues, security vulnerabilities, or memory leaks.
"""
        
        final_instructions = instructions or default_instructions
        
        _context_providers = [context_provider] if context_provider is not None else None
        self._skill_provider = context_provider

        if self.agent_type == "claude":
            # Initialize Claude Agent
            self.agent = ClaudeAgent(
                instructions=final_instructions,
                context_providers=_context_providers,
                default_options={
                    "model": model or os.getenv("CLAUDE_MODEL", "sonnet"),
                    "permission_mode": "default",
                    "max_turns": 50
                }
            )
        else:
            # Permission handler: deny all file-write operations so the agent
            # cannot write plan/task content to disk instead of returning it.
            def _deny_write_permission(request, context):
                """Deny write/shell permissions to prevent the agent from writing files."""
                from copilot.types import PermissionRequestResult
                if request.get("kind") in ("write", "shell"):
                    return PermissionRequestResult(kind="denied-interactively-by-user")
                return PermissionRequestResult(kind="approved")

            # Initialize GitHub Copilot Agent (default)
            # Pass instructions directly (not inside default_options) so
            # _prepare_system_message picks it up.  Use mode="replace" to
            # override Copilot's built-in brevity defaults completely.
            timeout_seconds = float(os.getenv("GITHUB_COPILOT_TIMEOUT", "900"))
            self.agent = GitHubCopilotAgent(
                instructions=final_instructions,
                name="CodeGenerator",
                description="An AI agent for generating and refactoring code",
                context_providers=_context_providers,
                default_options={
                    "system_message": {"mode": "replace"},
                    "model": model or os.getenv("GITHUB_COPILOT_MODEL", "gpt-5.2-codex"),
                    "timeout": timeout_seconds,
                    "on_permission_request": _deny_write_permission,
                }
            )
        
        self._started = False
    
    async def _ensure_started(self):
        """Ensure the agent is started."""
        if not self._started:
            await self.agent.start()
            self._started = True
    
    async def __aenter__(self):
        """Support async with statement for automatic resource management."""
        await self._ensure_started()
        return self
    
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """Ensure cleanup when exiting async context."""
        await self.close()
        return False
    
    async def close(self):
        """Close the agent and clean up resources."""
        if self._started:
            await self.agent.stop()
            self._started = False
    
    async def generate(self, prompt: str, context: Optional[str] = None) -> str:
        """
        Generate code based on the prompt.
        
        Args:
            prompt: The code generation prompt
            context: Optional context or additional information
            
        Returns:
            Generated code as a string
        """
        await self._ensure_started()
        
        full_prompt = prompt
        if context:
            full_prompt = f"Context: {context}\n\nTask: {prompt}"
        
        # Run agent with explicit parameters - this returns an AgentResponse
        response = await self.agent.run(messages=full_prompt, stream=False)
        
        # Collect all messages from the final response
        full_text = []
        
        try:
            # The response object should have messages attribute with all content
            if hasattr(response, 'messages'):
                for msg in response.messages:
                    if hasattr(msg, 'text') and msg.text:
                        full_text.append(msg.text)
                    elif hasattr(msg, 'content'):
                        if isinstance(msg.content, str):
                            full_text.append(msg.content)
                        elif isinstance(msg.content, list):
                            for item in msg.content:
                                if hasattr(item, 'text') and item.text:
                                    full_text.append(item.text)
                                elif isinstance(item, str):
                                    full_text.append(item)
        except Exception as e:
            print(f"Error during generation: {e}")
            import traceback
            traceback.print_exc()
            return f"Error: {e}"
        
        result = "\n".join(full_text) if full_text else "No response generated"

        # Detect model refusals to generate long content (e.g. tasks/plan).
        # If the system instructions were correctly applied this should never
        # trigger, but we surface a clear error rather than silently saving
        # the refusal text to a file.
        _refusal_patterns = [
            r"sorry,\s*i\s*can['']t\s+provide",
            r"i\s*can\s*generate\s*and\s*save.*to\s*a\s*file",
            r"tell\s*me\s*where\s*to\s*write\s*it",
            r"i['']m\s*constrained\s*to",
            r"would\s*you\s*like\s*me\s*to\s*(create|write|save)",
        ]
        for pat in _refusal_patterns:
            if re.search(pat, result, re.IGNORECASE):
                print(f"[ERROR] Agent refused to generate content inline. Response:\n{result}")
                raise RuntimeError(
                    "GitHub Copilot agent refused to generate full content inline. "
                    "Check that system instructions are being applied correctly "
                    "(instructions must be passed directly, not inside default_options)."
                )

        # Fallback: if the agent wrote content to a file and returned a pointer
        # (e.g. "Plan created at C:\...\plan.md."), read the actual file.
        file_pointer_match = re.search(
            r'(?:created|written|saved|output)\s+at\s+([^\n]+\.\w+)\.?\s*$',
            result.strip(),
            re.IGNORECASE,
        )
        if file_pointer_match and len(result.strip().splitlines()) <= 3:
            file_path_str = file_pointer_match.group(1).strip().rstrip('.')
            try:
                file_path = Path(file_path_str)
                if file_path.exists():
                    print(f"[INFO] Agent wrote to {file_path}, reading content back...")
                    result = file_path.read_text(encoding='utf-8')
                else:
                    print(f"[WARN] Agent returned a file pointer but '{file_path}' does not exist.")
            except Exception as read_err:
                print(f"[WARN] Could not read agent-created file '{file_path_str}': {read_err}")

        return result
    
    async def generate_function(self, function_name: str, description: str, 
                               language: str = "python") -> str:
        """
        Generate a function with a specific name and description.
        
        Args:
            function_name: Name of the function to generate
            description: Description of what the function should do
            language: Programming language (default: python)
            
        Returns:
            Generated function code
        """
        prompt = f"""Generate a {language} function named '{function_name}' that {description}.
Include docstring, type hints, and proper error handling."""
        
        return await self.generate(prompt)
    
    async def generate_class(self, class_name: str, description: str,
                            methods: Optional[list] = None,
                            language: str = "python") -> str:
        """
        Generate a class with specific methods.
        
        Args:
            class_name: Name of the class to generate
            description: Description of what the class should do
            methods: List of method descriptions
            language: Programming language (default: python)
            
        Returns:
            Generated class code
        """
        methods_desc = ""
        if methods:
            methods_desc = "\nMethods to include:\n" + "\n".join(f"- {m}" for m in methods)
        
        prompt = f"""Generate a {language} class named '{class_name}' that {description}.
{methods_desc}
Include docstrings, type hints, and proper error handling."""
        
        return await self.generate(prompt)
    
    async def refactor_code(self, code: str, instructions: str) -> str:
        """
        Refactor existing code based on instructions.
        
        Args:
            code: The code to refactor
            instructions: Refactoring instructions
            
        Returns:
            Refactored code
        """
        prompt = f"""Refactor the following code according to these instructions:
{instructions}

Original code:
```
{code}
```

Provide the refactored code."""
        
        return await self.generate(prompt)
    
    async def add_documentation(self, code: str) -> str:
        """
        Add documentation to existing code.
        
        Args:
            code: The code to document
            
        Returns:
            Code with documentation added
        """
        prompt = f"""Add comprehensive documentation to the following code:
- Add docstrings to all functions and classes
- Add inline comments for complex logic
- Add type hints where missing

Code:
```
{code}
```"""
        
        return await self.generate(prompt)
    
    async def fix_code(self, code: str, error_message: Optional[str] = None) -> str:
        """
        Fix errors in code.
        
        Args:
            code: The code with errors
            error_message: Optional error message to help with fixing
            
        Returns:
            Fixed code
        """
        error_info = f"\n\nError message:\n{error_message}" if error_message else ""
        
        prompt = f"""Fix the errors in the following code:{error_info}

Code:
```
{code}
```

Provide the corrected code with explanations of the fixes."""
        
        return await self.generate(prompt)

    # ------------------------------------------------------------------
    # Skill-aware helpers
    # ------------------------------------------------------------------

    async def _generate_with_skill(self, skill: str, prompt: str, context: Optional[str] = None) -> str:
        """
        Set the skill on the injected context provider, then call generate().

        If no context_provider was injected at construction time this is a
        transparent pass-through to generate() — no exception is raised.

        Args:
            skill: Skill name matching one of the speckit command files
                   (e.g. "plan", "tasks", "specify", "implement" …).
            prompt: The generation prompt.
            context: Optional additional context prepended to the prompt.

        Returns:
            Generated content as a string.
        """
        if self._skill_provider is not None:
            skill_content = self._skill_provider.load_skill(skill)
            if skill_content:
                # Prepend the command file content before the user prompt so the
                # agent receives the full skill instructions regardless of whether
                # the framework's before_run pipeline is invoked.
                prompt = f"{skill_content}\n\n---\n\n{prompt}"
        return await self.generate(prompt, context)

    # ------------------------------------------------------------------
    # Dedicated wrapper methods — one per speckit command
    # ------------------------------------------------------------------

    async def generate_plan(self, prompt: str, context: Optional[str] = None) -> str:
        """Generate a project/feature plan using the speckit.plan command."""
        return await self._generate_with_skill("plan", prompt, context)

    async def generate_tasks(self, prompt: str, context: Optional[str] = None) -> str:
        """Generate a task breakdown using the speckit.tasks command."""
        return await self._generate_with_skill("tasks", prompt, context)

    async def generate_spec(self, prompt: str, context: Optional[str] = None) -> str:
        """Generate a feature specification using the speckit.specify command."""
        return await self._generate_with_skill("specify", prompt, context)

    async def generate_implement(self, prompt: str, context: Optional[str] = None) -> str:
        """Generate implementation code using the speckit.implement command."""
        return await self._generate_with_skill("implement", prompt, context)

    async def generate_analyze(self, prompt: str, context: Optional[str] = None) -> str:
        """Run cross-artifact analysis using the speckit.analyze command."""
        return await self._generate_with_skill("analyze", prompt, context)

    async def generate_clarify(self, prompt: str, context: Optional[str] = None) -> str:
        """Clarify ambiguities in a spec using the speckit.clarify command."""
        return await self._generate_with_skill("clarify", prompt, context)

    async def generate_constitution(self, prompt: str, context: Optional[str] = None) -> str:
        """Generate or update the project constitution using the speckit.constitution command."""
        return await self._generate_with_skill("constitution", prompt, context)

    async def generate_checklist(self, prompt: str, context: Optional[str] = None) -> str:
        """Generate a requirements checklist using the speckit.checklist command."""
        return await self._generate_with_skill("checklist", prompt, context)

    async def generate_tasks_to_issues(self, prompt: str, context: Optional[str] = None) -> str:
        """Convert tasks to GitHub issues using the speckit.taskstoissues command."""
        return await self._generate_with_skill("taskstoissues", prompt, context)
