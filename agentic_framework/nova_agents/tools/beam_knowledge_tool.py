"""
BEAM Knowledge Retrieval Tool for Nova Agent
Provides access to real BEAM rule data from Discovery Engine datastore
"""

import asyncio
import logging
from typing import Dict, Any, List, Optional
from google.adk.tools.tool_context import ToolContext
from data.datastore_client import NovaDataStoreClient

logger = logging.getLogger(__name__)

async def beam_knowledge_search(query: str, tool_context: ToolContext) -> str:
    """
    Search for BEAM Features and Correlation Rules in the knowledge base.
    
    Args:
        query: Search query for BEAM rules, features, or detection logic
        tool_context: ADK tool context
    
    Returns:
        Detailed information about matching BEAM rules
    """
    try:
        logger.info(f"Searching BEAM knowledge base for: {query}")
        
        # Initialize datastore client with correct ID
        datastore_client = NovaDataStoreClient(datastore_id="content_1755237537757")
        
        # Search for BEAM features
        results = await datastore_client.search_beam_features(query, limit=5)
        
        if not results or results["total_found"] == 0:
            return f"No BEAM rules found matching '{query}'. Please check the rule name or try a broader search term."
        
        # Format the results for the agent
        response_parts = []
        response_parts.append(f"Found {results['total_found']} BEAM rule(s) matching '{query}':")
        response_parts.append(f"Data source: {results.get('source', 'unknown')}")
        response_parts.append("")
        
        for i, result in enumerate(results["results"], 1):
            response_parts.append(f"**Rule {i}:**")
            
            # Extract basic info
            rule_id = result.get("id", "Unknown")
            rule_name = result.get("name", "Unknown")
            
            response_parts.append(f"- **ID:** {rule_id}")
            response_parts.append(f"- **Name:** {rule_name}")
            
            # Extract content details
            content = result.get("content", {})
            
            if isinstance(content, dict):
                # Handle structured content
                rule_type = content.get("rule_type", content.get("type", "Unknown"))
                description = content.get("description", "No description available")
                
                response_parts.append(f"- **Type:** {rule_type}")
                response_parts.append(f"- **Description:** {description}")
                
                # Add technical details if available
                if "applicable_events" in content:
                    response_parts.append(f"- **Applicable Events:** {content['applicable_events']}")
                
                if "mitre_techniques" in content:
                    response_parts.append(f"- **MITRE Techniques:** {content['mitre_techniques']}")
                
                if "cim_fields" in content:
                    response_parts.append(f"- **CIM Fields:** {content['cim_fields']}")
                    
                if "detection_logic" in content:
                    response_parts.append(f"- **Detection Logic:** {content['detection_logic']}")
                    
                if "training_condition" in content:
                    response_parts.append(f"- **Training Condition:** {content['training_condition']}")
                    
                if "actOnCondition" in content:
                    response_parts.append(f"- **Condition:** {content['actOnCondition']}")
                
                # Add snippets if available (from Discovery Engine)
                if "snippets" in result and result["snippets"]:
                    response_parts.append(f"- **Context:** {result['snippets'][0][:200]}...")
                
            elif isinstance(content, str):
                # Handle text content
                response_parts.append(f"- **Content:** {content[:300]}...")
            
            response_parts.append("")
        
        return "\n".join(response_parts)
        
    except Exception as e:
        logger.error(f"Error searching BEAM knowledge: {str(e)}")
        return f"Error accessing BEAM knowledge base: {str(e)}. Please try again or contact support."

async def beam_rule_by_id(rule_id: str, tool_context: ToolContext) -> str:
    """
    Get specific BEAM rule details by ID.
    
    Args:
        rule_id: The specific rule ID to look up
        tool_context: ADK tool context
    
    Returns:
        Detailed information about the specific BEAM rule
    """
    try:
        logger.info(f"Looking up BEAM rule by ID: {rule_id}")
        
        # Initialize datastore client
        datastore_client = NovaDataStoreClient(datastore_id="content_1755237537757")
        
        # Get rule by ID
        result = await datastore_client.get_rule_by_id(rule_id)
        
        if not result:
            return f"BEAM rule '{rule_id}' not found. Please check the rule ID or try searching by name."
        
        # Format the result
        response_parts = []
        response_parts.append(f"**BEAM Rule Details: {rule_id}**")
        response_parts.append("")
        
        # Extract basic info
        rule_name = result.get("name", "Unknown")
        response_parts.append(f"**Name:** {rule_name}")
        
        # Extract content details
        content = result.get("content", {})
        
        if isinstance(content, dict):
            # Handle structured content
            for key, value in content.items():
                if key not in ["name", "id"] and value:
                    formatted_key = key.replace("_", " ").title()
                    if isinstance(value, list):
                        response_parts.append(f"**{formatted_key}:** {', '.join(map(str, value))}")
                    else:
                        response_parts.append(f"**{formatted_key}:** {value}")
        
        elif isinstance(content, str):
            response_parts.append(f"**Content:** {content}")
        
        # Add snippets if available
        if "snippets" in result and result["snippets"]:
            response_parts.append("")
            response_parts.append("**Additional Context:**")
            for snippet in result["snippets"][:2]:  # Show first 2 snippets
                response_parts.append(f"- {snippet}")
        
        return "\n".join(response_parts)
        
    except Exception as e:
        logger.error(f"Error looking up BEAM rule {rule_id}: {str(e)}")
        return f"Error accessing BEAM rule '{rule_id}': {str(e)}. Please try again or contact support."