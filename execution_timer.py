"""
Execution Timer Decorator Module

This module provides a decorator for measuring function execution time.
"""

import time
import functools
from typing import Callable, Any


def execution_timer(func: Callable) -> Callable:
    """
    A decorator that measures and prints the execution time of a function.
    
    Args:
        func: The function to be timed
        
    Returns:
        The wrapped function with timing capability
        
    Example:
        @execution_timer
        def slow_function():
            time.sleep(1)
            return "Done"
            
        result = slow_function()  # Will print: slow_function executed in 1.001s
    """
    @functools.wraps(func)
    def wrapper(*args, **kwargs) -> Any:
        start_time = time.perf_counter()
        result = func(*args, **kwargs)
        end_time = time.perf_counter()
        execution_time = end_time - start_time
        print(f"{func.__name__} executed in {execution_time:.3f}s")
        return result
    return wrapper


def execution_timer_detailed(unit: str = "seconds", return_time: bool = False):
    """
    A configurable decorator that measures function execution time with options.
    
    Args:
        unit: Time unit for display ("seconds", "milliseconds", "microseconds")
        return_time: If True, returns tuple of (result, execution_time)
        
    Returns:
        Decorator function
        
    Example:
        @execution_timer_detailed(unit="milliseconds", return_time=True)
        def my_function():
            time.sleep(0.1)
            return "Done"
            
        result, exec_time = my_function()  # Will print in milliseconds
    """
    def decorator(func: Callable) -> Callable:
        @functools.wraps(func)
        def wrapper(*args, **kwargs) -> Any:
            start_time = time.perf_counter()
            result = func(*args, **kwargs)
            end_time = time.perf_counter()
            
            execution_time = end_time - start_time
            
            # Convert time based on unit
            if unit == "milliseconds":
                display_time = execution_time * 1000
                unit_suffix = "ms"
            elif unit == "microseconds":
                display_time = execution_time * 1_000_000
                unit_suffix = "μs"
            else:  # seconds
                display_time = execution_time
                unit_suffix = "s"
            
            print(f"{func.__name__} executed in {display_time:.3f}{unit_suffix}")
            
            if return_time:
                return result, execution_time
            return result
        return wrapper
    return decorator


class ExecutionTimer:
    """
    A context manager and decorator class for measuring execution time.
    
    Can be used as either a context manager or a decorator.
    """
    
    def __init__(self, name: str = "Operation", unit: str = "seconds"):
        """
        Initialize the timer.
        
        Args:
            name: Name to display in timing output
            unit: Time unit ("seconds", "milliseconds", "microseconds")
        """
        self.name = name
        self.unit = unit
        self.start_time = None
        self.execution_time = None
    
    def __enter__(self):
        """Start timing when entering context."""
        self.start_time = time.perf_counter()
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        """End timing and print result when exiting context."""
        end_time = time.perf_counter()
        self.execution_time = end_time - self.start_time
        
        # Convert time based on unit
        if self.unit == "milliseconds":
            display_time = self.execution_time * 1000
            unit_suffix = "ms"
        elif self.unit == "microseconds":
            display_time = self.execution_time * 1_000_000
            unit_suffix = "μs"
        else:  # seconds
            display_time = self.execution_time
            unit_suffix = "s"
        
        print(f"{self.name} executed in {display_time:.3f}{unit_suffix}")
    
    def __call__(self, func: Callable) -> Callable:
        """Allow class to be used as a decorator."""
        @functools.wraps(func)
        def wrapper(*args, **kwargs) -> Any:
            with ExecutionTimer(func.__name__, self.unit):
                return func(*args, **kwargs)
        return wrapper


# Example usage and demonstration functions
if __name__ == "__main__":
    # Example 1: Basic decorator
    @execution_timer
    def example_function():
        """Example function that takes some time."""
        time.sleep(0.1)
        return "Task completed"
    
    # Example 2: Detailed decorator with milliseconds
    @execution_timer_detailed(unit="milliseconds", return_time=True)
    def example_function_detailed():
        """Example function with detailed timing."""
        time.sleep(0.05)
        return "Detailed task completed"
    
    # Example 3: Context manager usage
    def example_context_manager():
        """Example using context manager."""
        with ExecutionTimer("Custom operation", "milliseconds"):
            time.sleep(0.02)
    
    # Example 4: Class decorator usage
    @ExecutionTimer("Class decorated function", "microseconds")
    def example_class_decorator():
        """Example using class as decorator."""
        time.sleep(0.001)
    
    # Run examples
    print("=== Execution Timer Examples ===\n")
    
    print("1. Basic decorator:")
    result1 = example_function()
    print(f"Result: {result1}\n")
    
    print("2. Detailed decorator with return time:")
    result2, exec_time = example_function_detailed()
    print(f"Result: {result2}, Execution time: {exec_time:.6f}s\n")
    
    print("3. Context manager:")
    example_context_manager()
    print()
    
    print("4. Class decorator:")
    example_class_decorator()