#!/usr/bin/env python3
"""
Test authenticated endpoints to identify remaining errors
"""

import requests
import json
import time

BASE_URL = "http://localhost:8000"

def test_authenticated_endpoints():
    """Test endpoints with proper authentication"""
    print("🔐 Testing Authenticated Endpoints")
    print("=" * 50)
    
    # 1. First register/login to get a token
    print("\n1. 📝 Registering test user...")
    test_username = f"testuser_{int(time.time())}"
    test_password = "testpass123"
    
    # Register user
    register_data = {
        "username": test_username,
        "password": test_password,
        "full_name": "Test User"
    }
    
    response = requests.post(f"{BASE_URL}/register", json=register_data)
    print(f"Registration Status: {response.status_code}")
    
    # Login to get token
    login_data = {
        "username": test_username,
        "password": test_password
    }
    
    response = requests.post(f"{BASE_URL}/login", data=login_data)
    print(f"Login Status: {response.status_code}")
    
    if response.status_code != 200:
        print(f"❌ Login failed: {response.text}")
        return
    
    token_data = response.json()
    token = token_data.get("access_token")
    print(f"✅ Got token: {token[:20]}...")
    
    headers = {"Authorization": f"Bearer {token}"}
    
    # 2. Test notification settings endpoint
    print("\n2. 🔔 Testing Notification Settings...")
    try:
        response = requests.get(f"{BASE_URL}/notifications/settings", headers=headers)
        print(f"Status Code: {response.status_code}")
        if response.status_code == 200:
            print("✅ Notification settings endpoint working")
            print(f"Response: {response.json()}")
        else:
            print(f"❌ Notification settings failed: {response.text}")
    except Exception as e:
        print(f"❌ Exception in notification settings: {e}")
    
    # 3. Test security score endpoint
    print("\n3. 🔒 Testing Security Score...")
    try:
        response = requests.get(f"{BASE_URL}/coins/security-score", headers=headers)
        print(f"Status Code: {response.status_code}")
        if response.status_code == 200:
            print("✅ Security score endpoint working")
            print(f"Response: {response.json()}")
        else:
            print(f"❌ Security score failed: {response.text}")
    except Exception as e:
        print(f"❌ Exception in security score: {e}")
    
    # 4. Test system status endpoint (might need admin rights)
    print("\n4. 📊 Testing System Status...")
    try:
        response = requests.get(f"{BASE_URL}/system/status", headers=headers)
        print(f"Status Code: {response.status_code}")
        if response.status_code == 200:
            print("✅ System status endpoint working")
            print(f"Response: {response.json()}")
        elif response.status_code == 403:
            print("⚠️ System status requires admin privileges (expected)")
        else:
            print(f"❌ System status failed: {response.text}")
    except Exception as e:
        print(f"❌ Exception in system status: {e}")
    
    # 5. Test user profile endpoint
    print("\n5. 👤 Testing User Profile...")
    try:
        response = requests.get(f"{BASE_URL}/profile", headers=headers)
        print(f"Status Code: {response.status_code}")
        if response.status_code == 200:
            print("✅ Profile endpoint working")
            profile = response.json()
            print(f"Profile: {profile.get('username', 'N/A')}, Coins: {profile.get('coin_balance', 0)}")
        else:
            print(f"❌ Profile failed: {response.text}")
    except Exception as e:
        print(f"❌ Exception in profile: {e}")

if __name__ == "__main__":
    test_authenticated_endpoints()
