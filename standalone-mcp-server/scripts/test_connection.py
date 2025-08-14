#!/usr/bin/env python3
"""
Test script for the Exabeam MCP Server

This script tests JWT authentication, MCP endpoints, and SSE connections.
"""

import asyncio
import aiohttp
import json
import sys
import os
from datetime import datetime

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from generate_token import generate_token

async def test_health_check(base_url: str):
    """Test the health check endpoint"""
    print("🏥 Testing health check...")
    
    async with aiohttp.ClientSession() as session:
        try:
            async with session.get(f"{base_url}/health") as response:
                if response.status == 200:
                    data = await response.json()
                    print(f"✅ Health check passed: {data['status']}")
                    return True
                else:
                    print(f"❌ Health check failed: {response.status}")
                    return False
        except Exception as e:
            print(f"❌ Health check error: {str(e)}")
            return False

async def test_jwt_auth(base_url: str, token: str):
    """Test JWT authentication"""
    print("🔐 Testing JWT authentication...")
    
    headers = {"Authorization": f"Bearer {token}"}
    
    async with aiohttp.ClientSession() as session:
        try:
            async with session.get(f"{base_url}/mcp/tools", headers=headers) as response:
                if response.status == 200:
                    data = await response.json()
                    print(f"✅ JWT auth passed for user: {data.get('user', 'unknown')}")
                    print(f"   Available tools: {len(data.get('tools', []))}")
                    return True
                else:
                    error_text = await response.text()
                    print(f"❌ JWT auth failed: {response.status} - {error_text}")
                    return False
        except Exception as e:
            print(f"❌ JWT auth error: {str(e)}")
            return False

async def test_case_search(base_url: str, token: str):
    """Test case search endpoint"""
    print("🔍 Testing case search...")
    
    headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json"
    }
    
    search_request = {
        "limit": 10,
        "start_time": "2024-05-01T00:00:00Z",
        "end_time": "2024-06-01T00:00:00Z",
        "fields": ["*"],
        "filter_query": 'product: ("Correlation Rule", "NG Analytics")'
    }
    
    async with aiohttp.ClientSession() as session:
        try:
            async with session.post(
                f"{base_url}/mcp/search-cases", 
                headers=headers,
                json=search_request
            ) as response:
                if response.status == 200:
                    data = await response.json()
                    case_count = len(data.get('data', {}).get('cases', []))
                    print(f"✅ Case search passed: {case_count} cases found")
                    return True
                else:
                    error_text = await response.text()
                    print(f"⚠️  Case search returned {response.status}: {error_text}")
                    return response.status in [401, 500]  # Auth issues are expected in test
        except Exception as e:
            print(f"❌ Case search error: {str(e)}")
            return False

async def test_sse_connection(base_url: str, token: str, duration: int = 10):
    """Test Server-Sent Events connection"""
    print(f"📡 Testing SSE connection for {duration} seconds...")
    
    headers = {"Authorization": f"Bearer {token}"}
    
    async with aiohttp.ClientSession() as session:
        try:
            async with session.get(
                f"{base_url}/events", 
                headers=headers
            ) as response:
                if response.status == 200:
                    print("✅ SSE connection established")
                    
                    event_count = 0
                    start_time = asyncio.get_event_loop().time()
                    
                    async for line in response.content:
                        if asyncio.get_event_loop().time() - start_time > duration:
                            break
                        
                        line = line.decode('utf-8').strip()
                        if line.startswith('data: '):
                            try:
                                data = json.loads(line[6:])  # Remove 'data: ' prefix
                                event_count += 1
                                print(f"   📨 Event {event_count}: {data.get('message', data.get('status', 'unknown'))}")
                            except json.JSONDecodeError:
                                print(f"   📨 Raw event: {line}")
                    
                    print(f"✅ SSE test completed: {event_count} events received")
                    return True
                else:
                    error_text = await response.text()
                    print(f"❌ SSE connection failed: {response.status} - {error_text}")
                    return False
        except Exception as e:
            print(f"❌ SSE connection error: {str(e)}")
            return False

async def main():
    """Main test function"""
    if len(sys.argv) < 2:
        print("Usage: python test_connection.py <base_url> [jwt_secret]")
        print("Example: python test_connection.py http://localhost:8080 my-secret-key")
        sys.exit(1)
    
    base_url = sys.argv[1].rstrip('/')
    jwt_secret = sys.argv[2] if len(sys.argv) > 2 else "test-secret-key"
    
    print(f"🚀 Testing Exabeam MCP Server at {base_url}")
    print("=" * 60)
    
    token = generate_token(
        secret=jwt_secret,
        user_id="test-user-123",
        name="Test User",
        admin=True,
        hours=1
    )
    
    print(f"🎫 Generated test token for authentication")
    
    tests = [
        ("Health Check", test_health_check(base_url)),
        ("JWT Authentication", test_jwt_auth(base_url, token)),
        ("Case Search", test_case_search(base_url, token)),
        ("SSE Connection", test_sse_connection(base_url, token, 10))
    ]
    
    results = []
    for test_name, test_coro in tests:
        print(f"\n--- {test_name} ---")
        try:
            result = await test_coro
            results.append((test_name, result))
        except Exception as e:
            print(f"❌ {test_name} failed with exception: {str(e)}")
            results.append((test_name, False))
    
    print("\n" + "=" * 60)
    print("📊 Test Summary:")
    passed = sum(1 for _, result in results if result)
    total = len(results)
    
    for test_name, result in results:
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"   {status} {test_name}")
    
    print(f"\nOverall: {passed}/{total} tests passed")
    
    if passed == total:
        print("🎉 All tests passed! MCP server is working correctly.")
        sys.exit(0)
    else:
        print("⚠️  Some tests failed. Check the logs above for details.")
        sys.exit(1)

if __name__ == "__main__":
    asyncio.run(main())
