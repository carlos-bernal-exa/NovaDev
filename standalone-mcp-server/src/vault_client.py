"""
HashiCorp Vault integration for secure secret management.

This module provides functionality to retrieve secrets from HashiCorp Vault
for the Exabeam MCP server, supporting multiple authentication methods.
"""

import os
import logging
import asyncio
from typing import Dict, Any, Optional
import aiohttp
import json

logger = logging.getLogger(__name__)

class VaultClient:
    """HashiCorp Vault client for secret management"""
    
    def __init__(self):
        self.vault_url = os.getenv("VAULT_URL")
        self.vault_token = os.getenv("VAULT_TOKEN")
        self.secret_path = os.getenv("VAULT_SECRET_PATH", "secret/exabeam-mcp")
        self.mount_point = os.getenv("VAULT_MOUNT_POINT", "secret")
        self.role_id = os.getenv("VAULT_ROLE_ID")
        self.secret_id = os.getenv("VAULT_SECRET_ID")
        self.k8s_role = os.getenv("VAULT_K8S_ROLE")
        self.enabled = os.getenv("VAULT_ENABLED", "false").lower() == "true"
        
        if self.enabled and not self.vault_url:
            raise ValueError("VAULT_URL must be set when VAULT_ENABLED=true")
    
    async def authenticate(self) -> str:
        """Authenticate with Vault and return access token"""
        if self.vault_token:
            logger.info("Using provided Vault token")
            return self.vault_token
        
        if self.role_id and self.secret_id:
            logger.info("Authenticating with AppRole")
            return await self._authenticate_approle()
        
        if self.k8s_role:
            logger.info("Authenticating with Kubernetes")
            return await self._authenticate_kubernetes()
        
        raise ValueError("No valid Vault authentication method configured")
    
    async def _authenticate_approle(self) -> str:
        """Authenticate using AppRole method"""
        auth_url = f"{self.vault_url}/v1/auth/approle/login"
        auth_data = {
            "role_id": self.role_id,
            "secret_id": self.secret_id
        }
        
        async with aiohttp.ClientSession() as session:
            async with session.post(auth_url, json=auth_data) as response:
                if response.status == 200:
                    result = await response.json()
                    token = result["auth"]["client_token"]
                    logger.info("Successfully authenticated with AppRole")
                    return token
                else:
                    error_text = await response.text()
                    raise Exception(f"AppRole authentication failed: {response.status} - {error_text}")
    
    async def _authenticate_kubernetes(self) -> str:
        """Authenticate using Kubernetes service account"""
        try:
            with open("/var/run/secrets/kubernetes.io/serviceaccount/token", "r") as f:
                jwt_token = f.read().strip()
        except FileNotFoundError:
            raise Exception("Kubernetes service account token not found")
        
        auth_url = f"{self.vault_url}/v1/auth/kubernetes/login"
        auth_data = {
            "role": self.k8s_role,
            "jwt": jwt_token
        }
        
        async with aiohttp.ClientSession() as session:
            async with session.post(auth_url, json=auth_data) as response:
                if response.status == 200:
                    result = await response.json()
                    token = result["auth"]["client_token"]
                    logger.info("Successfully authenticated with Kubernetes")
                    return token
                else:
                    error_text = await response.text()
                    raise Exception(f"Kubernetes authentication failed: {response.status} - {error_text}")
    
    async def get_secrets(self) -> Dict[str, str]:
        """Retrieve secrets from Vault"""
        if not self.enabled:
            logger.info("Vault integration disabled, using environment variables")
            return {}
        
        try:
            token = await self.authenticate()
            
            if self.mount_point == "secret":
                secret_url = f"{self.vault_url}/v1/{self.mount_point}/data/{self.secret_path.replace(f'{self.mount_point}/', '')}"
            else:
                secret_url = f"{self.vault_url}/v1/{self.secret_path}"
            
            headers = {"X-Vault-Token": token}
            
            async with aiohttp.ClientSession() as session:
                async with session.get(secret_url, headers=headers) as response:
                    if response.status == 200:
                        result = await response.json()
                        
                        if "data" in result and "data" in result["data"]:
                            secrets = result["data"]["data"]
                        else:
                            secrets = result["data"]
                        
                        logger.info(f"Successfully retrieved {len(secrets)} secrets from Vault")
                        return secrets
                    else:
                        error_text = await response.text()
                        raise Exception(f"Failed to retrieve secrets: {response.status} - {error_text}")
        
        except Exception as e:
            logger.error(f"Vault secret retrieval failed: {str(e)}")
            logger.info("Falling back to environment variables")
            return {}
    
    async def health_check(self) -> bool:
        """Check Vault connectivity and authentication"""
        if not self.enabled:
            return True
        
        try:
            token = await self.authenticate()
            health_url = f"{self.vault_url}/v1/sys/health"
            headers = {"X-Vault-Token": token}
            
            async with aiohttp.ClientSession() as session:
                async with session.get(health_url, headers=headers) as response:
                    return response.status in [200, 429]  # 429 = standby node
        
        except Exception as e:
            logger.error(f"Vault health check failed: {str(e)}")
            return False

def load_secrets_from_vault() -> Dict[str, str]:
    """Synchronous wrapper to load secrets from Vault"""
    vault_client = VaultClient()
    
    if not vault_client.enabled:
        return {}
    
    try:
        loop = asyncio.get_event_loop()
        if loop.is_running():
            import concurrent.futures
            with concurrent.futures.ThreadPoolExecutor() as executor:
                future = executor.submit(asyncio.run, vault_client.get_secrets())
                return future.result(timeout=30)
        else:
            return asyncio.run(vault_client.get_secrets())
    except Exception as e:
        logger.error(f"Failed to load secrets from Vault: {str(e)}")
        return {}

def merge_vault_secrets(vault_secrets: Dict[str, str]) -> None:
    """Merge Vault secrets into environment variables"""
    secret_mapping = {
        "jwt_secret": "JWT_SECRET",
        "exabeam_client_id": "EXABEAM_CLIENT_ID", 
        "exabeam_client_secret": "EXABEAM_CLIENT_SECRET",
        "exabeam_base_url": "EXABEAM_BASE_URL"
    }
    
    for vault_key, env_key in secret_mapping.items():
        if vault_key in vault_secrets and not os.getenv(env_key):
            os.environ[env_key] = vault_secrets[vault_key]
            logger.info(f"Loaded {env_key} from Vault")

if __name__ != "__main__":
    try:
        vault_secrets = load_secrets_from_vault()
        merge_vault_secrets(vault_secrets)
    except Exception as e:
        logger.warning(f"Vault initialization failed: {str(e)}")
