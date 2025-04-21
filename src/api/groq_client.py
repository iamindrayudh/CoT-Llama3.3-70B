"""
Client for interacting with the Groq API.
"""

import os
from groq import Groq
from typing import List, Dict, Any, Optional
import json

from src.utils.logger import get_logger
from src.utils.groq_patch import patch_groq_client

logger = get_logger(__name__)

# Apply the patch before initializing the client
patch_groq_client()

class GroqClient:
    """Client for interacting with the Groq API."""
    
    def __init__(self):
        # Get API key from environment
        api_key = os.getenv("GROQ_API_KEY")
        if not api_key:
            raise ValueError("GROQ_API_KEY environment variable is not set")
            
        # Initialize client
        self.client = Groq(api_key=api_key)
        self.model = "llama-3.3-70b-versatile"
        logger.info(f"Initialized Groq client with model: {self.model}")
        
    def generate_completion(
        self,
        messages: List[Dict[str, str]],
        temperature: float = 0.7,
        max_tokens: int = 4000,
        response_format: Optional[Dict[str, Any]] = None,
        tools: Optional[List[Dict[str, Any]]] = None
    ) -> Dict[str, Any]:
        """
        Generate a completion using the Groq API.
        
        Args:
            messages: List of message dictionaries with 'role' and 'content'
            temperature: Sampling temperature (0.0 to 1.0)
            max_tokens: Maximum number of tokens to generate
            response_format: Format specification for the response
            tools: List of tools available to the model
            
        Returns:
            Dictionary containing the model's response
        """
        try:
            logger.debug(f"Sending request to Groq API with {len(messages)} messages")
            
            # Build kwargs dictionary
            kwargs = {
                "model": self.model,
                "messages": messages,
                "temperature": temperature,
                "max_tokens": max_tokens,
            }
            
            # Only add optional parameters if they're provided
            if response_format:
                kwargs["response_format"] = response_format
                
            if tools:
                kwargs["tools"] = tools
            
            # Make the API call
            completion = self.client.chat.completions.create(**kwargs)
            
            # Extract content
            content = completion.choices[0].message.content
            logger.debug(f"Received response from Groq API: {content[:100]}...")
            
            # Try to get tool calls if they exist
            tool_calls = None
            try:
                tool_calls = completion.choices[0].message.tool_calls
            except AttributeError:
                pass
            
            # Return result
            return {
                "content": content,
                "tool_calls": tool_calls
            }
            
        except Exception as e:
            logger.error(f"Error in Groq API call: {str(e)}")
            raise
