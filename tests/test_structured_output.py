# test_structured_output.py
import os
import sys
import json

# Add the project root to the Python path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '.')))

# Apply the patch
from src.utils.groq_patch import patch_groq_client
patch_groq_client()

# Import the reasoner
from src.cot.reasoning import ChainOfThoughtReasoner

def main():
    try:
        # Test without tools first (should work with response_format)
        reasoner_no_tools = ChainOfThoughtReasoner(use_tools=False)
        print("Successfully initialized ChainOfThoughtReasoner without tools")
        
        # Test a simple query with structured output
        query = "How many Rs are in the word 'strawberry'?"
        print(f"\nProcessing query without tools: {query}")
        
        result_no_tools = reasoner_no_tools.process_query(
            query=query,
            temperature=0.7,
            structured_output=True
        )
        
        print("\nResult without tools:")
        print(json.dumps(result_no_tools, indent=2))
        
        # Now test with tools
        reasoner_with_tools = ChainOfThoughtReasoner(use_tools=True)
        print("\nSuccessfully initialized ChainOfThoughtReasoner with tools")
        
        # Test a calculation query that should use tools
        calc_query = "What is the square root of 144 plus 25?"
        print(f"\nProcessing calculation query with tools: {calc_query}")
        
        result_with_tools = reasoner_with_tools.process_query(
            query=calc_query,
            temperature=0.7,
            structured_output=True
        )
        
        print("\nResult with tools:")
        print(json.dumps(result_with_tools, indent=2))
        
        print("\nTest successful!")
        
    except Exception as e:
        print(f"Error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()
