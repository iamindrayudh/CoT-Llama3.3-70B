"""
This module implements a calculator tool for mathematical expressions.
"""

import math
import operator
from typing import Dict, Any, Union
import re

from src.utils.logger import get_logger

logger = get_logger(__name__)

# Define safe operations
SAFE_OPERATORS = {
    '+': operator.add,
    '-': operator.sub,
    '*': operator.mul,
    '/': operator.truediv,
    '//': operator.floordiv,
    '%': operator.mod,
    '**': operator.pow,
}

SAFE_FUNCTIONS = {
    'abs': abs,
    'round': round,
    'min': min,
    'max': max,
    'sum': sum,
    'sin': math.sin,
    'cos': math.cos,
    'tan': math.tan,
    'sqrt': math.sqrt,
    'log': math.log,
    'log10': math.log10,
    'exp': math.exp,
}

def calculate(expression: str) -> Dict[str, Any]:
    """
    Safely evaluate a mathematical expression.
    
    Args:
        expression: The mathematical expression to evaluate
        
    Returns:
        Dictionary with the result or error message
    """
    try:
        logger.debug(f"Calculating expression: {expression}")
        
        # Sanitize the expression
        sanitized = sanitize_expression(expression)
        if not sanitized:
            return {"error": "Invalid or unsafe expression"}
        
        # Create a safe environment for evaluation
        safe_globals = {
            "__builtins__": {},
            **SAFE_FUNCTIONS,
            "pi": math.pi,
            "e": math.e,
        }
        
        safe_locals = {}
        
        # Evaluate the expression
        result = eval(sanitized, safe_globals, safe_locals)
        logger.debug(f"Calculation result: {result}")
        
        return {"result": result}
    
    except Exception as e:
        logger.error(f"Calculation error: {str(e)}")
        return {"error": f"Calculation error: {str(e)}"}

def sanitize_expression(expression: str) -> Union[str, None]:
    """
    Sanitize a mathematical expression to prevent code injection.
    
    Args:
        expression: The expression to sanitize
        
    Returns:
        Sanitized expression or None if invalid
    """
    # Remove any whitespace
    expression = expression.strip()
    
    # Check for any unsafe patterns
    unsafe_patterns = [
        r'import\s+',
        r'exec\s*\(',
        r'eval\s*\(',
        r'compile\s*\(',
        r'__\w+__',
        r'lambda\s+',
        r'globals\s*\(',
        r'locals\s*\(',
        r'getattr\s*\(',
        r'setattr\s*\(',
        r'delattr\s*\(',
        r'open\s*\(',
    ]
    
    for pattern in unsafe_patterns:
        if re.search(pattern, expression, re.IGNORECASE):
            return None
    
    # Only allow specific characters and patterns
    allowed_pattern = r'^[0-9\s\+\-\*\/\%\(\)\.\,\>\<\=\!\&\|\^\~]+$'
    
    # Allow safe function names
    for func in SAFE_FUNCTIONS:
        allowed_pattern = allowed_pattern[:-2] + '|' + re.escape(func) + r'\s*\(' + allowed_pattern[-2:]
    
    if not re.match(allowed_pattern, expression):
        # Check if there are any function calls that are not in our safe list
        function_calls = re.findall(r'([a-zA-Z_][a-zA-Z0-9_]*)\s*\(', expression)
        for func in function_calls:
            if func not in SAFE_FUNCTIONS:
                return None
    
    return expression
