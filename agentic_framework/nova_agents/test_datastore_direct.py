#!/usr/bin/env python3
"""
Test Nova Data Store directly (without MCP)
"""

import asyncio
from data.datastore_client import NovaDataStoreClient

async def test_datastore_direct():
    print("🗄️ Testing Nova Data Store (No MCP)")
    print("=" * 50)
    
    # Initialize data store client
    client = NovaDataStoreClient()
    
    # Test 1: Get datastore info
    print("1️⃣ Data Store Info:")
    info = client.get_datastore_info()
    print(f"   BEAM Features: {info['beam_features_count']}")
    print(f"   Correlation Rules: {info['correlation_rules_count']}")
    print(f"   Data Store ID: {info['datastore_id']}")
    
    # Test 2: Search lateral movement BEAM features
    print("\n2️⃣ BEAM Feature Search - 'lateral movement':")
    beam_results = await client.search_beam_features("lateral movement")
    print(f"   Found: {beam_results['total_found']} results")
    for result in beam_results['results']:
        print(f"   - {result['name']} ({result['rule_type']})")
        print(f"     {result['description']}")
    
    # Test 3: Search correlation rules
    print("\n3️⃣ Correlation Rule Search - 'lateral movement':")
    corr_results = await client.search_correlation_rules("lateral movement")
    print(f"   Found: {corr_results['total_found']} results")
    for result in corr_results['results']:
        print(f"   - {result['name']} ({result['rule_type']})")
        print(f"     {result['description']}")
    
    # Test 4: Search by activity type
    print("\n4️⃣ Search by Activity Type - 'process-create':")
    activity_results = await client.search_by_activity_type("process-create")
    print(f"   Found: {activity_results['total_found']} results")
    for result in activity_results['results']:
        print(f"   - {result['name']} (applies to: {result['applicable_events']})")
    
    # Test 5: Get rule by ID
    print("\n5️⃣ Get Rule by ID - 'bf_lateral_movement_1':")
    rule = await client.get_rule_by_id("bf_lateral_movement_1")
    if rule:
        print(f"   Found: {rule['name']}")
        print(f"   Type: {rule['rule_type']}")
        print(f"   MITRE: {rule.get('mitre_techniques', 'N/A')}")
    else:
        print("   Not found")
    
    print(f"\n✅ Nova Data Store is working with sample data!")

if __name__ == "__main__":
    asyncio.run(test_datastore_direct())