"""
Quick test of the Code Generator examples
"""

import asyncio
from code_generator import CodeGenerator


async def test_basic_generation():
    """Test: Basic code generation"""
    print("=== Test 1: Basic Code Generation ===")
    
    async with CodeGenerator() as generator:
        print(f"Using Agent: {generator.agent_type.upper()}\n")
        
        prompt = "Create a Python function that checks if a number is even. Include docstring and type hints."
        result = await generator.generate(prompt)
        
        print(f"✓ Basic generation completed\n")


async def test_generate_function():
    """Test: Generate a specific function"""
    print("=== Test 2: Generate Function ===")
    
    async with CodeGenerator() as generator:
        print(f"Using Agent: {generator.agent_type.upper()}\n")
        
        result = await generator.generate_function(
            function_name="is_palindrome",
            description="checks if a string is a palindrome",
            language="python"
        )
        
        print(f"✓ Function generation completed\n")


async def test_generate_class():
    """Test: Generate a class"""
    print("=== Test 3: Generate Class ===\n")
    
    async with CodeGenerator() as generator:
        print(f"Using Agent: {generator.agent_type.upper()}\n")
        
        result = await generator.generate_class(
            class_name="Counter",
            description="a simple counter that can increment and decrement",
            methods=[
                "increment() - adds 1 to the counter",
                "decrement() - subtracts 1 from the counter",
                "get_value() - returns the current value"
            ],
            language="python"
        )
        
        print(f"✓ Class generation completed\n")


async def main():
    """Run all tests"""
    try:
        await test_basic_generation()
        print("="*70 + "\n")
        
        await test_generate_function()
        print("="*70 + "\n")
        
        await test_generate_class()
        print("="*70 + "\n")
        
        print("✓ All tests passed successfully!")
        
    except Exception as e:
        print(f"✗ Error: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    asyncio.run(main())
