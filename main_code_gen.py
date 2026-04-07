import os
import asyncio
from dotenv import load_dotenv
from code_generator import CodeGenerator

# Load environment variables
load_dotenv(override=True)


async def main():
    """Main function to run the code generation agent."""
    agent_type = os.getenv("AGENT_TYPE", "github_copilot").lower()
    
    print("Code Generator Agent")
    print("=" * 50)
    print(f"\nAgent Type: {agent_type.upper()}")
    
    if agent_type == "claude":
        model = os.getenv("CLAUDE_MODEL", "sonnet")
        print(f"Using model: {model}")
        print("\nTip: Set AGENT_TYPE=claude and CLAUDE_MODEL in .env")
        print("     Available models: sonnet, opus, haiku")
    else:
        model = os.getenv("GITHUB_COPILOT_MODEL", "gpt-5.2")
        print(f"Using model: {model}")
        print("\nTip: Set AGENT_TYPE=github_copilot and GITHUB_COPILOT_MODEL in .env")
        print("     Available models: gpt-5.2, gpt-4o, claude-sonnet-4, o1, etc.")
    
    print()
    
    # Initialize the code generator with async context manager
    async with CodeGenerator() as generator:
        # Interactive mode
        while True:
            print("\nEnter your code generation prompt (or 'quit' to exit):")
            prompt = input("> ").strip()
            
            if prompt.lower() in ['quit', 'exit', 'q']:
                print("Goodbye!")
                break
            
            if not prompt:
                print("Please enter a valid prompt.")
                continue
            
            try:
                print("\nGenerating code...")
                result = await generator.generate(prompt)
                print("\nGenerated Response:")
                print("-" * 50)
                print(result)
                print("-" * 50)
            except Exception as e:
                print(f"\nError: {e}")
                import traceback
                traceback.print_exc()
        # Resources automatically cleaned up!


if __name__ == "__main__":
    asyncio.run(main())