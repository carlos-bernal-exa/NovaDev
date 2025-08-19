#!/usr/bin/env python3
"""
Test Nova Knowledge Agent directly
"""

import asyncio
import logging
from google.adk.agents.invocation_context import InvocationContext
from google.adk.agents.run_config import RunConfig
from google.adk.sessions import Session
from google.adk.sessions.base_session_service import BaseSessionService
from google.adk.plugins.plugin_manager import PluginManager
from google.genai import types

from agents.knowledge_agent import NovaKnowledgeAgent

class SimpleSessionService(BaseSessionService):
    async def create_session(self, session: Session) -> Session:
        return session
    
    async def delete_session(self, session_id: str) -> None:
        pass
    
    async def get_session(self, session_id: str) -> Session:
        return Session(id=session_id, appName="Test", userId="test")
    
    async def list_sessions(self, user_id: str = None):
        return []

async def test_knowledge_agent_direct():
    print("🧠 Testing Nova Knowledge Agent Directly")
    print("=" * 50)
    
    # Setup logging
    logging.basicConfig(level=logging.INFO)
    
    # Create knowledge agent
    knowledge_agent = NovaKnowledgeAgent()
    
    # Set to detection explanation mode
    print("Setting agent to DETECTION_EXPLANATION_MODE...")
    knowledge_agent.set_mode("DETECTION_EXPLANATION_MODE")
    print(f"Current mode: {knowledge_agent.current_mode}")
    
    # Create session and context
    session = Session(
        id="direct_test",
        appName="NovaTest", 
        userId="test_user"
    )
    
    session_service = SimpleSessionService()
    
    run_config = RunConfig(
        response_modalities=["TEXT"],
        max_llm_calls=5
    )
    
    # Test query
    query = "What rules do you have for lateral movement detection?"
    print(f"\nQuery: {query}")
    print("-" * 40)
    
    try:
        context = InvocationContext(
            agent=knowledge_agent,
            session=session,
            session_service=session_service,
            invocation_id="direct_test_1",
            user_content=types.Content(parts=[types.Part(text=query)]),
            plugin_manager=PluginManager(),
            run_config=run_config
        )
        
        print("Processing with Knowledge Agent...")
        response_events = []
        async for event in knowledge_agent.run_async(context):
            response_events.append(event)
            print(f"Event from {event.author}: {event.content}")
        
        if response_events:
            final_event = response_events[-1]
            print(f"\nFinal Response: {final_event.content}")
        else:
            print("No response generated")
            
    except Exception as e:
        print(f"Error: {str(e)}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(test_knowledge_agent_direct())