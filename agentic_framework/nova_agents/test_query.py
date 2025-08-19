#!/usr/bin/env python3
"""
Test Nova Framework with a real query
"""

import asyncio
from nova_framework import NovaFramework

async def test_lateral_movement_query():
    print("🚀 Testing Nova Framework with Lateral Movement Query")
    print("=" * 60)
    
    # Initialize Nova framework
    framework = NovaFramework()
    
    # Test query about lateral movement rules
    query = "What rules do you have for lateral movement?"
    print(f"Query: {query}")
    print("\nProcessing...")
    print("-" * 40)
    
    try:
        response = await framework.process_query(
            user_query=query,
            session_id="lateral_movement_test"
        )
        
        print("Nova Response:")
        print(response)
        
    except Exception as e:
        print(f"Error: {str(e)}")
    
    print("\n" + "=" * 60)

if __name__ == "__main__":
    asyncio.run(test_lateral_movement_query())