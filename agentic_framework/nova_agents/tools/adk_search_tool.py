"""
ADK Vertex AI Search tool for accessing BEAM rules
Uses built-in ADK search capabilities instead of custom Discovery Engine client
"""

import logging
from google.adk.tools.tool_context import ToolContext
from google.adk.tools.vertex_ai_search import vertex_ai_search

logger = logging.getLogger(__name__)

async def search_beam_rules(query: str, tool_context: ToolContext) -> str:
    """
    Search for BEAM rules using ADK's built-in Vertex AI Search.
    
    Args:
        query: Search query for BEAM rules
        tool_context: ADK tool context
    
    Returns:
        Search results from the BEAM datastore
    """
    try:
        logger.info(f"Searching BEAM rules using ADK Vertex AI Search: {query}")
        
        # Use ADK's built-in Vertex AI Search tool
        # This should automatically handle authentication and connection
        search_results = await vertex_ai_search(
            query=query,
            datastore_id="content_1755237537757",
            project_id="threatexplainer",
            location="global",
            tool_context=tool_context
        )
        
        # Format the results for better readability
        if search_results:
            formatted_result = f"🔍 **BEAM Search Results for '{query}':**\n\n"
            formatted_result += search_results
            formatted_result += "\n\n💡 **Note**: These are actual results from your BEAM datastore (content_1755237537757)"
            return formatted_result
        else:
            return f"No BEAM rules found matching '{query}'. The query might be too specific or the datastore might be empty."
            
    except Exception as e:
        logger.error(f"Error with ADK Vertex AI Search: {str(e)}")
        return f"Error accessing BEAM datastore with ADK search: {str(e)}. This might be an authentication or configuration issue."

async def get_beam_rule_details(rule_name: str, tool_context: ToolContext) -> str:
    """
    Get detailed information about a specific BEAM rule.
    
    Args:
        rule_name: Name or ID of the BEAM rule
        tool_context: ADK tool context
    
    Returns:
        Detailed rule information
    """
    try:
        logger.info(f"Getting BEAM rule details using ADK search: {rule_name}")
        
        # Search for the specific rule
        search_results = await vertex_ai_search(
            query=f'"{rule_name}" OR {rule_name.replace("-", "_").lower()}',
            datastore_id="content_1755237537757", 
            project_id="threatexplainer",
            location="global",
            tool_context=tool_context
        )
        
        if search_results:
            formatted_result = f"📋 **BEAM Rule Details for '{rule_name}':**\n\n"
            formatted_result += search_results
            formatted_result += f"\n\n🎯 **Specific Rule**: {rule_name}"
            formatted_result += "\n💡 **Source**: Your BEAM datastore via ADK Vertex AI Search"
            return formatted_result
        else:
            return f"BEAM rule '{rule_name}' not found. Please check the rule name or try a broader search."
            
    except Exception as e:
        logger.error(f"Error getting rule details with ADK search: {str(e)}")
        return f"Error retrieving rule '{rule_name}' details: {str(e)}. This might be an authentication or configuration issue."