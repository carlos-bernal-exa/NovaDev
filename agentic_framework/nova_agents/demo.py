#!/usr/bin/env python3
"""
Nova Framework Demo
Demonstrates the Nova AI framework for BEAM rule explanation and exclusion creation.
"""

import asyncio
import logging
from nova_framework import NovaFramework

async def main():
    """Main demo function"""
    print("🚀 Nova Framework Demo")
    print("=" * 50)
    
    # Initialize Nova framework
    print("Initializing Nova Framework...")
    framework = NovaFramework()
    
    # Get framework status
    print("\n📊 Framework Status:")
    status = framework.get_framework_status()
    print(f"Routing Agent: {status['routing_agent']['name']}")
    print(f"Knowledge Agent: {status['knowledge_agent']['name']}")
    print(f"Data Store: {status['datastore']['datastore_id']}")
    print(f"Vertex AI: {'✅ Configured' if status['vertex_ai_configured'] else '❌ Not Configured'}")
    
    # Test data store connection
    print("\n🔌 Testing Data Store Connection...")
    connection_test = await framework.test_datastore_connection()
    if connection_test["test_passed"]:
        print("✅ Data store connection successful")
    else:
        print(f"❌ Data store connection failed: {connection_test.get('error', 'Unknown error')}")
    
    # Demo queries
    demo_queries = [
        {
            "title": "Detection Explanation Query",
            "query": "How does the rundll32 ZxShell detection work?",
            "expected_mode": "DETECTION_EXPLANATION_MODE"
        },
        {
            "title": "Exclusion Creation Query", 
            "query": "I need to create an exclusion for false positives in the PowerShell execution rule",
            "expected_mode": "EXCLUSION_CREATION_MODE"
        },
        {
            "title": "BEAM Feature Search Query",
            "query": "Explain the profiledFeature for unusual logon times",
            "expected_mode": "DETECTION_EXPLANATION_MODE"
        }
    ]
    
    print("\n🧪 Testing Demo Queries:")
    print("-" * 50)
    
    for i, demo in enumerate(demo_queries, 1):
        print(f"\n{i}. {demo['title']}")
        print(f"Query: {demo['query']}")
        print(f"Expected Mode: {demo['expected_mode']}")
        print("Response:")
        
        try:
            response = await framework.process_query(
                user_query=demo['query'],
                session_id=f"demo_session_{i}"
            )
            print(f"✅ {response}")
        except Exception as e:
            print(f"❌ Error: {str(e)}")
        
        print("-" * 30)
    
    # Test direct data store searches
    print("\n🔍 Testing Direct Data Store Searches:")
    print("-" * 50)
    
    # Test BEAM feature search
    print("\n1. BEAM Feature Search:")
    beam_results = await framework.search_beam_features(
        query="process creation anomaly",
        rule_types=["factFeature", "profiledFeature"]
    )
    print(f"Found {beam_results.get('total_found', 0)} BEAM features")
    
    # Test correlation rule search
    print("\n2. Correlation Rule Search:")
    corr_results = await framework.search_correlation_rules(
        query="lateral movement detection"
    )
    print(f"Found {corr_results.get('total_found', 0)} correlation rules")
    
    # Test mode switching
    print("\n🔄 Testing Knowledge Agent Mode Switching:")
    print("-" * 50)
    
    try:
        print("Setting to DETECTION_EXPLANATION_MODE...")
        framework.set_knowledge_agent_mode("DETECTION_EXPLANATION_MODE")
        print("✅ Mode set successfully")
        
        print("Setting to EXCLUSION_CREATION_MODE...")
        framework.set_knowledge_agent_mode("EXCLUSION_CREATION_MODE")
        print("✅ Mode set successfully")
        
    except Exception as e:
        print(f"❌ Mode switching error: {str(e)}")
    
    print("\n🎉 Nova Framework Demo Complete!")
    print("=" * 50)

if __name__ == "__main__":
    # Setup logging
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    
    # Run the demo
    asyncio.run(main())