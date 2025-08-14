import asyncio
import aiohttp
import json
import time
from typing import Dict, Any, Optional, List
from datetime import datetime, timedelta
import logging
import os

logger = logging.getLogger(__name__)

class ExabeamTokenManager:
    """
    Manages Exabeam API tokens with automatic refresh based on TTL.
    Reuses the proven logic from the working implementation.
    """
    
    def __init__(
        self,
        client_id: str,
        client_secret: str,
        base_url: str = "https://api.us-west.exabeam.cloud",
        token_endpoint: str = "/auth/v1/token"
    ):
        self.client_id = client_id
        self.client_secret = client_secret
        self.base_url = base_url
        self.token_endpoint = token_endpoint
        self.full_token_url = f"{base_url}{token_endpoint}"
        
        self._access_token: Optional[str] = None
        self._refresh_token: Optional[str] = None
        self._token_expires_at: Optional[datetime] = None
        self._token_ttl: Optional[int] = None
        
        self.logger = logging.getLogger("exabeam_token_manager")
        
        self.refresh_buffer_seconds = 300
    
    async def get_access_token(self) -> str:
        """
        Get a valid access token, refreshing if necessary.
        Returns the current valid access token.
        """
        if self._needs_refresh():
            await self._refresh_token_async()
        
        if not self._access_token:
            raise Exception("Failed to obtain access token")
        
        return self._access_token
    
    def _needs_refresh(self) -> bool:
        """Check if token needs to be refreshed"""
        if not self._access_token or not self._token_expires_at:
            return True
        
        buffer_time = datetime.now() + timedelta(seconds=self.refresh_buffer_seconds)
        return self._token_expires_at <= buffer_time
    
    async def _refresh_token_async(self) -> None:
        """Refresh the access token using client credentials flow"""
        self.logger.info("Refreshing Exabeam access token")
        
        payload = {
            "grant_type": "client_credentials",
            "client_id": self.client_id,
            "client_secret": self.client_secret
        }
        
        headers = {
            "accept": "application/json",
            "content-type": "application/json"
        }
        
        try:
            async with aiohttp.ClientSession() as session:
                async with session.post(
                    self.full_token_url,
                    json=payload,
                    headers=headers
                ) as response:
                    if response.status == 200:
                        token_data = await response.json()
                        await self._process_token_response(token_data)
                        self.logger.info("Successfully refreshed Exabeam access token")
                    else:
                        error_text = await response.text()
                        self.logger.error(f"Token refresh failed: {response.status} - {error_text}")
                        raise Exception(f"Token refresh failed: {response.status}")
        
        except Exception as e:
            self.logger.error(f"Error refreshing token: {str(e)}")
            raise
    
    async def _process_token_response(self, token_data: Dict[str, Any]) -> None:
        """Process the token response and update internal state"""
        self._access_token = token_data.get("access_token")
        self._refresh_token = token_data.get("refresh_token")
        
        expires_in = token_data.get("expires_in", 3600)  # Default 1 hour
        self._token_ttl = expires_in
        self._token_expires_at = datetime.now() + timedelta(seconds=expires_in)
        
        self.logger.info(f"Token will expire at: {self._token_expires_at}")
        self.logger.info(f"Token TTL: {self._token_ttl} seconds")
    
    def get_token_info(self) -> Dict[str, Any]:
        """Get current token information"""
        return {
            "has_token": bool(self._access_token),
            "expires_at": self._token_expires_at.isoformat() if self._token_expires_at else None,
            "ttl_seconds": self._token_ttl,
            "needs_refresh": self._needs_refresh(),
            "client_id": self.client_id[:8] + "..." if self.client_id else None  # Partial for security
        }
    
    async def force_refresh(self) -> None:
        """Force a token refresh regardless of current state"""
        await self._refresh_token_async()
