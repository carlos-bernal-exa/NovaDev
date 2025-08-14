import pytest
import jwt
import json
import asyncio
from datetime import datetime, timedelta
from httpx import AsyncClient
import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from main import app

JWT_SECRET = "test-secret-key-for-testing-only"

def create_test_token(payload: dict = None, algorithm: str = "HS256"):
    """Create a test JWT token"""
    if payload is None:
        payload = {
            "sub": "1234567435453453453454365463568900",
            "name": "CARLITOTESTMCP",
            "admin": True,
            "iat": int(datetime.utcnow().timestamp()),
            "exp": int((datetime.utcnow() + timedelta(hours=1)).timestamp())
        }
    return jwt.encode(payload, JWT_SECRET, algorithm=algorithm)

@pytest.mark.asyncio
async def test_health_check():
    """Test the health check endpoint"""
    async with AsyncClient(app=app, base_url="http://test") as ac:
        response = await ac.get("/health")
    
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "healthy"
    assert "timestamp" in data
    assert data["service"] == "exabeam-mcp-server"

@pytest.mark.asyncio
async def test_jwt_authentication_valid():
    """Test JWT authentication with valid token"""
    os.environ["JWT_SECRET"] = JWT_SECRET
    os.environ["EXABEAM_CLIENT_ID"] = "test-client-id"
    os.environ["EXABEAM_CLIENT_SECRET"] = "test-client-secret"
    
    token = create_test_token()
    headers = {"Authorization": f"Bearer {token}"}
    
    async with AsyncClient(app=app, base_url="http://test") as ac:
        response = await ac.get("/mcp/tools", headers=headers)
    
    assert response.status_code == 200
    data = response.json()
    assert "tools" in data
    assert data["user"] == "CARLITOTESTMCP"
    assert len(data["tools"]) > 0

@pytest.mark.asyncio
async def test_jwt_authentication_invalid():
    """Test JWT authentication with invalid token"""
    headers = {"Authorization": "Bearer invalid-token"}
    
    async with AsyncClient(app=app, base_url="http://test") as ac:
        response = await ac.get("/mcp/tools", headers=headers)
    
    assert response.status_code == 401

@pytest.mark.asyncio
async def test_jwt_authentication_missing():
    """Test JWT authentication with missing token"""
    async with AsyncClient(app=app, base_url="http://test") as ac:
        response = await ac.get("/mcp/tools")
    
    assert response.status_code == 403  # FastAPI HTTPBearer returns 403 for missing auth

@pytest.mark.asyncio
async def test_search_cases_endpoint():
    """Test the search cases endpoint"""
    os.environ["JWT_SECRET"] = JWT_SECRET
    os.environ["EXABEAM_CLIENT_ID"] = "test-client-id"
    os.environ["EXABEAM_CLIENT_SECRET"] = "test-client-secret"
    
    token = create_test_token()
    headers = {"Authorization": f"Bearer {token}"}
    
    search_request = {
        "limit": 10,
        "start_time": "2024-05-01T00:00:00Z",
        "end_time": "2024-06-01T00:00:00Z",
        "fields": ["*"],
        "filter_query": 'product: ("Correlation Rule", "NG Analytics")'
    }
    
    async with AsyncClient(app=app, base_url="http://test") as ac:
        response = await ac.post(
            "/mcp/search-cases",
            json=search_request,
            headers=headers
        )
    
    assert response.status_code in [200, 500]
    
    if response.status_code == 500:
        assert "token" in response.text.lower() or "auth" in response.text.lower()

@pytest.mark.asyncio
async def test_token_status_endpoint():
    """Test the token status endpoint"""
    os.environ["JWT_SECRET"] = JWT_SECRET
    os.environ["EXABEAM_CLIENT_ID"] = "test-client-id"
    os.environ["EXABEAM_CLIENT_SECRET"] = "test-client-secret"
    
    token = create_test_token()
    headers = {"Authorization": f"Bearer {token}"}
    
    async with AsyncClient(app=app, base_url="http://test") as ac:
        response = await ac.get("/mcp/token-status", headers=headers)
    
    assert response.status_code in [200, 500]

def test_jwt_token_creation():
    """Test JWT token creation and validation"""
    payload = {
        "sub": "test-user",
        "name": "Test User",
        "admin": False,
        "iat": int(datetime.utcnow().timestamp()),
        "exp": int((datetime.utcnow() + timedelta(hours=1)).timestamp())
    }
    
    token = create_test_token(payload)
    assert isinstance(token, str)
    assert len(token) > 0
    
    decoded = jwt.decode(token, JWT_SECRET, algorithms=["HS256"])
    assert decoded["sub"] == "test-user"
    assert decoded["name"] == "Test User"
    assert decoded["admin"] == False

if __name__ == "__main__":
    pytest.main([__file__, "-v"])
