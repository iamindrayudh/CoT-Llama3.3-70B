"""
This module implements chain of thought reasoning with the Llama model.
"""

import json
import re
from typing import Dict, Any, List, Optional, Union

from src.api.groq_client import GroqClient
from src.cot.prompts import SYSTEM_PROMPT, REASONING_PROMPT_TEMPLATE
from src.cot.schemas import REASONING_SCHEMA, AVAILABLE_TOOLS
from src.tools.calculator import calculate
from src.utils.logger import get_logger

logger = get_logger(__name__)

class ChainOfThoughtReasoner:
    """
    Implements chain of thought reasoning using the Llama model via Groq API.
    """
    
    def __init__(self, use_tools: bool = True):
        """
        Initialize the reasoner.
        
        Args:
            use_tools: Whether to enable tool usage
        """
        self.client = GroqClient()
        self.use_tools = use_tools
        logger.info(f"Initialized ChainOfThoughtReasoner with tools {'enabled' if use_tools else 'disabled'}")
        
    def process_query(
        self, 
        query: str,
        temperature: float = 0.7,
        structured_output: bool = True
    ) -> Dict[str, Any]:
        """
        Process a query using chain of thought reasoning.
        
        Args:
            query: The user's question or problem
            temperature: Temperature for generation (0.0 to 1.0)
            structured_output: Whether to return structured JSON output
            
        Returns:
            Dictionary containing reasoning steps and final answer
        """
        # Prepare messages
        messages = [
            {"role": "system", "content": SYSTEM_PROMPT},
            {"role": "user", "content": REASONING_PROMPT_TEMPLATE.format(query=query)}
        ]
        
        # Prepare request parameters
        kwargs = {
            "messages": messages,
            "temperature": temperature,
        }
        
        # Note: Groq API doesn't support both response_format and tools at the same time
        # So we need to choose one or the other
        if structured_output and not self.use_tools:
            # If we want structured output and don't need tools, use response_format
            kwargs["response_format"] = REASONING_SCHEMA
            
            # Make sure we have the word "json" in the messages
            if "json" not in messages[0]["content"].lower() and "json" not in messages[1]["content"].lower():
                # Add JSON instruction to user message if not already present
                messages[1]["content"] += " Please format your response as JSON."
        elif self.use_tools:
            # If we need tools, we can't use response_format
            # Instead, add explicit instructions for JSON formatting
            if structured_output:
                messages[0]["content"] += "\n\nPlease format your response as a JSON object with the following structure:\n"
                messages[0]["content"] += "{\n  \"reasoning_steps\": [\n    {\"title\": \"Step Title\", \"content\": \"Step content\", \"next_action\": \"continue or final_answer\"},\n    ...\n  ],\n  \"final_answer\": \"Your final answer here\"\n}"
            
            kwargs["tools"] = AVAILABLE_TOOLS
        
        # Generate completion
        logger.info(f"Processing query: {query}")
        response = self.client.generate_completion(**kwargs)
        
        # Handle tool calls if present
        if response.get("tool_calls"):
            messages, result = self._handle_tool_calls(response, messages, structured_output)
            return result
        
        # Parse the response
        try:
            if structured_output:
                # Try to extract JSON from the response
                content = response["content"]
                result = self._extract_json_from_content(content)
            else:
                result = {"content": response["content"]}
                
            logger.info(f"Successfully processed query with {len(result.get('reasoning_steps', [])) if structured_output and 'reasoning_steps' in result else 'unstructured'} reasoning steps")
            return result
            
        except json.JSONDecodeError:
            logger.error("Failed to parse JSON response")
            # Return the raw content so it's still usable
            return {"content": response["content"], "structured": False}
    
    def _extract_json_from_content(self, content: str) -> Dict[str, Any]:
        """
        Extract JSON from content, handling various formats including markdown code blocks.
        
        Args:
            content: The content to extract JSON from
            
        Returns:
            Parsed JSON as a dictionary
        """
        # Try to extract JSON from markdown code blocks first
        json_block_pattern = r"``````"
        json_blocks = re.findall(json_block_pattern, content)
        
        if json_blocks:
            # Try each extracted block
            for block in json_blocks:
                try:
                    return json.loads(block.strip())
                except json.JSONDecodeError:
                    continue
        
        # If no valid JSON blocks found, try the entire content
        return json.loads(content)
    
    def _handle_tool_calls(
        self, 
        response: Dict[str, Any], 
        messages: List[Dict[str, str]],
        structured_output: bool = True
    ) -> tuple:
        """
        Handle tool calls in the response.
        
        Args:
            response: The response from the model
            messages: The current message history
            structured_output: Whether to request structured output
            
        Returns:
            Tuple of (updated messages, result)
        """
        tool_calls = response.get("tool_calls", [])
        if not tool_calls:
            return messages, {"content": response["content"]}
        
        # Add the assistant's message with tool calls
        messages.append({
            "role": "assistant",
            "content": response["content"],
            "tool_calls": tool_calls
        })
        
        # Process each tool call
        tool_results = []
        for tool_call in tool_calls:
            function_name = tool_call.function.name
            function_args = json.loads(tool_call.function.arguments)
            
            tool_result = None
            if function_name == "calculate":
                tool_result = calculate(function_args["expression"])
            
            if tool_result:
                tool_results.append({
                    "tool_call_id": tool_call.id,
                    "role": "tool",
                    "name": function_name,
                    "content": json.dumps(tool_result)
                })
        
        # Add tool results to messages
        messages.extend(tool_results)
        
        # If we want structured output, add a reminder to format as JSON
        if structured_output:
            messages.append({
                "role": "user",
                "content": "Now that you have the calculation result, please provide your final answer. Remember to format your response as JSON with reasoning_steps and final_answer."
            })
        
        # Get final response after tool use
        final_response = self.client.generate_completion(
            messages=messages,
            # We can't use response_format with tools
            # response_format=REASONING_SCHEMA if structured_output else None
        )
        
        try:
            if structured_output:
                # Try to extract JSON from the response
                content = final_response["content"]
                result = self._extract_json_from_content(content)
            else:
                result = {"content": final_response["content"]}
                
            return messages, result
            
        except json.JSONDecodeError:
            logger.warning("Failed to parse JSON response after tool use")
            return messages, {"content": final_response["content"], "structured": False}
            
    def generate_unstructured_reasoning(
        self,
        query: str,
        temperature: float = 0.7
    ) -> str:
        """
        Generate unstructured chain of thought reasoning.
        This is a fallback method when structured output fails.
        
        Args:
            query: The user's question or problem
            temperature: Temperature for generation (0.0 to 1.0)
            
        Returns:
            String containing the reasoning and answer
        """
        # Prepare messages with explicit instruction for step-by-step reasoning
        messages = [
            {
                "role": "system", 
                "content": "You are an expert AI assistant that explains your reasoning step by step. "
                           "Break down complex problems into steps and show your work clearly."
            },
            {
                "role": "user", 
                "content": f"Please solve the following problem using step-by-step reasoning. "
                           f"Show your work and explain each step of your thinking process:\n\n{query}"
            }
        ]
        
        # Generate completion without structured format
        response = self.client.generate_completion(
            messages=messages,
            temperature=temperature
        )
        
        return response["content"]
    
    def process_query_with_fallback(
        self,
        query: str,
        temperature: float = 0.7
    ) -> Dict[str, Any]:
        """
        Process a query with fallback to unstructured output if structured fails.
        
        Args:
            query: The user's question or problem
            temperature: Temperature for generation (0.0 to 1.0)
            
        Returns:
            Dictionary containing the response
        """
        try:
            # First try with structured output
            result = self.process_query(
                query=query,
                temperature=temperature,
                structured_output=True
            )
            
            # Check if we got an error
            if "error" in result:
                logger.warning(f"Structured output failed: {result['error']}. Falling back to unstructured output.")
                
                # Fall back to unstructured output
                content = self.generate_unstructured_reasoning(
                    query=query,
                    temperature=temperature
                )
                
                return {"content": content, "structured": False}
            
            # Check if we got structured output
            if "structured" in result and result["structured"] is False:
                logger.warning("Failed to get structured output. Using the unstructured response.")
                return result
                
            return {**result, "structured": True}
            
        except Exception as e:
            logger.error(f"Error in structured processing: {str(e)}. Falling back to unstructured output.")
            
            try:
                # Fall back to unstructured output
                content = self.generate_unstructured_reasoning(
                    query=query,
                    temperature=temperature
                )
                
                return {"content": content, "structured": False}
                
            except Exception as fallback_error:
                logger.error(f"Fallback also failed: {str(fallback_error)}")
                return {"error": f"Both structured and unstructured processing failed: {str(fallback_error)}"}
