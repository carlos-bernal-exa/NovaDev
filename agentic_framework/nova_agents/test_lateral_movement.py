#!/usr/bin/env python3
"""
Test Nova with lateral movement query - showing available rules
"""

import asyncio
from nova_framework import NovaFramework

async def test_lateral_movement_query():
    print("🎯 Testing Nova: 'What rules do you have for lateral movement?'")
    print("=" * 60)
    
    # Initialize Nova framework
    framework = NovaFramework()
    
    # Show what data we have available
    print("📋 Available Data in Nova Knowledge Base:")
    print("-" * 40)
    
    beam_results = await framework.search_beam_features("lateral movement")
    print(f"BEAM Features ({beam_results['total_found']} found):")
    for i, rule in enumerate(beam_results['results'], 1):
        print(f"  {i}. {rule['name']} ({rule['rule_type']})")
        print(f"     Description: {rule['description']}")
        print(f"     MITRE: {rule.get('mitre_techniques', [])}")
        print()
    
    corr_results = await framework.search_correlation_rules("lateral movement") 
    print(f"Correlation Rules ({corr_results['total_found']} found):")
    for i, rule in enumerate(corr_results['results'], 1):
        print(f"  {i}. {rule['name']} ({rule['rule_type']})")
        print(f"     Description: {rule['description']}")
        print(f"     MITRE: {rule.get('mitre', [])}")
        print()
    
    # Test with Knowledge Agent in Detection Mode
    print("🤖 Nova Knowledge Agent Response:")
    print("-" * 40)
    framework.set_knowledge_agent_mode("DETECTION_EXPLANATION_MODE")
    
    # Try a more specific query that should trigger the knowledge agent to use its training
    specific_query = "Explain the lateral movement detection rules: First Time Remote Access Tool Usage and Lateral Movement via SMB Admin Shares"
    print(f"Query: {specific_query}")
    print()
    
    response = await framework.process_query(specific_query, session_id="lateral_test")
    response_text = response.parts[0].text if hasattr(response, 'parts') else str(response)
    print("Response:")
    print(response_text)

if __name__ == "__main__":
    asyncio.run(test_lateral_movement_query())