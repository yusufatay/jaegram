#!/usr/bin/env python3
"""
Test specific endpoints to identify remaining errors
"""

import requests
import json

BASE_URL = "http://localhost:8001"

def test_specific_endpoints():
    """Test the endpoints that were showing errors"""
    print("🧪 Testing Specific Error-Prone Endpoints")
    print("=" * 50)
    
    # 1. Test notification settings endpoint
    print("\n1. 🔔 Testing Notification Settings...")
    try:
        response = requests.get(f"{BASE_URL}/notifications/settings")
        print(f"Status Code: {response.status_code}")
        if response.status_code == 200:
            print("✅ Notification settings endpoint working")
            print(f"Response: {response.json()}")
        else:
            print(f"❌ Notification settings failed: {response.text}")
    except Exception as e:
        print(f"❌ Exception in notification settings: {e}")
    
    # 2. Test security score endpoint
    print("\n2. 🔒 Testing Security Score...")
    try:
        response = requests.get(f"{BASE_URL}/coins/security-score")
        print(f"Status Code: {response.status_code}")
        if response.status_code == 200:
            print("✅ Security score endpoint working")
            print(f"Response: {response.json()}")
        else:
            print(f"❌ Security score failed: {response.text}")
    except Exception as e:
        print(f"❌ Exception in security score: {e}")
    
    # 3. Test system status endpoint
    print("\n3. 📊 Testing System Status...")
    try:
        response = requests.get(f"{BASE_URL}/system/status")
        print(f"Status Code: {response.status_code}")
        if response.status_code == 200:
            print("✅ System status endpoint working")
            print(f"Response: {response.json()}")
        else:
            print(f"❌ System status failed: {response.text}")
    except Exception as e:
        print(f"❌ Exception in system status: {e}")
    
    # 4. Test docs endpoint
    print("\n4. 📚 Testing API Documentation...")
    try:
        response = requests.get(f"{BASE_URL}/docs")
        print(f"Status Code: {response.status_code}")
        if response.status_code == 200:
            print("✅ API documentation working")
        else:
            print(f"❌ API docs failed: {response.status_code}")
    except Exception as e:
        print(f"❌ Exception in API docs: {e}")

if __name__ == "__main__":
    test_specific_endpoints()
