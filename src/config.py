import os
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# API Configuration
GROQ_API_KEY = os.getenv("GROQ_API_KEY")
if not GROQ_API_KEY:
    raise ValueError("GROQ_API_KEY environment variable is not set")

# Model Configuration
MODEL_NAME = "llama-3.3-70b-versatile"
DEFAULT_TEMPERATURE = 0.7
DEFAULT_MAX_TOKENS = 4000

# Logging Configuration
LOG_LEVEL = os.getenv("LOG_LEVEL", "INFO")
