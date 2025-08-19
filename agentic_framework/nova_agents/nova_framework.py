import asyncio
import logging
from typing import Dict, Any, List, Optional
from google.adk.agents.invocation_context import InvocationContext
from google.adk.agents.run_config import RunConfig
from google.adk.sessions import Session
from google.adk.sessions.base_session_service import BaseSessionService
from google.adk.plugins.plugin_manager import PluginManager
from google.genai import types
import os
from dotenv import load_dotenv
import google.cloud.aiplatform as aiplatform

from agents.routing_agent import NovaRoutingAgent
from agents.knowledge_agent import NovaKnowledgeAgent
from data.datastore_client import NovaDataStoreClient

load_dotenv()

class NovaFramework:
    """
    Nova AI Framework for Exabeam BEAM rule explanation and exclusion creation.
    Implements the coordinator/dispatcher pattern with specialized routing.
    """

    def __init__(self, datastore_id: str = "nova_knowledge_base"):
        self.logger = logging.getLogger("nova_framework")
        self.setup_logging()

        self.setup_vertex_ai()
        
        self.datastore_id = datastore_id
        self.datastore_client = NovaDataStoreClient(datastore_id=datastore_id)

        self.knowledge_agent = NovaKnowledgeAgent(datastore_id=datastore_id)
        self.routing_agent = NovaRoutingAgent(self.knowledge_agent)

        self.logger.info("Nova Framework initialized successfully")

    def setup_logging(self):
        """Setup logging configuration"""
        log_level = os.getenv("LOG_LEVEL", "INFO")
        logging.basicConfig(
            level=getattr(logging, log_level),
            format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
        )

    def setup_vertex_ai(self):
        """Setup Vertex AI credentials and initialize"""
        # First try to use gcloud user credentials
        try:
            # Get project from gcloud config
            import subprocess
            result = subprocess.run(['gcloud', 'config', 'get-value', 'project'], 
                                  capture_output=True, text=True)
            if result.returncode == 0 and result.stdout.strip():
                project_id = result.stdout.strip()
                self.logger.info(f"Using gcloud project: {project_id}")
                
                # Initialize Vertex AI with user credentials
                aiplatform.init(
                    project=project_id,
                    location="us-central1"
                )
                self.project_id = project_id
                self.location = "us-central1"
                self.logger.info(f"Vertex AI initialized with gcloud user credentials")
                return
            
        except Exception as e:
            self.logger.warning(f"Could not use gcloud credentials: {str(e)}")
        
        # Fallback to service account credentials
        credentials_path = os.getenv("GOOGLE_APPLICATION_CREDENTIALS", "./vertex_ai_credentials.json")
        
        if os.path.exists(credentials_path):
            os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = credentials_path
            
            import json
            with open(credentials_path, 'r') as f:
                creds = json.load(f)
                project_id = creds.get('project_id')
            
            if project_id:
                aiplatform.init(
                    project=project_id,
                    location="us-central1"
                )
                self.project_id = project_id
                self.location = "us-central1"
                self.logger.info(f"Vertex AI initialized with service account: {project_id}")
            else:
                self.logger.warning("No project_id found in credentials")
                self.project_id = None
                self.location = None
        else:
            self.logger.warning("Vertex AI credentials not found")
            self.project_id = None
            self.location = None

    async def process_query(self, user_query: str, session_id: str = None) -> str:
        """
        Process a user query through the Nova framework.
        Routes query to appropriate mode via the routing agent.
        """
        self.logger.info(f"Processing Nova query: {user_query[:100]}...")

        try:
            session = Session(
                id=session_id or f"nova_session_{int(asyncio.get_event_loop().time())}",
                appName="NovaFramework",
                userId="nova_user"
            )
            
            class NovaSessionService(BaseSessionService):
                async def create_session(self, session: Session) -> Session:
                    return session
                
                async def delete_session(self, session_id: str) -> None:
                    pass
                
                async def get_session(self, session_id: str) -> Session:
                    return session
                
                async def list_sessions(self, user_id: str = None) -> List[Session]:
                    return [session]
            
            session_service = NovaSessionService()
            
            run_config = RunConfig(
                response_modalities=["TEXT"],
                max_llm_calls=10
            )
            
            # Create proper InvocationContext
            context = InvocationContext(
                agent=self.routing_agent,
                session=session,
                session_service=session_service,
                invocation_id=f"nova_invocation_{int(asyncio.get_event_loop().time())}",
                user_content=types.Content(parts=[types.Part(text=user_query)]),
                plugin_manager=PluginManager(),
                run_config=run_config
            )
            
            response_events = []
            async for event in self.routing_agent.run_async(context):
                response_events.append(event)
                self.logger.debug(f"Event from {event.author}: {event.content}")
            
            if response_events:
                final_event = response_events[-1]
                return str(final_event.content)
            else:
                return "No response generated"

        except Exception as e:
            self.logger.error(f"Error processing Nova query: {str(e)}")
            return f"Error processing query: {str(e)}"

    async def search_beam_features(self, query: str, rule_types: List[str] = None) -> Dict[str, Any]:
        """Search for BEAM Features directly via data store client"""
        self.logger.info(f"Searching BEAM features: {query}")
        
        try:
            return await self.datastore_client.search_beam_features(
                query=query, 
                rule_types=rule_types
            )
        except Exception as e:
            self.logger.error(f"Error searching BEAM features: {str(e)}")
            return {"error": str(e), "results": []}

    async def search_correlation_rules(self, query: str, use_cases: List[str] = None) -> Dict[str, Any]:
        """Search for Correlation Rules directly via data store client"""
        self.logger.info(f"Searching correlation rules: {query}")
        
        try:
            return await self.datastore_client.search_correlation_rules(
                query=query, 
                use_cases=use_cases
            )
        except Exception as e:
            self.logger.error(f"Error searching correlation rules: {str(e)}")
            return {"error": str(e), "results": []}

    async def get_rule_by_id(self, rule_id: str) -> Optional[Dict[str, Any]]:
        """Get a specific rule by ID"""
        self.logger.info(f"Getting rule by ID: {rule_id}")
        
        try:
            return await self.datastore_client.get_rule_by_id(rule_id)
        except Exception as e:
            self.logger.error(f"Error getting rule by ID: {str(e)}")
            return None

    async def test_datastore_connection(self) -> Dict[str, Any]:
        """Test Nova knowledge base functionality"""
        self.logger.info("Testing Nova knowledge base")

        try:
            # Test search functionality with sample data
            test_result = await self.datastore_client.search_beam_features(
                query="lateral movement",
                limit=5
            )
            
            info = self.datastore_client.get_datastore_info()
            
            return {
                "test_passed": True,
                "datastore_id": self.datastore_id,
                "connection_status": "connected",
                "beam_features_available": info["beam_features_count"],
                "correlation_rules_available": info["correlation_rules_count"],
                "test_query_results": len(test_result.get("results", []))
            }

        except Exception as e:
            self.logger.error(f"Knowledge base test failed: {str(e)}")
            return {
                "test_passed": False,
                "error": str(e),
                "datastore_id": self.datastore_id
            }

    def set_knowledge_agent_mode(self, mode: str):
        """Set the knowledge agent operation mode"""
        try:
            self.knowledge_agent.set_mode(mode)
            self.logger.info(f"Knowledge agent mode set to: {mode}")
        except ValueError as e:
            self.logger.error(f"Invalid mode: {str(e)}")
            raise

    def get_framework_status(self) -> Dict[str, Any]:
        """Get current Nova framework status"""
        return {
            "routing_agent": {
                "name": self.routing_agent.name,
                "available_modes": self.routing_agent.get_available_modes()
            },
            "knowledge_agent": {
                "name": self.knowledge_agent.name,
                "current_mode": self.knowledge_agent.current_mode,
                "mode_info": self.knowledge_agent.get_mode_info()
            },
            "datastore": {
                "datastore_id": self.datastore_id,
                "info": self.datastore_client.get_datastore_info()
            },
            "vertex_ai_configured": bool(os.getenv("GOOGLE_APPLICATION_CREDENTIALS")),
            "framework_type": "Nova AI Framework"
        }