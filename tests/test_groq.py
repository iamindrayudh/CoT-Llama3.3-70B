import os
import sys
import inspect
from dotenv import load_dotenv
import traceback

# Load environment variables
load_dotenv()

# Get API key
api_key = os.getenv("GROQ_API_KEY")
print(f"API key found: {'Yes' if api_key else 'No'}")

# Debug information about the environment
print(f"Python version: {sys.version}")
print(f"Python executable: {sys.executable}")

try:
    # Import and print version information
    import groq
    print(f"Groq package location: {groq.__file__}")
    print(f"Groq version: {getattr(groq, '__version__', 'unknown')}")
    
    # Inspect the Groq class
    from groq import Groq
    print("\nGroq class initialization parameters:")
    sig = inspect.signature(Groq.__init__)
    print(f"Parameters: {sig.parameters}")
    
    # Inspect the base client
    base_client_path = os.path.join(os.path.dirname(groq.__file__), "_base_client.py")
    print(f"\nChecking if base client exists at: {base_client_path}")
    print(f"Base client exists: {os.path.exists(base_client_path)}")
    
    if os.path.exists(base_client_path):
        with open(base_client_path, 'r') as f:
            content = f.read()
            # Look for SyncHttpxClientWrapper
            if "SyncHttpxClientWrapper" in content:
                print("\nFound SyncHttpxClientWrapper in _base_client.py")
                # Extract the class definition
                import re
                wrapper_class = re.search(r'class SyncHttpxClientWrapper.*?def __init__\(self,(.*?)\):', 
                                         content, re.DOTALL)
                if wrapper_class:
                    print(f"SyncHttpxClientWrapper __init__ parameters: {wrapper_class.group(1)}")
    
    # Try to create a client with minimal arguments
    print("\nAttempting to initialize Groq client with only api_key...")
    client = Groq(api_key=api_key)
    print("Successfully initialized Groq client with minimal arguments")
    
    # If that works, try a simple completion
    print("\nTrying a simple completion...")
    response = client.chat.completions.create(
        messages=[{"role": "user", "content": "Hello, world!"}],
        model="llama-3.3-70b-versatile"
    )
    print(f"Response received: {response.choices[0].message.content[:50]}...")
    
except ImportError as e:
    print(f"ImportError: {e}")
    print("Please install the groq package with: pip install groq")
    
except TypeError as e:
    print(f"\nTypeError during initialization: {e}")
    print("\nDetailed error information:")
    traceback.print_exc()
    
    # Try to fix the issue by monkey patching
    print("\nAttempting to fix by monkey patching...")
    try:
        from groq._base_client import SyncHttpxClientWrapper
        
        # Save the original __init__
        original_init = SyncHttpxClientWrapper.__init__
        
        # Define a new __init__ that ignores the proxies parameter
        def new_init(self, *args, **kwargs):
            # Remove proxies if present
            if 'proxies' in kwargs:
                print("Removing 'proxies' parameter from kwargs")
                del kwargs['proxies']
            return original_init(self, *args, **kwargs)
        
        # Replace the __init__ method
        SyncHttpxClientWrapper.__init__ = new_init
        
        print("Monkey patching complete, trying to initialize client again...")
        client = Groq(api_key=api_key)
        print("Successfully initialized Groq client after monkey patching")
        
    except Exception as patch_error:
        print(f"Failed to apply monkey patch: {patch_error}")
        
        # Alternative approach: try to use httpx directly
        print("\nAttempting alternative approach with direct httpx usage...")
        try:
            import httpx
            print(f"httpx version: {httpx.__version__}")
            
            # Check if we can create a custom client implementation
            print("Creating custom Groq client implementation...")
            
            class CustomGroqClient:
                def __init__(self, api_key):
                    self.api_key = api_key
                    self.base_url = "https://api.groq.com/openai/v1"
                    self.client = httpx.Client(
                        base_url=self.base_url,
                        headers={"Authorization": f"Bearer {api_key}"}
                    )
                
                def create_completion(self, messages, model):
                    response = self.client.post(
                        "/chat/completions",
                        json={
                            "model": model,
                            "messages": messages
                        }
                    )
                    return response.json()
            
            custom_client = CustomGroqClient(api_key)
            print("Custom client created successfully")
            
        except Exception as httpx_error:
            print(f"Failed to create custom client: {httpx_error}")
    
except Exception as e:
    print(f"\nUnexpected error: {e}")
    traceback.print_exc()

print("\nDebugging complete")
