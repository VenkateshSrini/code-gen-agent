# AI Code Generator

A Python-based code generation agent powered by either Claude Agent or GitHub Copilot Agent using the Microsoft Agent Framework.

## Features

- **Dual Agent Support**: Choose between Claude Agent or GitHub Copilot Agent
- **Interactive Code Generation**: Generate code from natural language prompts
- **Multiple Model Support**: Use Claude (Sonnet, Opus, Haiku), GPT-4o, GPT-5.2, O1, and other models
- **Async Context Manager**: Automatic resource management with `async with`
- **Function Generation**: Create functions with specific names and descriptions
- **Class Generation**: Generate complete classes with methods
- **Code Refactoring**: Refactor existing code with AI assistance
- **Documentation**: Automatically add documentation to your code
- **Code Fixing**: Fix errors in existing code
- **System Prompt Customization**: Customize the agent's behavior with custom instructions

## Setup

1. **Install dependencies:**
```bash
pip install -r requirements.txt
```

2. **Configure Agent Settings:**

Create a `.env` file to configure which agent to use:

```env
# Agent Selection (claude or github_copilot)
AGENT_TYPE=github_copilot

# Claude Agent Settings
ANTHROPIC_API_KEY=your-anthropic-api-key-here
CLAUDE_MODEL=sonnet  # Options: sonnet, opus, haiku
CLAUDE_AGENT_PERMISSION_MODE=default
CLAUDE_AGENT_MAX_TURNS=50

# GitHub Copilot Agent Settings
GITHUB_COPILOT_MODEL=gpt-5.2-codex  # Options: gpt-5.2, gpt-4o, claude-sonnet-4, o1
GITHUB_COPILOT_TIMEOUT=60
```

**Authentication:**
- **Claude Agent**: Requires `ANTHROPIC_API_KEY` in your `.env` file
- **GitHub Copilot Agent**: Uses GitHub Copilot CLI (handles authentication automatically)

## Available Models

### Claude Agent
- `sonnet` (default, fast and balanced)
- `opus` (most capable)
- `haiku` (fastest)

### GitHub Copilot Agent
- `gpt-5.2-codex` (default)
- `gpt-4o`
- `claude-sonnet-4`
- `o1`
- And other models supported by GitHub Copilot

## Usage

### Interactive Mode

Run the main script for an interactive code generation session:

```bash
python main.py
```

Then enter your prompts:
```
> Create a function to sort a list of dictionaries by a specific key
```

### Using the CodeGenerator Module

#### With Async Context Manager (Recommended)

```python
import asyncio
from code_generator import CodeGenerator

async def main():
    # Automatic resource management with async with
    async with CodeGenerator(agent_type="claude", model="sonnet") as generator:
        code = await generator.generate_function(
            function_name="calculate_average",
            description="calculates the average of a list of numbers"
        )
        print(code)
    # Resources automatically cleaned up!

asyncio.run(main())
```

#### Traditional Try/Finally Pattern

```python
import asyncio
from code_generator import CodeGenerator

async def main():
    generator = CodeGenerator(agent_type="github_copilot", model="gpt-4o")
    
    try:
        code = await generator.generate_function(
            function_name="calculate_average",
            description="calculates the average of a list of numbers"
        )
        print(code)
    finally:
        await generator.close()  # Clean up resources

asyncio.run(main())
```

### Selecting Agent Type

```python
# Use Claude Agent with opus model
generator = CodeGenerator(agent_type="claude", model="opus")

# Use GitHub Copilot Agent with specific model
generator = CodeGenerator(agent_type="github_copilot", model="gpt-4o")

# Use environment variable (AGENT_TYPE in .env)
generator = CodeGenerator()  # Reads from .env
```

### Custom System Instructions

```python
async with CodeGenerator(
    agent_type="claude",
    model="sonnet",
    instructions="You are a Python expert. Always use type hints and write comprehensive docstrings."
) as generator:
    code = await generator.generate("Create a function to validate email addresses")
    print(code)
```

### Examples

Run the examples to see various use cases:

```bash
python examples.py
```

## Available Methods

### `generate(prompt, context=None)`
Generate code from a natural language prompt.

```python
code = await generator.generate(
    \"Create a REST API endpoint for user authentication\",
    context=\"Using FastAPI framework\"
)
```

### `generate_function(function_name, description, language='python')`
Generate a specific function with the given name and description.

### `generate_class(class_name, description, methods=None, language='python')`
Generate a class with specified methods.

### `refactor_code(code, instructions)`
Refactor existing code based on instructions.

### `add_documentation(code)`
Add comprehensive documentation to existing code.

### `fix_code(code, error_message=None)`
Fix errors in code with optional error message context.

## API Reference

### GitHubCopilotAgent

The underlying agent supports these options:

- **instructions**: System instructions for the agent
- **name**: Agent name
- **description**: Agent description
- **default_options**:
  - `model`: Model to use (e.g., \"gpt-4o\", \"claude-sonnet-4\")
  - `timeout`: Request timeout in seconds
  - `system_message`: System message configuration with `mode` (\"append\" or \"replace\") and `content`
  - `cli_path`: Path to Copilot CLI executable
  - `log_level`: CLI log level
  - `on_permission_request`: Permission request handler
  - `mcp_servers`: MCP server configurations
- **tools**: Custom tools for the agent
- **context_provider**: Context provider for the agent
- **middleware**: Agent middleware

## Project Structure

```
code-gen-agent/
├── main.py              # Interactive CLI application
├── code_generator.py    # Core CodeGenerator class
├── examples.py          # Usage examples
├── requirements.txt     # Python dependencies
├── .env                 # Environment variables (optional)
└── README.md           # This file
```

## Requirements

- Python 3.8+
- GitHub Copilot CLI access
- Internet connection for API calls

## License

MIT
