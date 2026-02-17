"""
Simple test of the Code Generator
"""

import asyncio
from code_generator import CodeGenerator


async def simple_test():
    """Simple test to verify the code generator works"""
    print("=== Testing Code Generation ===")
    
    async with CodeGenerator() as generator:
        print(f"Using Agent: {generator.agent_type.upper()}\n")
        
        prompt = "Create a simple Python function to add two numbers with type hints and docstring"
        print(f"Prompt: {prompt}\n")
        
        result = await generator.generate(prompt)
        
        print(f"Generated Code:\n{result}\n")
        print("✓ Test completed successfully!")


if __name__ == "__main__":
    asyncio.run(simple_test())
