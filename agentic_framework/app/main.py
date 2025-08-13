from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import Dict, Any, Optional
import asyncio
import logging

from .framework import AgenticFramework

app = FastAPI(
    title="Agentic Framework API",
    description="Multi-agent system with concierge routing and Gemini-2.0-flash integration",
    version="1.0.0"
)

# Disable CORS. Do not remove this for full-stack development.
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Allows all origins
    allow_credentials=True,
    allow_methods=["*"],  # Allows all methods
    allow_headers=["*"],  # Allows all headers
)

framework = None

@app.on_event("startup")
async def startup_event():
    """Initialize the agentic framework on startup"""
    global framework
    try:
        framework = AgenticFramework()
        logging.info("Agentic Framework initialized successfully")
    except Exception as e:
        logging.error(f"Failed to initialize framework: {str(e)}")
        raise

class QueryRequest(BaseModel):
    query: str
    session_id: Optional[str] = None

class QueryResponse(BaseModel):
    response: str
    session_id: str
    status: str

@app.get("/")
def read_root():
    """Root endpoint with framework information"""
    return {
        "message": "Agentic Framework API",
        "version": "1.0.0",
        "description": "Multi-agent system with concierge routing and Gemini-2.0-flash integration"
    }

@app.get("/healthz")
async def healthz():
    """Health check endpoint"""
    return {"status": "ok"}

@app.get("/status")
async def get_status():
    """Get framework status and configuration"""
    if not framework:
        raise HTTPException(status_code=503, detail="Framework not initialized")
    
    try:
        status = framework.get_framework_status()
        return {"status": "healthy", "framework": status}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error getting status: {str(e)}")

@app.post("/query", response_model=QueryResponse)
async def process_query(request: QueryRequest):
    """Process a user query through the agentic framework"""
    if not framework:
        raise HTTPException(status_code=503, detail="Framework not initialized")
    
    try:
        response = await framework.process_query(
            user_query=request.query,
            session_id=request.session_id
        )
        
        return QueryResponse(
            response=response,
            session_id=request.session_id or "default",
            status="success"
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error processing query: {str(e)}")

@app.get("/agents")
async def list_agents():
    """List available specialized agents"""
    if not framework:
        raise HTTPException(status_code=503, detail="Framework not initialized")
    
    try:
        status = framework.get_framework_status()
        return {
            "concierge": status["concierge_agent"],
            "specialized_agents": status["specialized_agents"]
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error listing agents: {str(e)}")

@app.get("/token/status")
async def get_token_status():
    """Get Exabeam token management status"""
    if not framework:
        raise HTTPException(status_code=503, detail="Framework not initialized")
    
    try:
        token_info = framework.token_manager.get_token_info()
        return {"token_status": token_info}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error getting token status: {str(e)}")

@app.post("/token/test")
async def test_token_management():
    """Test the token management system"""
    if not framework:
        raise HTTPException(status_code=503, detail="Framework not initialized")
    
    try:
        test_result = await framework.test_token_management()
        return test_result
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error testing token management: {str(e)}")

@app.post("/mcp/test")
async def test_mcp_connection():
    """Test MCP connection"""
    if not framework:
        raise HTTPException(status_code=503, detail="Framework not initialized")
    
    try:
        test_result = await framework.test_mcp_connection()
        return test_result
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error testing MCP connection: {str(e)}")

@app.get("/health")
async def health_check():
    """Detailed health check endpoint"""
    if not framework:
        return {"status": "unhealthy", "reason": "Framework not initialized"}
    
    try:
        status = framework.get_framework_status()
        return {
            "status": "healthy",
            "agents_count": len(status["specialized_agents"]),
            "vertex_ai_configured": status["vertex_ai_configured"]
        }
    except Exception as e:
        return {"status": "unhealthy", "reason": str(e)}
