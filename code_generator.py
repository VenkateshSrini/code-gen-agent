"""
Code Generator Module
Provides utilities for generating code using Claude Agent or GitHub Copilot Agent
"""

import os
from typing import Optional, Union
from dotenv import load_dotenv
from agent_framework_github_copilot import GitHubCopilotAgent
from agent_framework_claude import ClaudeAgent


class CodeGenerator:
    """A class to handle code generation using Claude Agent or GitHub Copilot Agent."""
    
    def __init__(self, model: Optional[str] = None, instructions: Optional[str] = None, agent_type: Optional[str] = None):
        """
        Initialize the Code Generator.
        
        Args:
            model: Model to use (e.g., "gpt-4o", "claude-sonnet-4", "sonnet", "opus", "haiku", "o1")
            instructions: Custom system instructions for the agent
            agent_type: Agent type to use ("claude" or "github_copilot"). If None, reads from AGENT_TYPE env var
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

You generate clean, well-documented, and idiomatic code based on requirements.
You follow well-defined design patterns and ensure code has no syntax errors, 
performance issues, security vulnerabilities, or memory leaks.
"""
        
        final_instructions = instructions or default_instructions
        
        if self.agent_type == "claude":
            # Initialize Claude Agent
            self.agent = ClaudeAgent(
                instructions=final_instructions,
                default_options={
                    "model": model or os.getenv("CLAUDE_MODEL", "sonnet"),
                    "permission_mode": "default",
                    "max_turns": 50
                }
            )
        else:
            # Initialize GitHub Copilot Agent (default)
            self.agent = GitHubCopilotAgent(
                name="CodeGenerator",
                description="An AI agent for generating and refactoring code",
                default_options={
                    "instructions": final_instructions,
                    "model": model or os.getenv("GITHUB_COPILOT_MODEL", "gpt-5.2-codex"),
                    "timeout": 300.0
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
