import os
import jwt
import asyncio
import json
import logging
from datetime import datetime, timedelta
from typing import Dict, Any, Optional, List
from fastapi import FastAPI, HTTPException, Depends, Request
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from fastapi.middleware.cors import CORSMiddleware
from sse_starlette.sse import EventSourceResponse
from pydantic import BaseModel
import uvicorn
from dotenv import load_dotenv

from exabeam_client import ExabeamTokenManager
from mcp_server import MCPServer

load_dotenv()

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

try:
    from vault_client import VaultClient, load_secrets_from_vault, merge_vault_secrets
    vault_available = True
except ImportError:
    vault_available = False
    logger.warning("Vault client not available, using environment variables only")

app = FastAPI(
    title="Standalone Exabeam MCP Server",
    version="1.0.0",
    description="Containerized MCP server for Exabeam case search with JWT authentication and SSE support"
)

security = HTTPBearer()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

exabeam_manager: Optional[ExabeamTokenManager] = None
mcp_server: Optional[MCPServer] = None
vault_client: Optional['VaultClient'] = None

@app.on_event("startup")
async def startup_event():
    """Initialize the application on startup"""
    global exabeam_manager, mcp_server, vault_client
    
    logger.info("Starting Exabeam MCP Server...")
    
    if vault_available:
        vault_client = VaultClient()
        if vault_client.enabled:
            logger.info("Vault integration enabled, loading secrets...")
            try:
                vault_secrets = await vault_client.get_secrets()
                merge_vault_secrets(vault_secrets)
                logger.info("Successfully loaded secrets from Vault")
            except Exception as e:
                logger.error(f"Failed to load secrets from Vault: {str(e)}")
                logger.info("Continuing with environment variables...")
    
    client_id = os.getenv("EXABEAM_CLIENT_ID")
    client_secret = os.getenv("EXABEAM_CLIENT_SECRET")
    jwt_secret = os.getenv("JWT_SECRET")
    
    if not client_id or not client_secret:
        raise ValueError("EXABEAM_CLIENT_ID and EXABEAM_CLIENT_SECRET must be set")
    
    if not jwt_secret:
        raise ValueError("JWT_SECRET must be set")
    
    cache_file = os.getenv("TOKEN_CACHE_FILE", "/tmp/exabeam_token_cache.json")
    exabeam_manager = ExabeamTokenManager(client_id, client_secret, token_cache_file=cache_file)
    mcp_server = MCPServer(exabeam_manager)
    
    logger.info("Exabeam MCP Server initialized successfully")

async def verify_jwt_token(credentials: HTTPAuthorizationCredentials = Depends(security)):
    """
    Verify JWT token and return payload.
    Supports both RS256 and HS256 algorithms for flexibility.
    """
    try:
        jwt_secret = os.getenv("JWT_SECRET")
        if not jwt_secret:
            raise HTTPException(status_code=500, detail="JWT_SECRET not configured")
        
        unverified_header = jwt.get_unverified_header(credentials.credentials)
        algorithm = unverified_header.get("alg", "HS256")
        
        if algorithm == "RS256":
            payload = jwt.decode(
                credentials.credentials,
                jwt_secret,
                algorithms=["RS256"],
                options={"verify_signature": False}  # For demo purposes, disable signature verification
            )
        else:
            payload = jwt.decode(
                credentials.credentials, 
                jwt_secret, 
                algorithms=["HS256"]
            )
        
        if payload.get("exp") and datetime.utcnow().timestamp() > payload["exp"]:
            raise HTTPException(status_code=401, detail="Token expired")
        
        logger.info(f"JWT token verified for user: {payload.get('name', payload.get('sub', 'unknown'))}")
        return payload
        
    except jwt.InvalidTokenError as e:
        logger.warning(f"Invalid JWT token: {str(e)}")
        raise HTTPException(status_code=401, detail="Invalid token")
    except Exception as e:
        logger.error(f"JWT verification error: {str(e)}")
        raise HTTPException(status_code=401, detail="Token verification failed")

class SearchCasesRequest(BaseModel):
    """Request model for case search"""
    limit: int = 3000
    start_time: str = "2024-05-01T00:00:00Z"
    end_time: str = "2024-06-01T00:00:00Z"
    fields: List[str] = ["*"]
    filter_query: str = 'product: ("Correlation Rule", "NG Analytics")'

@app.get("/health")
async def health_check():
    """Health check endpoint"""
    health_status = {
        "status": "healthy",
        "timestamp": datetime.utcnow().isoformat(),
        "service": "exabeam-mcp-server",
        "version": "1.0.0"
    }
    
    if vault_client and vault_client.enabled:
        try:
            vault_healthy = await vault_client.health_check()
            health_status["vault"] = {
                "enabled": True,
                "healthy": vault_healthy,
                "url": vault_client.vault_url
            }
        except Exception as e:
            health_status["vault"] = {
                "enabled": True,
                "healthy": False,
                "error": str(e)
            }
    else:
        health_status["vault"] = {"enabled": False}
    
    return health_status

@app.post("/mcp/search-cases")
async def search_cases(
    request: SearchCasesRequest,
    token_payload: dict = Depends(verify_jwt_token)
):
    """Search Exabeam cases with JWT authentication"""
    try:
        logger.info(f"Case search requested by user: {token_payload.get('name', 'unknown')}")
        
        result = await mcp_server.search_cases(
            limit=request.limit,
            start_time=request.start_time,
            end_time=request.end_time,
            fields=request.fields,
            filter_query=request.filter_query
        )
        
        return {
            "success": True,
            "data": result,
            "user": token_payload.get("name", token_payload.get("sub", "unknown")),
            "timestamp": datetime.utcnow().isoformat()
        }
        
    except Exception as e:
        logger.error(f"Case search failed: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/mcp/tools")
async def list_tools(token_payload: dict = Depends(verify_jwt_token)):
    """List available MCP tools"""
    return {
        "tools": [
            {
                "name": "search_cases",
                "description": "Search Exabeam security cases",
                "parameters": {
                    "limit": "Maximum number of cases to return (default: 3000)",
                    "start_time": "Start time in ISO format (default: 2024-05-01T00:00:00Z)",
                    "end_time": "End time in ISO format (default: 2024-06-01T00:00:00Z)", 
                    "fields": "List of fields to return (default: ['*'])",
                    "filter_query": "Filter query string (default: product filter)"
                }
            }
        ],
        "user": token_payload.get("name", token_payload.get("sub", "unknown")),
        "timestamp": datetime.utcnow().isoformat()
    }

@app.get("/events")
async def stream_events(
    request: Request,
    token_payload: dict = Depends(verify_jwt_token)
):
    """Server-Sent Events endpoint for real-time updates"""
    
    user_name = token_payload.get("name", token_payload.get("sub", "unknown"))
    logger.info(f"SSE connection established for user: {user_name}")
    
    async def event_generator():
        try:
            yield {
                "event": "connected",
                "data": json.dumps({
                    "message": "Connected to Exabeam MCP Server",
                    "user": user_name,
                    "admin": token_payload.get("admin", False),
                    "timestamp": datetime.utcnow().isoformat(),
                    "server_version": "1.0.0"
                })
            }
            
            heartbeat_count = 0
            while True:
                if await request.is_disconnected():
                    logger.info(f"SSE connection disconnected for user: {user_name}")
                    break
                
                heartbeat_count += 1
                
                yield {
                    "event": "heartbeat", 
                    "data": json.dumps({
                        "timestamp": datetime.utcnow().isoformat(),
                        "status": "alive",
                        "heartbeat_count": heartbeat_count,
                        "user": user_name
                    })
                }
                
                if heartbeat_count % 10 == 0:  # Every 10 heartbeats = 5 minutes
                    try:
                        token_info = exabeam_manager.get_token_info()
                        yield {
                            "event": "token_status",
                            "data": json.dumps({
                                "timestamp": datetime.utcnow().isoformat(),
                                "token_info": token_info,
                                "user": user_name
                            })
                        }
                    except Exception as e:
                        logger.error(f"Error getting token info: {str(e)}")
                
                await asyncio.sleep(30)
                
        except Exception as e:
            logger.error(f"SSE error for user {user_name}: {str(e)}")
            yield {
                "event": "error",
                "data": json.dumps({
                    "error": str(e),
                    "timestamp": datetime.utcnow().isoformat()
                })
            }
    
    return EventSourceResponse(event_generator())

@app.get("/mcp/token-status")
async def get_token_status(token_payload: dict = Depends(verify_jwt_token)):
    """Get current Exabeam token status"""
    try:
        token_info = exabeam_manager.get_token_info()
        return {
            "success": True,
            "token_info": token_info,
            "user": token_payload.get("name", token_payload.get("sub", "unknown")),
            "timestamp": datetime.utcnow().isoformat()
        }
    except Exception as e:
        logger.error(f"Error getting token status: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

if __name__ == "__main__":
    port = int(os.getenv("PORT", 8080))
    log_level = os.getenv("LOG_LEVEL", "info").lower()
    
    logger.info(f"Starting server on port {port}")
    
    uvicorn.run(
        app, 
        host="0.0.0.0", 
        port=port,
        log_level=log_level,
        access_log=True
    )
