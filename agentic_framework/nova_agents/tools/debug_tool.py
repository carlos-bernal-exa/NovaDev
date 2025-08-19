"""
Simple debug tool to test if tools are being called at all
"""

import logging
from google.adk.tools.tool_context import ToolContext

logger = logging.getLogger(__name__)

def debug_tool_test(tool_context: ToolContext = None) -> str:
    """
    Simple debug tool to confirm tools are being called.
    
    Returns:
        Debug message confirming tool execution
    """
    try:
        logger.info("DEBUG: Tool was called successfully!")
        
        return """🔧 DEBUG: Tool execution confirmed!

This proves that:
✅ Tools are properly registered with the agent
✅ The agent can call tools when instructed
✅ The tool execution environment is working

If you see this message, the tools are working correctly.
The issue might be with the specific BEAM datastore tools or authentication.

Available tools should include:
- debug_tool_test() ← This one (working!)
- list_all_beam_rules() ← List BEAM rules
- beam_knowledge_search(query) ← Search rules
- beam_rule_by_id(rule_id) ← Get rule details"""
        
    except Exception as e:
        logger.error(f"DEBUG: Tool execution failed: {str(e)}")
        return f"🔧 DEBUG: Tool execution failed: {str(e)}"