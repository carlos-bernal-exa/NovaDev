#!/usr/bin/env python3

import sys
import os

print("Testing imports for agentic framework...")

try:
    import google.adk.agents
    print("✅ google.adk.agents imported successfully")
except ImportError as e:
    print(f"❌ Failed to import google.adk.agents: {e}")

try:
    from google.adk.agents import LlmAgent, BaseAgent
    print("✅ LlmAgent and BaseAgent imported successfully")
except ImportError as e:
    print(f"❌ Failed to import LlmAgent/BaseAgent: {e}")

try:
    import google.cloud.aiplatform
    print("✅ google.cloud.aiplatform imported successfully")
except ImportError as e:
    print(f"❌ Failed to import google.cloud.aiplatform: {e}")

try:
    import mcp
    print("✅ mcp imported successfully")
except ImportError as e:
    print(f"❌ Failed to import mcp: {e}")

try:
    import aiohttp
    print("✅ aiohttp imported successfully")
except ImportError as e:
    print(f"❌ Failed to import aiohttp: {e}")

try:
    from dotenv import load_dotenv
    print("✅ python-dotenv imported successfully")
except ImportError as e:
    print(f"❌ Failed to import python-dotenv: {e}")

print("\nAll import tests completed!")
