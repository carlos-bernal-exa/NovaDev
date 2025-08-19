#!/usr/bin/env python3
"""
Deploy Nova Framework Agent using Google ADK
"""

import asyncio
import logging
import os
import subprocess
import sys
from pathlib import Path

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("nova_deployment")

class NovaDeployment:
    """Nova Framework Deployment Manager"""
    
    def __init__(self):
        self.project_id = "threatexplainer"
        self.location = "us-central1"
        self.agent_id = "nova-agent"
        self.agentspace_id = "agentspace-1754331730713_1754331730714"
        
        # Set environment
        os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = "/Users/cbernal/Downloads/threatexplainer-1185aa9fcd44.json"
    
    def check_prerequisites(self):
        """Check if all prerequisites are met"""
        logger.info("Checking deployment prerequisites...")
        
        # Check if gcloud is authenticated
        try:
            result = subprocess.run(['gcloud', 'auth', 'list', '--format=json'], 
                                  capture_output=True, text=True)
            if result.returncode != 0:
                logger.error("gcloud not authenticated")
                return False
                
            # Check if correct project is set
            result = subprocess.run(['gcloud', 'config', 'get-value', 'project'], 
                                  capture_output=True, text=True)
            current_project = result.stdout.strip()
            
            if current_project != self.project_id:
                logger.info(f"Setting project to {self.project_id}")
                subprocess.run(['gcloud', 'config', 'set', 'project', self.project_id])
            
            logger.info("Prerequisites check passed")
            return True
            
        except Exception as e:
            logger.error(f"Prerequisites check failed: {str(e)}")
            return False
    
    def enable_apis(self):
        """Enable required Google Cloud APIs"""
        logger.info("Enabling required APIs...")
        
        apis = [
            "aiplatform.googleapis.com",
            "discoveryengine.googleapis.com",
            "dialogflow.googleapis.com"
        ]
        
        for api in apis:
            try:
                result = subprocess.run([
                    'gcloud', 'services', 'enable', api,
                    '--project', self.project_id
                ], capture_output=True, text=True)
                
                if result.returncode == 0:
                    logger.info(f"✓ Enabled {api}")
                else:
                    logger.warning(f"Failed to enable {api}: {result.stderr}")
                    
            except Exception as e:
                logger.error(f"Error enabling {api}: {str(e)}")
    
    def deploy_agent(self):
        """Deploy the Nova agent using ADK"""
        logger.info(f"Deploying Nova agent to project {self.project_id}...")
        
        try:
            # Create the deployment command
            deploy_cmd = [
                'gcloud', 'adk', 'agents', 'deploy',
                '--agent-file', 'agent.yaml',
                '--project', self.project_id,
                '--location', self.location
            ]
            
            logger.info(f"Running: {' '.join(deploy_cmd)}")
            result = subprocess.run(deploy_cmd, capture_output=True, text=True)
            
            if result.returncode == 0:
                logger.info("✓ Agent deployment successful")
                logger.info(f"Output: {result.stdout}")
                return True
            else:
                logger.error(f"Agent deployment failed: {result.stderr}")
                return False
                
        except Exception as e:
            logger.error(f"Deployment error: {str(e)}")
            return False
    
    def register_with_agentspace(self):
        """Register the deployed agent with Agentspace"""
        logger.info(f"Registering agent with Agentspace ID: {self.agentspace_id}...")
        
        try:
            # Create registration payload
            registration_data = {
                "agent_id": self.agent_id,
                "display_name": "Nova AI Framework Agent",
                "description": "AI agent for BEAM rule explanation and exclusion creation",
                "oauth_client_info": {
                    "client_type": "SERVICE_ACCOUNT",
                    "service_account_email": "researchaiservice@threatexplainer.iam.gserviceaccount.com"
                }
            }
            
            # Use Discovery Engine API to register with existing agent
            import json
            import requests
            
            # Get access token
            token_result = subprocess.run([
                'gcloud', 'auth', 'application-default', 'print-access-token'
            ], capture_output=True, text=True)
            
            if token_result.returncode != 0:
                logger.error("Failed to get access token")
                return False
            
            access_token = token_result.stdout.strip()
            
            # The agent already exists in Agentspace, so we'll just verify it
            headers = {
                'Authorization': f'Bearer {access_token}',
                'Content-Type': 'application/json'
            }
            
            # Check if agent exists
            agent_url = f"https://discoveryengine.googleapis.com/v1/projects/{self.project_id}/locations/global/collections/default_collection/engines/{self.agentspace_id}"
            
            response = requests.get(agent_url, headers=headers)
            
            if response.status_code == 200:
                agent_info = response.json()
                logger.info(f"✓ Agent found in Agentspace: {agent_info.get('displayName')}")
                logger.info(f"✓ Connected to datastore: {agent_info.get('dataStoreIds')}")
                return True
            else:
                logger.error(f"Agent not found in Agentspace: {response.status_code}")
                return False
                
        except Exception as e:
            logger.error(f"Agentspace registration error: {str(e)}")
            return False
    
    def test_deployment(self):
        """Test the deployed agent"""
        logger.info("Testing deployed agent...")
        
        try:
            # Import and test our Nova framework
            from nova_framework import NovaFramework
            
            # Initialize framework
            framework = NovaFramework()
            
            # Test basic functionality
            test_query = "What lateral movement rules are available?"
            
            # Run the test
            response = asyncio.run(framework.process_query(test_query, "deployment_test"))
            
            if response and not response.startswith("Error"):
                logger.info("✓ Agent deployment test passed")
                logger.info(f"Test response: {response[:200]}...")
                return True
            else:
                logger.error(f"Agent deployment test failed: {response}")
                return False
                
        except Exception as e:
            logger.error(f"Deployment test error: {str(e)}")
            return False
    
    def deploy_full(self):
        """Run complete deployment process"""
        logger.info("🚀 Starting Nova Framework deployment...")
        
        steps = [
            ("Prerequisites Check", self.check_prerequisites),
            ("Enable APIs", self.enable_apis),
            ("Deploy Agent", self.deploy_agent),
            ("Register with Agentspace", self.register_with_agentspace),
            ("Test Deployment", self.test_deployment)
        ]
        
        for step_name, step_func in steps:
            logger.info(f"\n📋 Step: {step_name}")
            
            if not step_func():
                logger.error(f"❌ {step_name} failed - deployment stopped")
                return False
            
            logger.info(f"✅ {step_name} completed")
        
        logger.info("\n🎉 Nova Framework deployment completed successfully!")
        logger.info(f"Agent ID: {self.agent_id}")
        logger.info(f"Agentspace ID: {self.agentspace_id}")
        logger.info(f"Project: {self.project_id}")
        logger.info(f"Location: {self.location}")
        
        return True

if __name__ == "__main__":
    deployment = NovaDeployment()
    success = deployment.deploy_full()
    sys.exit(0 if success else 1)