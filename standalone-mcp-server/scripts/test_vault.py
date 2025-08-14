#!/usr/bin/env python3
"""
Test script for HashiCorp Vault integration

This script tests Vault connectivity, authentication, and secret retrieval.
"""

import asyncio
import sys
import os
import json
from datetime import datetime

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from vault_client import VaultClient

async def test_vault_connection():
    """Test Vault connection and authentication"""
    print("🔐 Testing HashiCorp Vault Integration")
    print("=" * 50)
    
    vault_enabled = os.getenv("VAULT_ENABLED", "false").lower() == "true"
    vault_url = os.getenv("VAULT_URL")
    vault_token = os.getenv("VAULT_TOKEN")
    secret_path = os.getenv("VAULT_SECRET_PATH", "secret/exabeam-mcp")
    
    print(f"Vault Enabled: {vault_enabled}")
    print(f"Vault URL: {vault_url}")
    print(f"Secret Path: {secret_path}")
    print(f"Token Provided: {'Yes' if vault_token else 'No'}")
    
    if not vault_enabled:
        print("❌ Vault integration is disabled (VAULT_ENABLED=false)")
        return False
    
    if not vault_url:
        print("❌ VAULT_URL not set")
        return False
    
    vault_client = VaultClient()
    
    print("\n🏥 Testing Vault Health Check...")
    try:
        healthy = await vault_client.health_check()
        if healthy:
            print("✅ Vault is healthy and accessible")
        else:
            print("❌ Vault health check failed")
            return False
    except Exception as e:
        print(f"❌ Vault health check error: {str(e)}")
        return False
    
    print("\n🔑 Testing Vault Authentication...")
    try:
        token = await vault_client.authenticate()
        print(f"✅ Successfully authenticated with Vault")
        print(f"   Token: {token[:20]}..." if len(token) > 20 else f"   Token: {token}")
    except Exception as e:
        print(f"❌ Vault authentication failed: {str(e)}")
        return False
    
    print("\n📋 Testing Secret Retrieval...")
    try:
        secrets = await vault_client.get_secrets()
        if secrets:
            print(f"✅ Successfully retrieved {len(secrets)} secrets")
            print("   Available secrets:")
            for key in secrets.keys():
                value = secrets[key]
                masked_value = value[:8] + "..." if len(value) > 8 else "***"
                print(f"     - {key}: {masked_value}")
        else:
            print("⚠️  No secrets found at the specified path")
            return False
    except Exception as e:
        print(f"❌ Secret retrieval failed: {str(e)}")
        return False
    
    print("\n🎉 All Vault tests passed!")
    return True

async def setup_vault_secrets():
    """Helper function to set up example secrets in Vault"""
    print("\n🛠️  Vault Setup Helper")
    print("=" * 30)
    print("To set up secrets in Vault, run these commands:")
    print()
    print("# For KV v2 engine (default 'secret' mount):")
    print("vault kv put secret/exabeam-mcp \\")
    print("  jwt_secret=\"your-super-secure-jwt-secret-key-here\" \\")
    print("  exabeam_client_id=\"your-exabeam-client-id\" \\")
    print("  exabeam_client_secret=\"your-exabeam-client-secret\" \\")
    print("  exabeam_base_url=\"https://api.us-west.exabeam.cloud\"")
    print()
    print("# For KV v1 engine:")
    print("vault write secret/exabeam-mcp \\")
    print("  jwt_secret=\"your-super-secure-jwt-secret-key-here\" \\")
    print("  exabeam_client_id=\"your-exabeam-client-id\" \\")
    print("  exabeam_client_secret=\"your-exabeam-client-secret\"")
    print()
    print("# Set up AppRole authentication:")
    print("vault auth enable approle")
    print("vault write auth/approle/role/exabeam-mcp \\")
    print("  token_policies=\"exabeam-mcp-policy\" \\")
    print("  token_ttl=1h \\")
    print("  token_max_ttl=4h")
    print()
    print("# Create policy:")
    print("vault policy write exabeam-mcp-policy - <<EOF")
    print("path \"secret/data/exabeam-mcp\" {")
    print("  capabilities = [\"read\"]")
    print("}")
    print("EOF")

def main():
    """Main test function"""
    if len(sys.argv) > 1 and sys.argv[1] == "setup":
        asyncio.run(setup_vault_secrets())
        return
    
    print(f"🚀 Vault Integration Test - {datetime.utcnow().isoformat()}")
    
    try:
        success = asyncio.run(test_vault_connection())
        if success:
            print("\n✅ Vault integration is working correctly!")
            sys.exit(0)
        else:
            print("\n❌ Vault integration test failed!")
            sys.exit(1)
    except KeyboardInterrupt:
        print("\n⚠️  Test interrupted by user")
        sys.exit(1)
    except Exception as e:
        print(f"\n❌ Unexpected error: {str(e)}")
        sys.exit(1)

if __name__ == "__main__":
    main()
