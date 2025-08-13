import asyncio
import json
import sys
import os

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.framework import AgenticFramework

async def main():
    """
    Demo script to test the agentic framework functionality.
    Tests intent detection, routing, and token management.
    """
    print("🚀 Starting Agentic Framework Demo")
    print("=" * 50)
    
    framework = AgenticFramework()
    
    print("\n📊 Framework Status:")
    status = framework.get_framework_status()
    print(json.dumps(status, indent=2))
    
    print("\n🔐 Testing Token Management:")
    token_test = await framework.test_token_management()
    print(json.dumps(token_test, indent=2))
    
    print("\n🔌 Testing MCP Connection:")
    mcp_test = await framework.test_mcp_connection()
    print(json.dumps(mcp_test, indent=2))
    
    print("\n🎯 Testing Intent Detection and Routing:")
    test_queries = [
        "I need help analyzing a suspicious email attachment that might be malware",
        "What are the GDPR compliance requirements for data processing?",
        "We had a security breach and need incident response guidance",
        "How should we design a secure network architecture for our cloud infrastructure?",
        "Can you explain the latest cybersecurity threats?"
    ]
    
    for i, query in enumerate(test_queries, 1):
        print(f"\n--- Test Query {i} ---")
        print(f"Query: {query}")
        
        try:
            response = await framework.process_query(query, f"demo_session_{i}")
            print(f"Response: {response}")
        except Exception as e:
            print(f"Error: {str(e)}")
    
    print("\n✅ Demo completed!")

if __name__ == "__main__":
    asyncio.run(main())
