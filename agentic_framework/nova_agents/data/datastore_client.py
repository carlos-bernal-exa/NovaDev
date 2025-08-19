import asyncio
import json
import logging
import os
from typing import Dict, Any, List, Optional
from datetime import datetime
from google.cloud import discoveryengine_v1
from google.oauth2 import service_account
from google.auth.transport.requests import Request
import vertexai
from vertexai import rag
from vertexai.generative_models import GenerativeModel, Tool

logger = logging.getLogger(__name__)

class NovaDataStoreClient:
    """
    Client for accessing Nova's knowledge base of BEAM Features and Correlation Rules.
    Provides search and retrieval capabilities for Exabeam detection rules.
    """
    
    def __init__(self, datastore_id: str = "content_1755237537757"):
        self.datastore_id = datastore_id
        self.logger = logging.getLogger("nova_datastore_client")
        self.project_id = os.getenv("GOOGLE_CLOUD_PROJECT", "threatexplainer")
        # Discovery Engine requires "global" location for search
        self.location = "global"
        
        # Use the correct engine ID from Agentspace
        self.search_engine_id = "agentspace-1754331730713_1754331730714"
        
        # Initialize Vertex AI RAG Engine 
        self._initialize_rag_engine()
        
        # Initialize Discovery Engine client (fallback)
        self._initialize_discovery_engine_client()
        
        # Keep sample data as fallback
        self._initialize_sample_data()
    
    def _initialize_rag_engine(self):
        """Initialize Vertex AI RAG Engine for real BEAM knowledge retrieval"""
        try:
            # Initialize Vertex AI
            vertexai.init(
                project=self.project_id,
                location="us-central1"  # RAG Engine uses us-central1
            )
            
            # Try to get the RAG corpus for BEAM data
            # The corpus name might be different - this is just an attempt
            self.rag_corpus_name = f"projects/{self.project_id}/locations/us-central1/ragCorpora/{self.datastore_id}"
            
            self.logger.info(f"Initialized Vertex AI RAG Engine for project: {self.project_id}")
            self.logger.info(f"RAG Corpus: {self.rag_corpus_name}")
            self.rag_enabled = True
            
        except Exception as e:
            self.logger.error(f"Failed to initialize RAG Engine: {str(e)}")
            self.rag_enabled = False
    
    async def _query_rag_corpus(self, query: str, limit: int = 10) -> Dict[str, Any]:
        """Query the RAG corpus for BEAM rule information"""
        try:
            if not self.rag_enabled:
                raise Exception("RAG Engine not initialized")
            
            # Create a retrieval query
            from vertexai import rag
            
            retrieval_tool = Tool.from_retrieval(
                retrieval=rag.Retrieval(
                    source=rag.VertexRagStore(
                        rag_resources=[rag.RagResource(
                            rag_corpus=self.rag_corpus_name
                        )],
                    ),
                )
            )
            
            # Use Gemini with RAG retrieval
            model = GenerativeModel(
                model_name="gemini-1.5-pro",
                tools=[retrieval_tool],
            )
            
            # Generate response with retrieval
            response = model.generate_content(
                f"Find BEAM rules and information related to: {query}. "
                f"Focus on rule specifications, CIM fields, detection logic, and technical details.",
                generation_config={"temperature": 0.1}
            )
            
            # Process the response and extract retrieved documents
            results = []
            if hasattr(response, 'candidates') and response.candidates:
                candidate = response.candidates[0]
                
                # Extract grounding metadata if available
                if hasattr(candidate, 'grounding_metadata'):
                    for grounding in candidate.grounding_metadata.retrieval_metadata:
                        for source in grounding.sources:
                            results.append({
                                "id": source.uri.split('/')[-1] if source.uri else "unknown",
                                "name": getattr(source, 'title', 'BEAM Rule'),
                                "content": {
                                    "text": getattr(source, 'content', ''),
                                    "uri": source.uri
                                },
                                "source": "rag_engine"
                            })
                
                # If no grounding metadata, use the response text
                if not results and hasattr(candidate, 'content'):
                    results.append({
                        "id": "rag_response",
                        "name": "RAG Generated Response",
                        "content": {
                            "text": candidate.content.parts[0].text,
                            "generated": True
                        },
                        "source": "rag_engine"
                    })
            
            return {
                "query": query,
                "results": results,
                "total_found": len(results),
                "datastore_id": self.datastore_id,
                "source": "rag_engine"
            }
            
        except Exception as e:
            self.logger.error(f"RAG corpus query failed: {str(e)}")
            raise
    
    def _initialize_discovery_engine_client(self):
        """Initialize the Discovery Engine client for real datastore access"""
        try:
            # Use service account if available
            service_account_path = os.getenv('GOOGLE_APPLICATION_CREDENTIALS')
            if service_account_path and os.path.exists(service_account_path):
                credentials = service_account.Credentials.from_service_account_file(
                    service_account_path,
                    scopes=['https://www.googleapis.com/auth/cloud-platform']
                )
                self.search_client = discoveryengine_v1.SearchServiceClient(credentials=credentials)
                self.logger.info(f"Initialized Discovery Engine client with service account: {service_account_path}")
            else:
                # Use default credentials
                self.search_client = discoveryengine_v1.SearchServiceClient()
                self.logger.info("Initialized Discovery Engine client with default credentials")
            
            # Construct the serving config path for search using the correct engine ID
            self.serving_config = f"projects/{self.project_id}/locations/{self.location}/collections/default_collection/engines/{self.search_engine_id}/servingConfigs/default_config"
            self.logger.info(f"Using serving config: {self.serving_config}")
            
        except Exception as e:
            self.logger.error(f"Failed to initialize Discovery Engine client: {str(e)}")
            self.search_client = None
            self.serving_config = None
    
    async def _search_discovery_engine(self, query: str, limit: int = 10) -> Dict[str, Any]:
        """Search the Discovery Engine datastore for BEAM content"""
        try:
            if not self.search_client or not self.serving_config:
                raise Exception("Discovery Engine client not initialized")
            
            # Create search request
            request = discoveryengine_v1.SearchRequest(
                serving_config=self.serving_config,
                query=query,
                page_size=limit,
                safe_search=False,
            )
            
            # Execute search
            response = self.search_client.search(request=request)
            
            # Process results
            results = []
            for result in response.results:
                document = result.document
                # Extract content from the document
                content = {}
                
                # Parse document data
                if hasattr(document, 'derived_struct_data') and document.derived_struct_data:
                    content.update(dict(document.derived_struct_data))
                
                if hasattr(document, 'struct_data') and document.struct_data:
                    content.update(dict(document.struct_data))
                
                # Extract snippets for context
                snippets = []
                if hasattr(result, 'document_snippets'):
                    for snippet in result.document_snippets:
                        if hasattr(snippet, 'snippet') and snippet.snippet:
                            snippets.append(snippet.snippet)
                
                result_entry = {
                    "id": document.id if hasattr(document, 'id') else document.name.split('/')[-1],
                    "name": document.name,
                    "content": content,
                    "snippets": snippets,
                    "uri": getattr(document, 'uri', ''),
                }
                
                results.append(result_entry)
            
            return {
                "query": query,
                "results": results,
                "total_found": len(results),
                "datastore_id": self.datastore_id,
                "source": "discovery_engine"
            }
            
        except Exception as e:
            self.logger.error(f"Discovery Engine search failed: {str(e)}")
            raise
    
    def _initialize_sample_data(self):
        """Initialize with sample BEAM Features and Correlation Rules"""
        
        # Sample BEAM Features
        self.beam_features = [
            {
                "id": "NumDCP-Auth-TgsEC-U-Sn",
                "name": "Kerberos TGS Error Count Anomaly Detection", 
                "rule_type": "numeric count profileFeature",
                "description": "Detects anomalous number of Kerberos TGS (Ticket Granting Service) error conditions per user, indicating potential lateral movement attempts or credential attacks",
                "applicable_events": ["authentication-failure"],
                "scope": "user",
                "training_condition": "activity_type = 'authentication-failure' and event_code = 4769 and logon_type = 3",
                "feature_value": "count(*)",
                "window_size": "1h",
                "window_stride": "15m",
                "anomaly_threshold": 0.1,
                "scope_maturity": 7,
                "feature_value_maturity": 5,
                "mitre_techniques": ["T1558.003", "T1078"],
                "use_cases": ["Lateral Movement", "Credential Access"],
                "cim_fields": ["user_name", "src_host", "dest_host", "event_code", "logon_type", "failure_reason"],
                "detection_logic": "Counts Kerberos TGS failures (event 4769) and triggers when user exceeds normal failure patterns",
                "tuning_guidance": "Exclude known service accounts and automated systems. Consider user behavior patterns and normal authentication flows."
            },
            {
                "id": "bf_lateral_movement_1",
                "name": "First Time Remote Access Tool Usage",
                "rule_type": "factFeature",
                "description": "Detects first-time usage of remote access tools like TeamViewer, AnyDesk",
                "applicable_events": ["process-create"],
                "actOnCondition": "process_name in ['teamviewer.exe', 'anydesk.exe', 'logmein.exe']",
                "mitre_techniques": ["T1219"],
                "use_cases": ["Lateral Movement", "Initial Access"]
            },
            {
                "id": "bf_lateral_movement_2", 
                "name": "Unusual Network Logon Locations",
                "rule_type": "profiledFeature",
                "description": "Detects user logons from unusual network locations",
                "applicable_events": ["authentication-success"],
                "scope": "user",
                "feature_value": "src_ip",
                "training_condition": "activity_type = 'authentication-success'",
                "anomaly_threshold": 0.1,
                "mitre_techniques": ["T1078"],
                "use_cases": ["Lateral Movement", "Credential Access"]
            },
            {
                "id": "bf_privilege_escalation_1",
                "name": "PowerShell Script Execution",
                "rule_type": "factFeature", 
                "description": "Detects suspicious PowerShell script execution patterns",
                "applicable_events": ["process-create"],
                "actOnCondition": "process_name = 'powershell.exe' and command_line contains '-enc'",
                "mitre_techniques": ["T1059.001"],
                "use_cases": ["Privilege Escalation", "Defense Evasion"]
            }
        ]
        
        # Sample Correlation Rules
        self.correlation_rules = [
            {
                "id": "cr_lateral_movement_1",
                "name": "Lateral Movement via SMB Admin Shares",
                "rule_type": "rule_sequence",
                "description": "Detects lateral movement using administrative SMB shares",
                "query": "authentication-success followed by file-access within 5 minutes",
                "condition": {"operator": "and", "time_window": "5m", "threshold": 1},
                "useCase": "Lateral Movement Detection",
                "mitre": ["T1021.002"],
                "outcomes": ["case_creation", "alerting"]
            },
            {
                "id": "cr_privilege_escalation_1", 
                "name": "Privilege Escalation via Service Creation",
                "rule_type": "rule_sequence",
                "description": "Detects privilege escalation through service creation",
                "query": "process-create where process_name = 'sc.exe' followed by service-start within 2 minutes",
                "condition": {"operator": "sequence", "time_window": "2m", "threshold": 1},
                "useCase": "Privilege Escalation",
                "mitre": ["T1543.003"],
                "outcomes": ["case_creation"]
            }
        ]
    
    async def search_beam_features(
        self,
        query: str,
        rule_types: List[str] = None,
        limit: int = 10
    ) -> Dict[str, Any]:
        """
        Search for BEAM Features in the data store.
        
        Args:
            query: Search query string
            rule_types: Optional list of rule types to filter by 
                       (factFeature, profiledFeature, contextFeature, etc.)
            limit: Maximum number of results to return
        
        Returns:
            Dictionary containing search results
        """
        try:
            self.logger.info(f"Searching BEAM features with query: {query}")
            
            # Try RAG Engine search first
            if self.rag_enabled:
                try:
                    search_results = await self._query_rag_corpus(query, limit)
                    if search_results and search_results["total_found"] > 0:
                        # Filter by rule types if specified
                        if rule_types:
                            filtered_results = []
                            for result in search_results["results"]:
                                result_content = result.get("content", {})
                                if result_content.get("rule_type") in rule_types:
                                    filtered_results.append(result)
                            search_results["results"] = filtered_results
                            search_results["total_found"] = len(filtered_results)
                        
                        return search_results
                except Exception as e:
                    self.logger.warning(f"RAG Engine search failed, trying Discovery Engine: {str(e)}")
            
            # Try Discovery Engine search as fallback
            if self.search_client and self.serving_config:
                try:
                    search_results = await self._search_discovery_engine(query, limit)
                    if search_results and search_results["total_found"] > 0:
                        # Filter by rule types if specified
                        if rule_types:
                            filtered_results = []
                            for result in search_results["results"]:
                                result_content = result.get("content", {})
                                if result_content.get("rule_type") in rule_types:
                                    filtered_results.append(result)
                            search_results["results"] = filtered_results
                            search_results["total_found"] = len(filtered_results)
                        
                        return search_results
                except Exception as e:
                    self.logger.warning(f"Discovery Engine search failed, using sample data: {str(e)}")
            
            # Fallback to sample BEAM features
            results = []
            query_lower = query.lower()
            
            for feature in self.beam_features:
                # Simple text matching on name, description, and use cases
                if (query_lower in feature["name"].lower() or 
                    query_lower in feature["description"].lower() or
                    any(query_lower in uc.lower() for uc in feature.get("use_cases", []))):
                    
                    # Filter by rule type if specified
                    if not rule_types or feature["rule_type"] in rule_types:
                        results.append(feature)
                        
                        if len(results) >= limit:
                            break
            
            return {
                "query": query,
                "results": results,
                "total_found": len(results),
                "datastore_id": self.datastore_id,
                "source": "sample_data"
            }
            
        except Exception as e:
            self.logger.error(f"Error searching BEAM features: {str(e)}")
            return {
                "query": query,
                "results": [],
                "total_found": 0,
                "error": str(e)
            }
    
    async def search_correlation_rules(
        self,
        query: str,
        use_cases: List[str] = None,
        mitre_techniques: List[str] = None,
        limit: int = 10
    ) -> Dict[str, Any]:
        """
        Search for Correlation Rules in the data store.
        
        Args:
            query: Search query string
            use_cases: Optional list of use cases to filter by
            mitre_techniques: Optional list of MITRE techniques to filter by
            limit: Maximum number of results to return
        
        Returns:
            Dictionary containing search results
        """
        try:
            self.logger.info(f"Searching correlation rules with query: {query}")
            
            # Search through sample correlation rules
            results = []
            query_lower = query.lower()
            
            for rule in self.correlation_rules:
                # Simple text matching on name, description, and use case
                if (query_lower in rule["name"].lower() or 
                    query_lower in rule["description"].lower() or
                    query_lower in rule.get("useCase", "").lower()):
                    
                    # Filter by use cases if specified
                    if not use_cases or any(uc in rule.get("useCase", "") for uc in use_cases):
                        # Filter by MITRE techniques if specified
                        if not mitre_techniques or any(mt in rule.get("mitre", []) for mt in mitre_techniques):
                            results.append(rule)
                            
                            if len(results) >= limit:
                                break
            
            return {
                "query": query,
                "results": results,
                "total_found": len(results),
                "datastore_id": self.datastore_id
            }
            
        except Exception as e:
            self.logger.error(f"Error searching correlation rules: {str(e)}")
            return {
                "query": query,
                "results": [],
                "total_found": 0,
                "error": str(e)
            }
    
    async def get_rule_by_id(self, rule_id: str) -> Optional[Dict[str, Any]]:
        """
        Get a specific rule by its ID.
        
        Args:
            rule_id: The unique identifier for the rule
        
        Returns:
            Rule data dictionary or None if not found
        """
        try:
            self.logger.info(f"Getting rule by ID: {rule_id}")
            
            # Try RAG Engine search first
            if self.rag_enabled:
                try:
                    search_results = await self._query_rag_corpus(f"rule ID {rule_id} OR rule name {rule_id} OR {rule_id}", limit=1)
                    if search_results and search_results["results"]:
                        return search_results["results"][0]
                except Exception as e:
                    self.logger.warning(f"RAG Engine search by ID failed, trying Discovery Engine: {str(e)}")
            
            # Try Discovery Engine search as fallback
            if self.search_client and self.serving_config:
                try:
                    search_results = await self._search_discovery_engine(f"id:{rule_id} OR rule_id:{rule_id} OR name:{rule_id}", limit=1)
                    if search_results and search_results["results"]:
                        return search_results["results"][0]
                except Exception as e:
                    self.logger.warning(f"Discovery Engine search by ID failed, using sample data: {str(e)}")
            
            # Fallback to sample data
            # Search in BEAM features
            for feature in self.beam_features:
                if feature["id"] == rule_id:
                    return feature
                    
            # Search in correlation rules
            for rule in self.correlation_rules:
                if rule["id"] == rule_id:
                    return rule
            
            return None
            
        except Exception as e:
            self.logger.error(f"Error getting rule by ID {rule_id}: {str(e)}")
            return None
    
    async def search_by_activity_type(
        self,
        activity_type: str,
        limit: int = 20
    ) -> Dict[str, Any]:
        """
        Search for rules by activity type (e.g., process-create, network-connect).
        
        Args:
            activity_type: The activity type to search for
            limit: Maximum number of results to return
        
        Returns:
            Dictionary containing search results
        """
        try:
            self.logger.info(f"Searching rules for activity type: {activity_type}")
            
            results = []
            
            # Search BEAM features by applicable events
            for feature in self.beam_features:
                if activity_type in feature.get("applicable_events", []):
                    results.append(feature)
                    if len(results) >= limit:
                        break
            
            return {
                "activity_type": activity_type,
                "results": results,
                "total_found": len(results),
                "datastore_id": self.datastore_id
            }
            
        except Exception as e:
            self.logger.error(f"Error searching by activity type {activity_type}: {str(e)}")
            return {
                "activity_type": activity_type,
                "results": [],
                "total_found": 0,
                "error": str(e)
            }
    
    def get_all_beam_features(self) -> List[Dict[str, Any]]:
        """Get all available BEAM features"""
        return self.beam_features.copy()
    
    def get_all_correlation_rules(self) -> List[Dict[str, Any]]:
        """Get all available correlation rules"""
        return self.correlation_rules.copy()
    
    def get_datastore_info(self) -> Dict[str, Any]:
        """Get information about the knowledge base"""
        return {
            "datastore_id": self.datastore_id,
            "content_types": ["beam_feature", "correlation_rule"],
            "beam_features_count": len(self.beam_features),
            "correlation_rules_count": len(self.correlation_rules),
            "supported_rule_types": [
                "factFeature",
                "profiledFeature", 
                "contextFeature",
                "numeric count profileFeature",
                "numeric distinct count profileFeature", 
                "numeric sum profileFeature",
                "rule_sequence"
            ]
        }