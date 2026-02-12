Here's the implementation of `baseline/calculator.py` following the specified requirements:

```python
"""
Calculator module providing basic arithmetic operations with input validation.

This module contains core calculator functions and input validation utilities
for a Streamlit-based calculator application.
"""

from typing import Union

def add(a: float, b: float) -> float:
    """Add two numbers.

    Args:
        a: First number to add
        b: Second number to add

    Returns:
        Sum of a and b
    """
    return a + b

def subtract(a: float, b: float) -> float:
    """Subtract the second number from the first.

    Args:
        a: Number to subtract from
        b: Number to subtract

    Returns:
        Result of a - b
    """
    return a - b

def multiply(a: float, b: float) -> float:
    """Multiply two numbers.

    Args:
        a: First number to multiply
        b: Second number to multiply

    Returns:
        Product of a and b
    """
    return a * b

def divide(a: float, b: float) -> Union[float, str]:
    """Divide the first number by the second.

    Args:
        a: Dividend
        b: Divisor

    Returns:
        Result of a / b if b is not zero, otherwise error message
    """
    if b == 0:
        return "Error: Division by zero"
    return a / b

def validate_input(value: str) -> Union[float, str]:
    """Convert string input to float with error handling.

    Args:
        value: String input to validate

    Returns:
        Converted float if valid, otherwise error message
    """
    try:
        return float(value)
    except ValueError:
        return "Error: Invalid number"
```

This implementation includes:
1. All required arithmetic operations with proper type hints
2. Comprehensive Google-style docstrings
3. Input validation for division by zero
4. String-to-number conversion with error handling
5. Clear variable names and simple logic
6. Union types for functions that can return either a number or error message

The module is designed to be imported and used by a Streamlit application, with all the core calculator logic separated from the UI layer.
