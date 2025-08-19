"""
Simple tool to list available BEAM rules for debugging
"""

import asyncio
import logging
from typing import Dict, Any, List, Optional
from google.adk.tools.tool_context import ToolContext
from data.datastore_client import NovaDataStoreClient

logger = logging.getLogger(__name__)

async def list_all_beam_rules(tool_context: ToolContext) -> str:
    """
    List all available BEAM rules in the knowledge base.
    
    Args:
        tool_context: ADK tool context
    
    Returns:
        List of all available BEAM rules
    """
    try:
        logger.info("Listing all available BEAM rules")
        
        # Initialize datastore client with correct ID
        datastore_client = NovaDataStoreClient(datastore_id="content_1755237537757")
        
        # Search for all BEAM-related content with broad query
        results = await datastore_client.search_beam_features("BEAM", limit=20)
        
        if not results or results["total_found"] == 0:
            # Try alternative searches
            alt_results = await datastore_client.search_beam_features("rule", limit=20)
            if alt_results and alt_results["total_found"] > 0:
                results = alt_results
            else:
                return "No BEAM rules found in the datastore. The datastore might be empty or inaccessible."
        
        # Format the results for the agent
        response_parts = []
        response_parts.append(f"📋 **Available BEAM Rules ({results['total_found']} found):**")
        response_parts.append(f"Data source: {results.get('source', 'unknown')}")
        response_parts.append("")
        
        for i, result in enumerate(results["results"], 1):
            rule_id = result.get("id", "Unknown")
            rule_name = result.get("name", "Unknown")
            
            # Clean up the display name
            clean_name = rule_id.replace("_", "-").upper() if rule_id != "Unknown" else rule_name
            
            response_parts.append(f"{i}. **{clean_name}**")
            response_parts.append(f"   - Rule ID: `{rule_id}`")
            
            # Add any content info if available
            content = result.get("content", {})
            if isinstance(content, dict):
                if "title" in content:
                    response_parts.append(f"   - Title: {content['title']}")
                if "description" in content and content["description"] != "No description available":
                    response_parts.append(f"   - Description: {content['description'][:100]}...")
            
            response_parts.append("")
        
        response_parts.append("💡 **To get details about a specific rule, ask:**")
        response_parts.append("   'Explain rule [RULE_NAME]' or 'Get details for rule [RULE_ID]'")
        
        return "\n".join(response_parts)
        
    except Exception as e:
        logger.error(f"Error listing BEAM rules: {str(e)}")
        return f"Error accessing BEAM rule list: {str(e)}. Please try again or contact support."