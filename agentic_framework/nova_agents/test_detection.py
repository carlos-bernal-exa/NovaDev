#!/usr/bin/env python3
"""
Test Nova Framework with detection explanation queries
"""

import asyncio
from nova_framework import NovaFramework

async def test_detection_queries():
    print("🚀 Testing Nova Framework - Detection Explanation Mode")
    print("=" * 60)
    
    # Initialize Nova framework
    framework = NovaFramework()
    
    # Test queries that should trigger detection explanation mode
    test_queries = [
        "How does the lateral movement detection rule work?",
        "Explain the BEAM feature for unusual network connections",
        "What does the correlation rule for privilege escalation detect?",
        "How does the profiledFeature for first-time logon locations work?"
    ]
    
    for i, query in enumerate(test_queries, 1):
        print(f"\n{'='*60}")
        print(f"Test {i}: {query}")
        print("="*60)
        
        try:
            response = await framework.process_query(
                user_query=query,
                session_id=f"detection_test_{i}"
            )
            
            print("Nova Response:")
            # Clean up the response text
            if hasattr(response, 'parts') and response.parts:
                text = response.parts[0].text if hasattr(response.parts[0], 'text') else str(response.parts[0])
            else:
                text = str(response)
            
            print(text)
            
        except Exception as e:
            print(f"Error: {str(e)}")
        
        print("-" * 40)

if __name__ == "__main__":
    asyncio.run(test_detection_queries())