# AI Code Generator

AI-powered code generation system using **Microsoft Agent Framework** with support for GitHub Copilot and Claude agents.

## 🚀 Quick Start

```bash
# Install dependencies
pip install -r requirements.txt

# Interactive code generation
python main.py

# Spec-driven development workflow
python workflow_example.py ./document/co-pilot github_copilot "Python 3.10+"
```

## 📖 Documentation

**For complete documentation, see:**  
👉 **[Complete Guide](document/COMPLETE_GUIDE.md)** 👈

The comprehensive guide includes:

- **Setup & Installation** - Environment configuration, dependencies
- **Code Generator** - Interactive code generation API
- **Spec-Driven Development** - Automated workflow from spec to implementation
- **Microsoft Agent Framework** - Workflow orchestration with human approval
- **Architecture** - System components and data flow
- **API Reference** - Complete API documentation
- **Examples** - Usage patterns and code samples
- **Best Practices** - Writing constitutions and specifications
- **Troubleshooting** - Common issues and solutions
- **Advanced Usage** - Custom templates, CI/CD integration

## ✨ Features

- ✅ **Dual Agent Support**: GitHub Copilot or Claude
- ✅ **Multiple Models**: GPT-5.2, GPT-4o, O1, Claude Sonnet/Opus/Haiku
- ✅ **Spec-Driven Workflow**: Constitution → Spec → Plan → Tasks → Implementation
- ✅ **Human-in-the-Loop**: Approval gates at critical workflow steps
- ✅ **Microsoft Agent Framework**: Production-ready workflow orchestration
- ✅ **TDD Integration**: Test-first development by default
- ✅ **Validation System**: Comprehensive artifact validation

## 📂 Project Structure

```
code-gen-agent/
├── code_generator.py           # Agent wrapper (GitHub Copilot/Claude)
├── spec_orchestrator.py        # Workflow orchestration
├── spec_workflow.py            # Framework workflows with HITL
├── spec_templates.py           # Prompt templates
├── spec_validator.py           # Validation utilities
├── workflow_example.py         # Usage examples
├── main.py                     # Interactive code generation
├── requirements.txt            # Python dependencies
│
├── document/
│   ├── COMPLETE_GUIDE.md       # 📖 COMPREHENSIVE DOCUMENTATION
│   │
│   ├── co-pilot/               # GitHub Copilot workspace
│   │   ├── constitution.md     # Project principles
│   │   ├── spec.md             # Requirements
│   │   └── outputs/            # Generated artifacts
│   │
│   └── anthropic/              # Claude workspace
│       ├── constitution.md
│       ├── spec.md
│       └── outputs/
│
└── examples.py                 # Example usage patterns
```

## 🎯 Usage Examples

### Interactive Code Generation

```python
import asyncio
from code_generator import CodeGenerator

async def main():
    async with CodeGenerator(agent_type="github_copilot") as gen:
        code = await gen.generate("Create a REST API endpoint for user login")
        print(code)

asyncio.run(main())
```

### Spec-Driven Development

```python
from spec_orchestrator import SpecOrchestrator

async def main():
    async with SpecOrchestrator("document/co-pilot") as orch:
        result = await orch.run_full_workflow(
            tech_stack="Python 3.10+ with FastAPI"
        )
        print(f"Generated {result['file_count']} files")

asyncio.run(main())
```

### With Human Approval

```bash
python workflow_example.py ./document/co-pilot github_copilot "Python 3.10+"
```

The workflow pauses for your approval after generating tasks.

## ⚙️ Configuration

Create a `.env` file:

```env
# Agent Selection
AGENT_TYPE=github_copilot  # or "claude"

# Claude Configuration
ANTHROPIC_API_KEY=your-api-key
CLAUDE_MODEL=sonnet

# GitHub Copilot Configuration
GITHUB_COPILOT_MODEL=gpt-5.2-codex
```

## 📚 Learn More

- [Complete Guide](document/COMPLETE_GUIDE.md) - Comprehensive documentation
- [Microsoft Agent Framework](https://learn.microsoft.com/en-us/agent-framework/) - Framework documentation
- [GitHub Copilot](https://github.com/features/copilot) - AI code assistance
- [Anthropic Claude](https://www.anthropic.com/claude) - AI assistant

## 🤝 Contributing

Contributions are welcome! Please see the [Complete Guide](document/COMPLETE_GUIDE.md) for architecture details.

## 📝 License

[Your License Here]

---

**For detailed documentation, troubleshooting, and advanced usage, see the [Complete Guide](document/COMPLETE_GUIDE.md).**
