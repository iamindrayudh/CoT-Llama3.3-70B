"""
Web application example using FastAPI.
"""

import sys
import os
from typing import Optional, Dict, Any

# Add the project root to the Python path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

# Apply the Groq patch before importing any Groq-related modules
from src.utils.groq_patch import patch_groq_client
patch_groq_client()

import uvicorn
from fastapi import FastAPI, HTTPException, Request
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel

from src.cot.reasoning import ChainOfThoughtReasoner
from src.utils.logger import get_logger

logger = get_logger(__name__)

# Initialize the FastAPI app
app = FastAPI(
    title="Chain of Thought API",
    description="API for chain of thought reasoning with Llama 3.3 70B using Groq",
    version="0.1.0"
)

# Mount static files
app.mount("/static", StaticFiles(directory="static"), name="static")

# Initialize reasoners (with and without tools)
reasoner_with_tools = ChainOfThoughtReasoner(use_tools=True)
reasoner_without_tools = ChainOfThoughtReasoner(use_tools=False)

class QueryRequest(BaseModel):
    query: str
    temperature: Optional[float] = 0.7
    structured_output: Optional[bool] = True
    use_tools: Optional[bool] = True

class QueryResponse(BaseModel):
    result: Dict[str, Any]

@app.post("/api/reason", response_model=QueryResponse)
async def reason(request: QueryRequest):
    """
    Process a query using chain of thought reasoning.
    """
    try:
        logger.info(f"Received query: {request.query}")
        
        # Choose the appropriate reasoner based on tools setting
        reasoner = reasoner_with_tools if request.use_tools else reasoner_without_tools
        
        result = reasoner.process_query(
            query=request.query,
            temperature=request.temperature,
            structured_output=request.structured_output
        )
        
        return {"result": result}
    
    except Exception as e:
        logger.error(f"Error processing query: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Error processing query: {str(e)}")

@app.get("/")
async def root():
    """
    Root endpoint that serves the HTML interface.
    """
    return FileResponse("static/index.html")

@app.get("/health")
async def health():
    """
    Health check endpoint.
    """
    return {"status": "ok", "version": "0.1.0"}

def main():
    """
    Run the FastAPI application.
    """
    uvicorn.run(app, host="0.0.0.0", port=8000)

if __name__ == "__main__":
    main()
