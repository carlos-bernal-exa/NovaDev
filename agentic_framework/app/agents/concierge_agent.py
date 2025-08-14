from typing import Dict, Any, Optional, List, AsyncGenerator
from google.adk.agents import LlmAgent
from google.adk.agents.invocation_context import InvocationContext
from google.adk.events import Event
from app.agents.base_agent import SpecializedAgent
import logging

logger = logging.getLogger(__name__)

class ConciergeAgent(LlmAgent):
    """
    Concierge agent that detects user intents and routes to appropriate specialized agents.
    Uses LLM-driven delegation pattern from ADK documentation.
    """
    
    def __init__(self, specialized_agents: List['SpecializedAgent'], **kwargs):
        agent_descriptions = []
        for agent in specialized_agents:
            agent_descriptions.append(f"- {agent.name}: {agent.description} (domain: {agent.domain})")
        
        agents_info = "\n".join(agent_descriptions)
        
        instruction = f"""
You are a concierge agent that routes user requests to specialized agents based on intent detection.

Available specialized agents:
{agents_info}

Your job is to:
1. Analyze the user's request to understand their intent
2. Determine which specialized agent is best suited to handle the request
3. Use the transfer_to_agent function to route the request to the appropriate agent

Guidelines for routing:
- For security-related questions, route to security agents
- For threat analysis, route to threat analysis agents  
- For general information, route to information agents
- If unsure, ask clarifying questions before routing

Always explain why you're routing to a specific agent.
"""
        
        super().__init__(
            name="Concierge",
            description="Routes user requests to appropriate specialized agents based on intent detection",
            model="gemini-2.0-flash",
            instruction=instruction,
            sub_agents=specialized_agents,
            **kwargs
        )
        
        object.__setattr__(self, '_specialized_agents', {agent.name: agent for agent in specialized_agents})
        object.__setattr__(self, '_logger', logging.getLogger("concierge_agent"))
    
    @property
    def specialized_agents(self) -> Dict[str, 'SpecializedAgent']:
        """Get the specialized agents dictionary"""
        return getattr(self, '_specialized_agents', {})
    
    @property
    def logger(self):
        """Get the logger for this agent"""
        return getattr(self, '_logger', logging.getLogger("concierge_agent"))
    
    def add_specialized_agent(self, agent: 'SpecializedAgent'):
        """Add a new specialized agent to the concierge's routing options"""
        specialized_agents = getattr(self, '_specialized_agents', {})
        specialized_agents[agent.name] = agent
        if agent not in self.sub_agents:
            self.sub_agents.append(agent)
        self.logger.info(f"Added specialized agent: {agent.name}")
    
    def get_available_agents(self) -> Dict[str, str]:
        """Get a dictionary of available agents and their descriptions"""
        return {
            name: agent.description 
            for name, agent in self.specialized_agents.items()
        }
