"""
Example usage of the Code Generator
"""

import asyncio
from code_generator import CodeGenerator


async def example_basic_generation():
    """Example: Basic code generation"""
    print("=== Basic Code Generation ===")
    
    async with CodeGenerator() as generator:
        print(f"Using Agent: {generator.agent_type.upper()}\n")
        
        prompt = "Create a function to calculate the factorial of a number. Always right the output to  folder named outputs"
        result = await generator.generate(prompt)
        
        print(f"Prompt: {prompt}\n")
        print(f"Generated Code:\n{result}\n")


async def example_generate_function():
    """Example: Generate a specific function"""
    print("=== Generate Function ===")
    
    async with CodeGenerator() as generator:
        print(f"Using Agent: {generator.agent_type.upper()}\n")
        
        result = await generator.generate_function(
            function_name="validate_email",
            description="validates an email address using regex.Always right the output to  folder named outputs",
            language="python"
        )
        
        print(f"Generated Function:\n{result}\n")


async def example_generate_class():
    """Example: Generate a class"""
    print("=== Generate Class ===\n")
    
    async with CodeGenerator() as generator:
        print(f"Using Agent: {generator.agent_type.upper()}\n")
        
        result = await generator.generate_class(
            class_name="BankAccount",
            description="manages a bank account with deposits and withdrawals. Always right the output to  folder named outputs",
            methods=[
                "deposit(amount) - adds money to the account",
                "withdraw(amount) - removes money from the account",
                "get_balance() - returns the current balance"
            ],
            language="python"
        )
        
        print(f"Generated Class:\n{result}\n")


async def example_with_custom_model():
    """Example: Using a specific model with explicit agent type"""
    print("=== Custom Model (Claude Opus) ===\n")
    
    # Explicitly use Claude Agent with opus model
    async with CodeGenerator(model="opus", agent_type="claude") as generator:
        print(f"Using Agent: {generator.agent_type.upper()} with model: opus\n")
        
        result = await generator.generate(
            "Create a Python decorator that measures function execution time. Always right the output to  folder named outputs"
        )
        
        print(f"Generated Code:\n{result}\n")


async def example_with_context_manager():
    """Example: Using async context manager for automatic cleanup"""
    print("=== Using Async Context Manager ===\n")
    
    # Using async with - automatic resource management
    async with CodeGenerator(agent_type="claude", model="sonnet") as generator:
        print(f"Using Agent: {generator.agent_type.upper()} with context manager\n")
        
        result = await generator.generate(
            "Create a simple Python function to check if a number is prime"
        )
        
        print(f"Generated Code:\n{result}\n")
    # No need to call close() - it's automatically handled!
    print("Resources automatically cleaned up!")


async def main():
    """Run all examples"""
    try:
        await example_basic_generation()
        print("\n" + "="*70 + "\n")
        
        await example_generate_function()
        print("\n" + "="*70 + "\n")
        
        await example_generate_class()
        print("\n" + "="*70 + "\n")
        
        await example_with_custom_model()
        print("\n" + "="*70 + "\n")
        
        await example_with_context_manager()
        
    except Exception as e:
        print(f"Error: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    asyncio.run(main())
