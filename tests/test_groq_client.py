"""
Tests for the Groq client.
"""

import pytest
import os
import sys
from unittest.mock import patch, MagicMock

# Add the project root to the Python path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from src.api.groq_client import GroqClient

class TestGroqClient:
    
    @patch('src.api.groq_client.Groq')
    def test_initialization(self, mock_groq):
        """Test client initialization."""
        # Arrange
        mock_groq_instance = MagicMock()
        mock_groq.return_value = mock_groq_instance
        
        # Act
        client = GroqClient()
        
        # Assert
        assert client.client == mock_groq_instance
        mock_groq.assert_called_once()
    
    @patch('src.api.groq_client.Groq')
    def test_generate_completion(self, mock_groq):
        """Test generate_completion method."""
        # Arrange
        mock_groq_instance = MagicMock()
        mock_response = MagicMock()
        mock_choice = MagicMock()
        mock_message = MagicMock()
        
        mock_message.content = "Test response"
        mock_choice.message = mock_message
        mock_response.choices = [mock_choice]
        
        mock_groq_instance.chat.completions.create.return_value = mock_response
        mock_groq.return_value = mock_groq_instance
        
        client = GroqClient()
        messages = [{"role": "user", "content": "Test query"}]
        
        # Act
        result = client.generate_completion(messages=messages)
        
        # Assert
        assert result["content"] == "Test response"
        mock_groq_instance.chat.completions.create.assert_called_once()
    
    @patch('src.api.groq_client.Groq')
    def test_generate_completion_with_tools(self, mock_groq):
        """Test generate_completion method with tools."""
        # Arrange
        mock_groq_instance = MagicMock()
        mock_response = MagicMock()
        mock_choice = MagicMock()
        mock_message = MagicMock()
        mock_tool_call = MagicMock()
        
        mock_message.content = "Test response"
        mock_message.tool_calls = [mock_tool_call]
        mock_choice.message = mock_message
        mock_response.choices = [mock_choice]
        
        mock_groq_instance.chat.completions.create.return_value = mock_response
        mock_groq.return_value = mock_groq_instance
        
        client = GroqClient()
        messages = [{"role": "user", "content": "Test query"}]
        tools = [{"type": "function", "function": {"name": "test_function"}}]
        
        # Act
        result = client.generate_completion(messages=messages, tools=tools)
        
        # Assert
        assert result["content"] == "Test response"
        assert result["tool_calls"] == [mock_tool_call]
        mock_groq_instance.chat.completions.create.assert_called_once()
