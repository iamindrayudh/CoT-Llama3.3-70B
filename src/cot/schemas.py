"""
This module contains schema definitions for chain of thought reasoning.
"""

# JSON schema for structured reasoning steps
REASONING_SCHEMA = {
    "type": "json_object",
    "schema": {
        "type": "object",
        "properties": {
            "reasoning_steps": {
                "type": "array",
                "items": {
                    "type": "object",
                    "properties": {
                        "title": {"type": "string"},
                        "content": {"type": "string"},
                        "next_action": {"type": "string", "enum": ["continue", "final_answer"]}
                    },
                    "required": ["title", "content", "next_action"]
                }
            },
            "final_answer": {"type": "string"}
        },
        "required": ["reasoning_steps", "final_answer"]
    }
}

# Tool definitions
CALCULATOR_TOOL = {
    "type": "function",
    "function": {
        "name": "calculate",
        "description": "Evaluate a mathematical expression",
        "parameters": {
            "type": "object",
            "properties": {
                "expression": {
                    "type": "string",
                    "description": "The mathematical expression to evaluate"
                }
            },
            "required": ["expression"]
        }
    }
}

# List of available tools
AVAILABLE_TOOLS = [
    CALCULATOR_TOOL
]
