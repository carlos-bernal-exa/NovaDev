from abc import ABC, abstractmethod
from typing import Dict, Any, Optional, List
from google.adk.agents import BaseAgent as ADKBaseAgent, LlmAgent
from google.adk.agents.invocation_context import InvocationContext
from google.adk.events import Event
from typing import AsyncGenerator
import logging

logger = logging.getLogger(__name__)

class AgenticBaseAgent(ADKBaseAgent):
    """Base class for all agents in the framework"""
    
    def __init__(
        self,
        name: str,
        description: str = "",
        model: str = "gemini-2.0-flash",
        **kwargs
    ):
        super().__init__(name=name, description=description, **kwargs)
        self.model = model
        self.logger = logging.getLogger(f"agent.{name}")
    
    async def _run_async_impl(self, ctx: InvocationContext) -> AsyncGenerator[Event, None]:
        """Default implementation - subclasses should override"""
        self.logger.info(f"Agent {self.name} executing")
        yield Event(author=self.name, content=f"Agent {self.name} completed")

class SpecializedAgent(LlmAgent):
    """Specialized agent for specific domains using Gemini-2.0-flash"""
    
    def __init__(
        self,
        name: str,
        description: str,
        domain: str,
        instruction: str,
        **kwargs
    ):
        super().__init__(
            name=name,
            description=description,
            model="gemini-2.0-flash",
            instruction=instruction,
            **kwargs
        )
        object.__setattr__(self, '_domain', domain)
        object.__setattr__(self, '_logger', logging.getLogger(f"specialized_agent.{name}"))
    
    @property
    def domain(self) -> str:
        """Get the domain this agent specializes in"""
        return getattr(self, '_domain', 'general')
    
    @property
    def logger(self):
        """Get the logger for this agent"""
        return getattr(self, '_logger', logging.getLogger(f"specialized_agent.{self.name}"))
    
    def can_handle_intent(self, intent: str) -> bool:
        """Check if this agent can handle the given intent"""
        return self.domain.lower() in intent.lower()
