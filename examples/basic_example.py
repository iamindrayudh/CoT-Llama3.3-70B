"""
Basic example of using the chain of thought reasoner.
"""

import json
import sys
import os

# Add the project root to the Python path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from src.cot.reasoning import ChainOfThoughtReasoner

def main():
    # Initialize the reasoner
    reasoner = ChainOfThoughtReasoner(use_tools=True)
    
    # Example queries
    queries = [
        "How many Rs are in the word 'strawberry'?",
        "If I have 5 apples and give 2 to my friend, then buy 3 more, how many apples do I have?",
        "Explain the concept of recursion in programming."
    ]
    
    # Process each query
    for query in queries:
        print(f"\n\n{'=' * 50}")
        print(f"QUERY: {query}")
        print(f"{'=' * 50}\n")
        
        result = reasoner.process_query(query)
        
        # Print the reasoning steps
        if "reasoning_steps" in result:
            print("REASONING STEPS:")
            for i, step in enumerate(result["reasoning_steps"], 1):
                print(f"\nSTEP {i}: {step['title']}")
                print(f"{'-' * 40}")
                print(step["content"])
                print(f"Next action: {step['next_action']}")
        
        # Print the final answer
        print("\nFINAL ANSWER:")
        print(f"{'-' * 40}")
        if "final_answer" in result:
            print(result["final_answer"])
        else:
            print(result.get("content", "No answer provided"))

if __name__ == "__main__":
    main()
