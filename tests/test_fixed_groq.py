# test_fixed_groq.py
import os
import sys

# Add the project root to the Python path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '.')))

# Apply the patch
from src.utils.groq_patch import patch_groq_client
patch_groq_client()

# Import the client
from src.api.groq_client import GroqClient

def main():
    try:
        # Initialize the client
        client = GroqClient()
        print("Successfully initialized GroqClient")
        
        # Test a simple completion
        result = client.generate_completion(
            messages=[{"role": "user", "content": "Hello, world!"}]
        )
        
        print(f"Response: {result['content']}")
        print("Test successful!")
        
    except Exception as e:
        print(f"Error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()
