import asyncio
import json
import logging
from typing import Dict, Any, List, AsyncGenerator
from datetime import datetime
import aiohttp
from exabeam_client import ExabeamTokenManager

logger = logging.getLogger(__name__)

class MCPServer:
    """MCP Server for handling Exabeam operations"""
    
    def __init__(self, token_manager: ExabeamTokenManager):
        self.token_manager = token_manager
        self.logger = logging.getLogger("mcp_server")
        self.active_connections: List[Any] = []
    
    async def search_cases(
        self,
        limit: int = 3000,
        start_time: str = "2024-05-01T00:00:00Z", 
        end_time: str = "2024-06-01T00:00:00Z",
        fields: List[str] = None,
        filter_query: str = 'product: ("Correlation Rule", "NG Analytics")'
    ) -> Dict[str, Any]:
        """
        Search Exabeam cases using the threat-center API.
        Reuses the exact same logic from the working implementation.
        
        Args:
            limit: Maximum number of cases to return (default: 3000)
            start_time: Start time for search in ISO format (default: 2024-05-01T00:00:00Z)
            end_time: End time for search in ISO format (default: 2024-06-01T00:00:00Z)
            fields: List of fields to return (default: ["*"] for all fields)
            filter_query: Filter query string (default: product filter)
        
        Returns:
            Dictionary containing search results from Exabeam API
        """
        if fields is None:
            fields = ["*"]
        
        try:
            access_token = await self.token_manager.get_access_token()
        except Exception as e:
            self.logger.error(f"Failed to get access token for case search: {str(e)}")
            raise
        
        url = f"{self.token_manager.base_url}/threat-center/v1/search/cases"
        headers = {
            "accept": "application/json",
            "authorization": f"Bearer {access_token}",
            "content-type": "application/json"
        }
        
        payload = {
            "limit": limit,
            "startTime": start_time,
            "endTime": end_time,
            "fields": fields,
            "filter": filter_query
        }
        
        self.logger.info(f"Searching cases with limit={limit}, timerange={start_time} to {end_time}")
        
        try:
            async with aiohttp.ClientSession() as session:
                async with session.post(url, json=payload, headers=headers) as response:
                    if response.status == 200:
                        result = await response.json()
                        case_count = len(result.get("cases", []))
                        self.logger.info(f"Successfully retrieved {case_count} cases")
                        return result
                    else:
                        error_text = await response.text()
                        self.logger.error(f"Case search failed: {response.status} - {error_text}")
                        raise Exception(f"Case search failed: {response.status} - {error_text}")
        
        except Exception as e:
            self.logger.error(f"Error searching cases: {str(e)}")
            raise
    
    async def search_alerts(
        self,
        limit: int = 3000,
        start_time: str = "2024-05-01T00:00:00Z",
        end_time: str = "2024-06-01T00:00:00Z",
        fields: List[str] = None,
        filter_query: str = "caseId:null"
    ) -> Dict[str, Any]:
        """
        Search Exabeam alerts using the threat-center API.
        
        Args:
            limit: Maximum number of alerts to return (default: 3000)
            start_time: Start time for search in ISO format (default: 2024-05-01T00:00:00Z)
            end_time: End time for search in ISO format (default: 2024-06-01T00:00:00Z)
            fields: List of fields to return (default: ["*"] for all fields)
            filter_query: Filter query string (default: "caseId:null")
        
        Returns:
            Dictionary containing search results from Exabeam API
        """
        if fields is None:
            fields = ["*"]
        
        try:
            access_token = await self.token_manager.get_access_token()
        except Exception as e:
            self.logger.error(f"Failed to get access token for alert search: {str(e)}")
            raise
        
        url = f"{self.token_manager.base_url}/threat-center/v1/search/alerts"
        headers = {
            "accept": "application/json",
            "authorization": f"Bearer {access_token}",
            "content-type": "application/json"
        }
        
        payload = {
            "limit": limit,
            "startTime": start_time,
            "endTime": end_time,
            "fields": fields,
            "filter": filter_query
        }
        
        self.logger.info(f"Searching alerts with limit={limit}, timerange={start_time} to {end_time}")
        
        try:
            async with aiohttp.ClientSession() as session:
                async with session.post(url, json=payload, headers=headers) as response:
                    if response.status == 200:
                        result = await response.json()
                        alert_count = len(result.get("alerts", []))
                        self.logger.info(f"Successfully retrieved {alert_count} alerts")
                        return result
                    else:
                        error_text = await response.text()
                        self.logger.error(f"Alert search failed: {response.status} - {error_text}")
                        raise Exception(f"Alert search failed: {response.status} - {error_text}")
        
        except Exception as e:
            self.logger.error(f"Error searching alerts: {str(e)}")
            raise
    
    async def search_events(
        self,
        limit: int = 3000,
        start_time: str = "2024-04-01T00:00:00Z",
        end_time: str = "2024-04-08T00:00:00Z",
        fields: List[str] = None,
        filter_query: str = 'product:"Audit Log"',
        distinct: bool = False
    ) -> Dict[str, Any]:
        """
        Search Exabeam events using the search API.
        
        Args:
            limit: Maximum number of events to return (default: 3000)
            start_time: Start time for search in ISO format (default: 2024-04-01T00:00:00Z)
            end_time: End time for search in ISO format (default: 2024-04-08T00:00:00Z)
            fields: List of fields to return (default: ["*"] for all fields)
            filter_query: Filter query string (default: 'product:"Audit Log"')
            distinct: Whether to return distinct results (default: False)
        
        Returns:
            Dictionary containing search results from Exabeam API
        """
        if fields is None:
            fields = ["*"]
        
        try:
            access_token = await self.token_manager.get_access_token()
        except Exception as e:
            self.logger.error(f"Failed to get access token for event search: {str(e)}")
            raise
        
        url = f"{self.token_manager.base_url}/search/v2/events"
        headers = {
            "accept": "application/json",
            "authorization": f"Bearer {access_token}",
            "content-type": "application/json"
        }
        
        payload = {
            "limit": limit,
            "distinct": distinct,
            "fields": fields,
            "startTime": start_time,
            "endTime": end_time,
            "filter": filter_query
        }
        
        self.logger.info(f"Searching events with limit={limit}, timerange={start_time} to {end_time}")
        
        try:
            async with aiohttp.ClientSession() as session:
                async with session.post(url, json=payload, headers=headers) as response:
                    if response.status == 200:
                        result = await response.json()
                        event_count = len(result.get("events", []))
                        self.logger.info(f"Successfully retrieved {event_count} events")
                        return result
                    else:
                        error_text = await response.text()
                        self.logger.error(f"Event search failed: {response.status} - {error_text}")
                        raise Exception(f"Event search failed: {response.status} - {error_text}")
        
        except Exception as e:
            self.logger.error(f"Error searching events: {str(e)}")
            raise
    
    def get_available_tools(self) -> List[Dict[str, Any]]:
        """Get list of available MCP tools"""
        return [
            {
                "name": "search_cases",
                "description": "Search Exabeam security cases",
                "input_schema": {
                    "type": "object",
                    "properties": {
                        "limit": {
                            "type": "integer",
                            "description": "Maximum number of cases to return",
                            "default": 3000
                        },
                        "start_time": {
                            "type": "string",
                            "description": "Start time in ISO format",
                            "default": "2024-05-01T00:00:00Z"
                        },
                        "end_time": {
                            "type": "string", 
                            "description": "End time in ISO format",
                            "default": "2024-06-01T00:00:00Z"
                        },
                        "fields": {
                            "type": "array",
                            "items": {"type": "string"},
                            "description": "List of fields to return",
                            "default": ["*"]
                        },
                        "filter_query": {
                            "type": "string",
                            "description": "Filter query string",
                            "default": 'product: ("Correlation Rule", "NG Analytics")'
                        }
                    }
                }
            },
            {
                "name": "search_alerts",
                "description": "Search Exabeam security alerts",
                "input_schema": {
                    "type": "object",
                    "properties": {
                        "limit": {
                            "type": "integer",
                            "description": "Maximum number of alerts to return",
                            "default": 3000
                        },
                        "start_time": {
                            "type": "string",
                            "description": "Start time in ISO format",
                            "default": "2024-05-01T00:00:00Z"
                        },
                        "end_time": {
                            "type": "string",
                            "description": "End time in ISO format", 
                            "default": "2024-06-01T00:00:00Z"
                        },
                        "fields": {
                            "type": "array",
                            "items": {"type": "string"},
                            "description": "List of fields to return",
                            "default": ["*"]
                        },
                        "filter_query": {
                            "type": "string",
                            "description": "Filter query string",
                            "default": "caseId:null"
                        }
                    }
                }
            },
            {
                "name": "search_events",
                "description": "Search Exabeam security events",
                "input_schema": {
                    "type": "object",
                    "properties": {
                        "limit": {
                            "type": "integer",
                            "description": "Maximum number of events to return",
                            "default": 3000
                        },
                        "start_time": {
                            "type": "string",
                            "description": "Start time in ISO format",
                            "default": "2024-04-01T00:00:00Z"
                        },
                        "end_time": {
                            "type": "string",
                            "description": "End time in ISO format",
                            "default": "2024-04-08T00:00:00Z"
                        },
                        "fields": {
                            "type": "array",
                            "items": {"type": "string"},
                            "description": "List of fields to return",
                            "default": ["*"]
                        },
                        "filter_query": {
                            "type": "string",
                            "description": "Filter query string",
                            "default": 'product:"Audit Log"'
                        },
                        "distinct": {
                            "type": "boolean",
                            "description": "Whether to return distinct results",
                            "default": False
                        }
                    }
                }
            }
        ]
    
    async def call_tool(self, tool_name: str, arguments: Dict[str, Any]) -> Dict[str, Any]:
        """Call a specific MCP tool"""
        if tool_name == "search_cases":
            return await self.search_cases(**arguments)
        elif tool_name == "search_alerts":
            return await self.search_alerts(**arguments)
        elif tool_name == "search_events":
            return await self.search_events(**arguments)
        else:
            raise ValueError(f"Unknown tool: {tool_name}")
