#!/usr/bin/env python3
"""
Test authentication setup for Nova Framework
"""

import os
import subprocess
from google.oauth2 import service_account
from google.auth import default
import google.cloud.aiplatform as aiplatform

def test_gcloud_auth():
    """Test gcloud authentication"""
    print("🔍 Testing gcloud authentication...")
    try:
        # Get current user
        result = subprocess.run(['gcloud', 'auth', 'list', '--format=value(account)'], 
                              capture_output=True, text=True)
        if result.returncode == 0:
            accounts = result.stdout.strip().split('\n')
            print(f"✅ Authenticated accounts: {accounts}")
            
            # Get project
            result = subprocess.run(['gcloud', 'config', 'get-value', 'project'], 
                                  capture_output=True, text=True)
            if result.returncode == 0 and result.stdout.strip():
                project = result.stdout.strip()
                print(f"✅ Current project: {project}")
                return project
        
        print("❌ No gcloud authentication found")
        return None
        
    except Exception as e:
        print(f"❌ gcloud auth error: {e}")
        return None

def test_default_credentials():
    """Test Google default credentials"""
    print("\n🔍 Testing default credentials...")
    try:
        credentials, project = default()
        print(f"✅ Default credentials found for project: {project}")
        return credentials, project
    except Exception as e:
        print(f"❌ Default credentials error: {e}")
        return None, None

def test_vertex_ai_init(project_id):
    """Test Vertex AI initialization"""
    print(f"\n🔍 Testing Vertex AI initialization with project: {project_id}")
    try:
        aiplatform.init(project=project_id, location="us-central1")
        print("✅ Vertex AI initialized successfully")
        return True
    except Exception as e:
        print(f"❌ Vertex AI init error: {e}")
        return False

def main():
    print("🚀 Nova Framework Authentication Test")
    print("=" * 50)
    
    # Test 1: gcloud auth
    project = test_gcloud_auth()
    
    # Test 2: Default credentials  
    credentials, default_project = test_default_credentials()
    
    # Use project from gcloud or default
    target_project = project or default_project
    
    if target_project:
        # Test 3: Vertex AI
        vertex_success = test_vertex_ai_init(target_project)
        
        if vertex_success:
            print("\n🎉 Authentication is working!")
            print(f"Project: {target_project}")
            print("Nova Framework should work with these credentials.")
        else:
            print("\n⚠️ Authentication partially working")
            print("You may need to run: gcloud auth application-default login")
    else:
        print("\n❌ No valid authentication found")
        print("Please run: gcloud auth login")

if __name__ == "__main__":
    main()