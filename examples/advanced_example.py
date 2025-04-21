"""
Advanced example demonstrating tool use and complex reasoning.
"""

import json
import sys
import os
import argparse

# Add the project root to the Python path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from src.cot.reasoning import ChainOfThoughtReasoner
from src.utils.logger import get_logger

logger = get_logger(__name__)

def parse_args():
    parser = argparse.ArgumentParser(description="Chain of Thought Reasoning Example")
    parser.add_argument(
        "--query", 
        type=str, 
        default="Calculate the compound interest on $1000 invested for 5 years at an annual rate of 8% compounded quarterly.",
        help="The query to process"
    )
    parser.add_argument(
        "--temperature", 
        type=float, 
        default=0.7, 
        help="Temperature for generation (0.0 to 1.0)"
    )
    parser.add_argument(
        "--structured", 
        action="store_true", 
        help="Use structured JSON output"
    )
    parser.add_argument(
        "--no-tools", 
        action="store_true", 
        help="Disable tool usage"
    )
    return parser.parse_args()

def main():
    args = parse_args()
    
    # Initialize the reasoner
    reasoner = ChainOfThoughtReasoner(use_tools=not args.no_tools)
    
    print(f"\n{'=' * 50}")
    print(f"QUERY: {args.query}")
    print(f"Temperature: {args.temperature}")
    print(f"Structured output: {args.structured}")
    print(f"Tools enabled: {not args.no_tools}")
    print(f"{'=' * 50}\n")
    
    # Process the query
    result = reasoner.process_query(
        query=args.query,
        temperature=args.temperature,
        structured_output=args.structured
    )
    
    # Print the result
    if args.structured:
        if "reasoning_steps" in result:
            print("REASONING STEPS:")
            for i, step in enumerate(result["reasoning_steps"], 1):
                print(f"\nSTEP {i}: {step['title']}")
                print(f"{'-' * 40}")
                print(step["content"])
                print(f"Next action: {step['next_action']}")
        
        print("\nFINAL ANSWER:")
        print(f"{'-' * 40}")
        if "final_answer" in result:
            print(result["final_answer"])
        else:
            print("No structured final answer provided")
    else:
        print("RESPONSE:")
        print(f"{'-' * 40}")
        print(result.get("content", "No content provided"))
    
    # Save the result to a file
    output_file = "advanced_example_output.json"
    with open(output_file, "w") as f:
        json.dump(result, f, indent=2)
    
    print(f"\nOutput saved to {output_file}")

if __name__ == "__main__":
    main()
