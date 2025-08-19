#!/usr/bin/env python3
"""
Agent Cleanup Script for Google Cloud Platform
Cleans up old agents from various Google Cloud AI services including:
- ReasoningEngines (Vertex AI)
- Discovery Engine agents  
- Dialogflow agents
- Test agents and orphaned resources
"""

import asyncio
import json
import logging
import os
import subprocess
import sys
from typing import Dict, List, Any
import requests

# Setup logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger("agent_cleanup")

class AgentCleanup:
    """Comprehensive agent cleanup utility"""
    
    def __init__(self, project_id: str = "threatexplainer", location: str = "us-central1"):
        self.project_id = project_id
        self.project_number = "658179545428"  # Known from API responses
        self.location = location
        self.global_location = "global"
        
        # Set credentials
        self.credentials_path = "/Users/cbernal/Downloads/threatexplainer-1185aa9fcd44.json"
        os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = self.credentials_path
        
        # Track what we delete
        self.deleted_items = []
        self.failed_deletions = []
    
    def get_access_token(self) -> str:
        """Get Google Cloud access token"""
        try:
            result = subprocess.run([
                'gcloud', 'auth', 'application-default', 'print-access-token'
            ], capture_output=True, text=True)
            
            if result.returncode == 0:
                return result.stdout.strip()
            else:
                raise Exception(f"Failed to get access token: {result.stderr}")
                
        except Exception as e:
            logger.error(f"Error getting access token: {str(e)}")
            raise
    
    def make_request(self, method: str, url: str, **kwargs) -> requests.Response:
        """Make authenticated API request"""
        headers = {
            'Authorization': f'Bearer {self.get_access_token()}',
            'Content-Type': 'application/json'
        }
        
        return requests.request(method, url, headers=headers, **kwargs)
    
    def list_reasoning_engines(self) -> List[Dict[str, Any]]:
        """List all ReasoningEngines"""
        logger.info("Listing ReasoningEngines...")
        
        try:
            url = f"https://aiplatform.googleapis.com/v1beta1/projects/{self.project_number}/locations/{self.location}/reasoningEngines"
            response = self.make_request('GET', url)
            
            if response.status_code == 200:
                data = response.json()
                engines = data.get('reasoningEngines', [])
                logger.info(f"Found {len(engines)} ReasoningEngines")
                return engines
            else:
                logger.error(f"Failed to list ReasoningEngines: {response.status_code} - {response.text}")
                return []
                
        except Exception as e:
            logger.error(f"Error listing ReasoningEngines: {str(e)}")
            return []
    
    def delete_reasoning_engine(self, engine_id: str, force: bool = True) -> bool:
        """Delete a ReasoningEngine"""
        logger.info(f"Deleting ReasoningEngine: {engine_id}")
        
        try:
            url = f"https://aiplatform.googleapis.com/v1beta1/projects/{self.project_number}/locations/{self.location}/reasoningEngines/{engine_id}"
            if force:
                url += "?force=true"
            
            response = self.make_request('DELETE', url)
            
            if response.status_code == 200:
                result = response.json()
                if result.get('done', False):
                    logger.info(f"✅ Successfully deleted ReasoningEngine: {engine_id}")
                    self.deleted_items.append(f"ReasoningEngine:{engine_id}")
                    return True
                else:
                    logger.info(f"⏳ ReasoningEngine deletion started: {engine_id}")
                    self.deleted_items.append(f"ReasoningEngine:{engine_id}:pending")
                    return True
            else:
                logger.error(f"Failed to delete ReasoningEngine {engine_id}: {response.status_code} - {response.text}")
                self.failed_deletions.append(f"ReasoningEngine:{engine_id}:{response.status_code}")
                return False
                
        except Exception as e:
            logger.error(f"Error deleting ReasoningEngine {engine_id}: {str(e)}")
            self.failed_deletions.append(f"ReasoningEngine:{engine_id}:error")
            return False
    
    def list_discovery_engines(self) -> List[Dict[str, Any]]:
        """List Discovery Engine agents"""
        logger.info("Listing Discovery Engine agents...")
        
        try:
            url = f"https://discoveryengine.googleapis.com/v1/projects/{self.project_id}/locations/{self.global_location}/collections/default_collection/engines"
            response = self.make_request('GET', url)
            
            if response.status_code == 200:
                data = response.json()
                engines = data.get('engines', [])
                logger.info(f"Found {len(engines)} Discovery Engine agents")
                return engines
            else:
                logger.error(f"Failed to list Discovery engines: {response.status_code} - {response.text}")
                return []
                
        except Exception as e:
            logger.error(f"Error listing Discovery engines: {str(e)}")
            return []
    
    def delete_discovery_engine(self, engine_id: str) -> bool:
        """Delete a Discovery Engine agent"""
        logger.info(f"Deleting Discovery Engine: {engine_id}")
        
        try:
            url = f"https://discoveryengine.googleapis.com/v1/projects/{self.project_number}/locations/{self.global_location}/collections/default_collection/engines/{engine_id}"
            response = self.make_request('DELETE', url)
            
            if response.status_code == 200:
                result = response.json()
                if result.get('done', False):
                    logger.info(f"✅ Successfully deleted Discovery Engine: {engine_id}")
                    self.deleted_items.append(f"DiscoveryEngine:{engine_id}")
                    return True
                else:
                    logger.info(f"⏳ Discovery Engine deletion started: {engine_id}")
                    self.deleted_items.append(f"DiscoveryEngine:{engine_id}:pending")
                    return True
            else:
                logger.error(f"Failed to delete Discovery Engine {engine_id}: {response.status_code} - {response.text}")
                self.failed_deletions.append(f"DiscoveryEngine:{engine_id}:{response.status_code}")
                return False
                
        except Exception as e:
            logger.error(f"Error deleting Discovery Engine {engine_id}: {str(e)}")
            self.failed_deletions.append(f"DiscoveryEngine:{engine_id}:error")
            return False
    
    def list_dialogflow_agents(self) -> List[Dict[str, Any]]:
        """List Dialogflow agents"""
        logger.info("Listing Dialogflow agents...")
        
        try:
            url = f"https://dialogflow.googleapis.com/v3/projects/{self.project_id}/locations/{self.global_location}/agents"
            response = self.make_request('GET', url)
            
            if response.status_code == 200:
                data = response.json()
                agents = data.get('agents', [])
                logger.info(f"Found {len(agents)} Dialogflow agents")
                return agents
            else:
                logger.error(f"Failed to list Dialogflow agents: {response.status_code} - {response.text}")
                return []
                
        except Exception as e:
            logger.error(f"Error listing Dialogflow agents: {str(e)}")
            return []
    
    def cleanup_test_agents(self, dry_run: bool = False) -> Dict[str, Any]:
        """Clean up test and old agents"""
        logger.info(f"Starting agent cleanup (dry_run={dry_run})...")
        
        # Keep track of what we preserve
        preserved_agents = []
        
        # 1. Clean up ReasoningEngines
        reasoning_engines = self.list_reasoning_engines()
        for engine in reasoning_engines:
            engine_id = engine['name'].split('/')[-1]
            display_name = engine.get('displayName', 'Unknown')
            
            # Delete all ReasoningEngines (they were the BEAM agents)
            if not dry_run:
                self.delete_reasoning_engine(engine_id)
            else:
                logger.info(f"[DRY RUN] Would delete ReasoningEngine: {engine_id} ({display_name})")
        
        # 2. Check Discovery Engine agents - preserve our Nova agent
        discovery_engines = self.list_discovery_engines()
        for engine in discovery_engines:
            engine_id = engine['name'].split('/')[-1]
            display_name = engine.get('displayName', 'Unknown')
            
            # Preserve our Nova agent
            if engine_id == "agentspace-1754331730713_1754331730714":
                logger.info(f"✅ Preserving Nova agent: {display_name}")
                preserved_agents.append(f"DiscoveryEngine:{engine_id}:{display_name}")
            elif 'test' in display_name.lower() or 'test' in engine_id.lower():
                # Delete test agents
                if not dry_run:
                    self.delete_discovery_engine(engine_id)
                else:
                    logger.info(f"[DRY RUN] Would delete Discovery Engine: {engine_id} ({display_name})")
            else:
                # Preserve production agents
                logger.info(f"✅ Preserving production agent: {display_name}")
                preserved_agents.append(f"DiscoveryEngine:{engine_id}:{display_name}")
        
        # 3. List Dialogflow agents (usually don't delete these)
        dialogflow_agents = self.list_dialogflow_agents()
        for agent in dialogflow_agents:
            agent_id = agent['name'].split('/')[-1]
            display_name = agent.get('displayName', 'Unknown')
            logger.info(f"📋 Dialogflow agent found: {display_name} (preserved)")
            preserved_agents.append(f"DialogflowAgent:{agent_id}:{display_name}")
        
        return {
            "dry_run": dry_run,
            "deleted_items": self.deleted_items,
            "failed_deletions": self.failed_deletions,
            "preserved_agents": preserved_agents,
            "summary": {
                "total_deleted": len(self.deleted_items),
                "total_failed": len(self.failed_deletions),
                "total_preserved": len(preserved_agents)
            }
        }
    
    def cleanup_all_agents(self, confirm: bool = False) -> Dict[str, Any]:
        """Clean up ALL agents (dangerous!)"""
        if not confirm:
            logger.warning("This will delete ALL agents! Use confirm=True if you're sure.")
            return {"error": "Confirmation required"}
        
        logger.warning("⚠️  DELETING ALL AGENTS! This cannot be undone!")
        
        # Delete everything
        reasoning_engines = self.list_reasoning_engines()
        for engine in reasoning_engines:
            engine_id = engine['name'].split('/')[-1]
            self.delete_reasoning_engine(engine_id)
        
        discovery_engines = self.list_discovery_engines()
        for engine in discovery_engines:
            engine_id = engine['name'].split('/')[-1]
            self.delete_discovery_engine(engine_id)
        
        return {
            "deleted_items": self.deleted_items,
            "failed_deletions": self.failed_deletions,
            "warning": "ALL agents were deleted!"
        }

async def main():
    """Main cleanup function"""
    import argparse
    
    parser = argparse.ArgumentParser(description='Cleanup Google Cloud AI agents')
    parser.add_argument('--dry-run', action='store_true', help='Show what would be deleted without actually deleting')
    parser.add_argument('--all', action='store_true', help='Delete ALL agents (dangerous!)')
    parser.add_argument('--confirm', action='store_true', help='Confirm destructive operations')
    parser.add_argument('--project', default='threatexplainer', help='Google Cloud project ID')
    
    args = parser.parse_args()
    
    cleanup = AgentCleanup(project_id=args.project)
    
    print("🧹 Google Cloud Agent Cleanup Utility")
    print("=" * 40)
    
    if args.all:
        if not args.confirm:
            print("⚠️  WARNING: --all flag requires --confirm to proceed")
            sys.exit(1)
        result = cleanup.cleanup_all_agents(confirm=True)
    else:
        result = cleanup.cleanup_test_agents(dry_run=args.dry_run)
    
    print("\n📊 Cleanup Results:")
    print("=" * 40)
    print(json.dumps(result, indent=2))
    
    if result.get("summary"):
        summary = result["summary"]
        print(f"\n✅ Deleted: {summary['total_deleted']}")
        print(f"❌ Failed: {summary['total_failed']}")
        print(f"🔒 Preserved: {summary['total_preserved']}")
    
    print("\n🎉 Cleanup completed!")

if __name__ == "__main__":
    asyncio.run(main())