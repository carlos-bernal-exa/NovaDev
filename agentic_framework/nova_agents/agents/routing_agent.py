from typing import Dict, Any, List
from google.adk.agents import LlmAgent
from google.adk.agents.invocation_context import InvocationContext
from google.adk.events import Event
import logging

logger = logging.getLogger(__name__)

class NovaRoutingAgent(LlmAgent):
    """
    Nova routing agent that determines user intent and routes to the appropriate Nova knowledge agent.
    Specializes in routing queries about BEAM Features, Correlation Rules, and exclusion creation.
    """
    
    def __init__(self, knowledge_agent: 'NovaKnowledgeAgent', **kwargs):
        instruction = """
You are Nova's routing agent within Exabeam's agentic framework. Your role is to analyze user queries and immediately route them to the appropriate knowledge base mode.

You MUST route ALL queries to the NovaKnowledge agent with one of two modes:

1. **DETECTION_EXPLANATION_MODE** - For queries about:
   - Understanding how BEAM Features work
   - Explaining Correlation Rules  
   - Learning about detection logic
   - Questions about rule types (factFeature, profiledFeature, contextFeature, correlation rules)
   - MITRE ATT&CK technique mappings
   - Security detection explanations
   - Any "how does X work" or "what does X detect" questions

2. **EXCLUSION_CREATION_MODE** - For queries about:
   - Creating rule exclusions
   - Reducing false positives
   - Crafting BEAM expressions
   - Tuning noisy rules
   - Building exclusion logic
   - Using BEAM functions and expressions

Routing Logic:
- Detection/explanation queries → DETECTION_EXPLANATION_MODE
- False positive/exclusion queries → EXCLUSION_CREATION_MODE
- When in doubt → DETECTION_EXPLANATION_MODE

YOU MUST ALWAYS ROUTE. Never ask for clarification. Immediately transfer to the NovaKnowledge agent.
"""
        
        super().__init__(
            name="NovaRouting",
            description="Routes Nova queries to appropriate knowledge base mode based on user intent",
            model="gemini-2.5-flash",
            instruction=instruction,
            sub_agents=[knowledge_agent],
            **kwargs
        )
        
        object.__setattr__(self, '_knowledge_agent', knowledge_agent)
        object.__setattr__(self, '_logger', logging.getLogger("nova_routing_agent"))
    
    @property
    def knowledge_agent(self) -> 'NovaKnowledgeAgent':
        """Get the Nova knowledge agent"""
        return getattr(self, '_knowledge_agent')
    
    @property
    def logger(self):
        """Get the logger for this agent"""
        return getattr(self, '_logger', logging.getLogger("nova_routing_agent"))
    
    def get_available_modes(self) -> Dict[str, str]:
        """Get available routing modes"""
        return {
            "DETECTION_EXPLANATION_MODE": "Explains how BEAM Features and Correlation Rules work",
            "EXCLUSION_CREATION_MODE": "Helps create exclusions and reduce false positives"
        }