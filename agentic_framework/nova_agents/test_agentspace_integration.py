#!/usr/bin/env python3
"""
Test Nova Framework integration with Agentspace
"""

import asyncio
import json
import logging
import os
import requests
import subprocess
from nova_framework import NovaFramework

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("agentspace_test")

class AgentspaceIntegrationTest:
    """Test Nova Framework with Agentspace integration"""
    
    def __init__(self):
        self.project_id = "threatexplainer"
        self.agentspace_id = "agentspace-1754331730713_1754331730714"
        self.datastore_id = "content_1755237537757"
        
        # Set environment
        os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = "/Users/cbernal/Downloads/threatexplainer-1185aa9fcd44.json"
    
    def get_access_token(self):
        """Get access token for API calls"""
        try:
            result = subprocess.run([
                'gcloud', 'auth', 'application-default', 'print-access-token'
            ], capture_output=True, text=True)
            
            if result.returncode == 0:
                return result.stdout.strip()
            else:
                logger.error(f"Failed to get access token: {result.stderr}")
                return None
                
        except Exception as e:
            logger.error(f"Error getting access token: {str(e)}")
            return None
    
    def test_agentspace_agent(self):
        """Test connection to Agentspace agent"""
        logger.info(f"Testing Agentspace agent: {self.agentspace_id}")
        
        try:
            access_token = self.get_access_token()
            if not access_token:
                return False
            
            headers = {
                'Authorization': f'Bearer {access_token}',
                'Content-Type': 'application/json'
            }
            
            # Get agent information
            agent_url = f"https://discoveryengine.googleapis.com/v1/projects/{self.project_id}/locations/global/collections/default_collection/engines/{self.agentspace_id}"
            
            response = requests.get(agent_url, headers=headers)
            
            if response.status_code == 200:
                agent_info = response.json()
                logger.info(f"✓ Agentspace agent found: {agent_info.get('displayName')}")
                logger.info(f"✓ Solution type: {agent_info.get('solutionType')}")
                logger.info(f"✓ Datastore IDs: {agent_info.get('dataStoreIds')}")
                logger.info(f"✓ Create time: {agent_info.get('createTime')}")
                
                # Check if our datastore is connected
                datastore_ids = agent_info.get('dataStoreIds', [])
                if self.datastore_id in datastore_ids:
                    logger.info(f"✓ Nova datastore {self.datastore_id} is connected")
                else:
                    logger.warning(f"⚠️ Nova datastore {self.datastore_id} not found in connected datastores")
                
                return True
            else:
                logger.error(f"Failed to get agent info: {response.status_code} - {response.text}")
                return False
                
        except Exception as e:
            logger.error(f"Error testing Agentspace agent: {str(e)}")
            return False
    
    def test_datastore_connection(self):
        """Test datastore connection"""
        logger.info(f"Testing datastore connection: {self.datastore_id}")
        
        try:
            access_token = self.get_access_token()
            if not access_token:
                return False
            
            headers = {
                'Authorization': f'Bearer {access_token}',
                'Content-Type': 'application/json'
            }
            
            # Get datastore information
            datastore_url = f"https://discoveryengine.googleapis.com/v1/projects/{self.project_id}/locations/global/collections/default_collection/dataStores/{self.datastore_id}"
            
            response = requests.get(datastore_url, headers=headers)
            
            if response.status_code == 200:
                datastore_info = response.json()
                logger.info(f"✓ Datastore found: {datastore_info.get('displayName')}")
                logger.info(f"✓ Content config: {datastore_info.get('contentConfig')}")
                logger.info(f"✓ Solution types: {datastore_info.get('solutionTypes')}")
                return True
            else:
                logger.error(f"Failed to get datastore info: {response.status_code} - {response.text}")
                return False
                
        except Exception as e:
            logger.error(f"Error testing datastore: {str(e)}")
            return False
    
    async def test_nova_framework(self):
        """Test Nova Framework functionality"""
        logger.info("Testing Nova Framework...")
        
        try:
            # Initialize Nova Framework
            framework = NovaFramework(datastore_id=self.datastore_id)
            
            # Test 1: Framework status
            logger.info("\n🧪 Test 1: Framework Status")
            status = framework.get_framework_status()
            logger.info(f"✓ Routing agent: {status['routing_agent']['name']}")
            logger.info(f"✓ Knowledge agent: {status['knowledge_agent']['name']}")
            logger.info(f"✓ Current mode: {status['knowledge_agent']['current_mode']}")
            logger.info(f"✓ Datastore ID: {status['datastore']['datastore_id']}")
            
            # Test 2: Datastore connection
            logger.info("\n🧪 Test 2: Datastore Connection")
            connection_test = await framework.test_datastore_connection()
            if connection_test['test_passed']:
                logger.info(f"✓ Connection test passed")
                logger.info(f"✓ BEAM features: {connection_test.get('beam_features_available', 0)}")
                logger.info(f"✓ Correlation rules: {connection_test.get('correlation_rules_available', 0)}")
            else:
                logger.error(f"✗ Connection test failed: {connection_test.get('error')}")
                return False
            
            # Test 3: Search functionality
            logger.info("\n🧪 Test 3: Search Functionality")
            beam_results = await framework.search_beam_features("lateral movement")
            logger.info(f"✓ BEAM features found: {beam_results.get('total_found', 0)}")
            
            corr_results = await framework.search_correlation_rules("lateral movement")
            logger.info(f"✓ Correlation rules found: {corr_results.get('total_found', 0)}")
            
            # Test 4: Agent processing
            logger.info("\n🧪 Test 4: Agent Processing")
            
            # Test Detection Mode
            framework.set_knowledge_agent_mode("DETECTION_EXPLANATION_MODE")
            detection_response = await framework.process_query(
                "Explain the lateral movement detection rules available",
                "agentspace_test_detection"
            )
            
            if detection_response and not detection_response.startswith("Error"):
                logger.info("✓ Detection mode response received")
                logger.info(f"Response preview: {detection_response[:150]}...")
            else:
                logger.error(f"✗ Detection mode failed: {detection_response}")
                return False
            
            # Test Exclusion Mode
            framework.set_knowledge_agent_mode("EXCLUSION_CREATION_MODE")
            exclusion_response = await framework.process_query(
                "Help me create an exclusion for PowerShell false positives",
                "agentspace_test_exclusion"
            )
            
            if exclusion_response and not exclusion_response.startswith("Error"):
                logger.info("✓ Exclusion mode response received")
                logger.info(f"Response preview: {exclusion_response[:150]}...")
            else:
                logger.error(f"✗ Exclusion mode failed: {exclusion_response}")
                return False
            
            logger.info("\n✅ All Nova Framework tests passed!")
            return True
            
        except Exception as e:
            logger.error(f"Nova Framework test error: {str(e)}")
            return False
    
    async def run_full_test(self):
        """Run complete integration test"""
        logger.info("🚀 Starting Nova-Agentspace Integration Test")
        
        test_steps = [
            ("Agentspace Agent Test", self.test_agentspace_agent),
            ("Datastore Connection Test", self.test_datastore_connection),
            ("Nova Framework Test", self.test_nova_framework)
        ]
        
        for step_name, test_func in test_steps:
            logger.info(f"\n📋 Running: {step_name}")
            
            if asyncio.iscoroutinefunction(test_func):
                result = await test_func()
            else:
                result = test_func()
            
            if not result:
                logger.error(f"❌ {step_name} failed - stopping tests")
                return False
            
            logger.info(f"✅ {step_name} passed")
        
        logger.info("\n🎉 Nova-Agentspace Integration Test completed successfully!")
        logger.info(f"🤖 Agent ID: {self.agentspace_id}")
        logger.info(f"📊 Datastore ID: {self.datastore_id}")
        logger.info(f"☁️ Project: {self.project_id}")
        logger.info(f"✨ Nova Framework: Ready for production!")
        
        return True

async def main():
    """Main test function"""
    test = AgentspaceIntegrationTest()
    success = await test.run_full_test()
    return success

if __name__ == "__main__":
    success = asyncio.run(main())
    exit(0 if success else 1)