"""
Tests for the chain of thought reasoning module.
"""

import pytest
import os
import sys
import json
from unittest.mock import patch, MagicMock

# Add the project root to the Python path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from src.cot.reasoning import ChainOfThoughtReasoner

class TestChainOfThoughtReasoner:
    
    @patch('src.cot.reasoning.GroqClient')
    def test_initialization(self, mock_groq_client):
        """Test reasoner initialization."""
        # Arrange
        mock_client_instance = MagicMock()
        mock_groq_client.return_value = mock_client_instance
        
        # Act
        reasoner = ChainOfThoughtReasoner(use_tools=True)
        
        # Assert
        assert reasoner.client == mock_client_instance
        assert reasoner.use_tools is True
    
    @patch('src.cot.reasoning.GroqClient')
    def test_process_query_structured(self, mock_groq_client):
        """Test process_query method with structured output."""
        # Arrange
        mock_client_instance = MagicMock()
        mock_response = {
            "content": json.dumps({
                "reasoning_steps": [
                    {
                        "title": "Step 1",
                        "content": "Content 1",
                        "next_action": "continue"
                    },
                    {
                        "title": "Step 2",
                        "content": "Content 2",
                        "next_action": "final_answer"
                    }
                ],
                "final_answer": "Final answer"
            })
        }
        mock_client_instance.generate_completion.return_value = mock_response
        mock_groq_client.return_value = mock_client_instance
        
        reasoner = ChainOfThoughtReasoner(use_tools=False)
        
        # Act
        result = reasoner.process_query("Test query", structured_output=True)
        
        # Assert
        assert "reasoning_steps" in result
        assert len(result["reasoning_steps"]) == 2
        assert result["final_answer"] == "Final answer"
        mock_client_instance.generate_completion.assert_called_once()
    
    @patch('src.cot.reasoning.GroqClient')
    def test_process_query_unstructured(self, mock_groq_client):
        """Test process_query method with unstructured output."""
        # Arrange
        mock_client_instance = MagicMock()
        mock_response = {
            "content": "This is an unstructured response."
        }
        mock_client_instance.generate_completion.return_value = mock_response
        mock_groq_client.return_value = mock_client_instance
        
        reasoner = ChainOfThoughtReasoner(use_tools=False)
        
        # Act
        result = reasoner.process_query("Test query", structured_output=False)
        
        # Assert
        assert "content" in result
        assert result["content"] == "This is an unstructured response."
        mock_client_instance.generate_completion.assert_called_once()
    
    @patch('src.cot.reasoning.GroqClient')
    @patch('src.cot.reasoning.calculate')
    def test_process_query_with_tool_calls(self, mock_calculate, mock_groq_client):
        """Test process_query method with tool calls."""
        # Arrange
        mock_client_instance = MagicMock()
        
        # First response with tool call
        mock_tool_call = MagicMock()
        mock_tool_call.id = "call_123"
        mock_tool_call.function.name = "calculate"
        mock_tool_call.function.arguments = json.dumps({"expression": "2+2"})
        
        mock_first_response = {
            "content": "Let me calculate that for you.",
            "tool_calls": [mock_tool_call]
        }
        
        # Second response after tool call
        mock_second_response = {
            "content": json.dumps({
                "reasoning_steps": [
                    {
                        "title": "Calculation",
                        "content": "I calculated 2+2=4",
                        "next_action": "final_answer"
                    }
                ],
                "final_answer": "The answer is 4"
            })
        }
        
        mock_client_instance.generate_completion.side_effect = [
            mock_first_response, 
            mock_second_response
        ]
        
        mock_groq_client.return_value = mock_client_instance
        mock_calculate.return_value = {"result": 4}
        
        reasoner = ChainOfThoughtReasoner(use_tools=True)
        
        # Act
        result = reasoner.process_query("Calculate 2+2", structured_output=True)
        
        # Assert
        assert "reasoning_steps" in result
        assert result["final_answer"] == "The answer is 4"
        assert mock_client_instance.generate_completion.call_count == 2
        mock_calculate.assert_called_once_with("2+2")
