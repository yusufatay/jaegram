#!/usr/bin/env python3
"""
Test script to specifically debug system status endpoint
"""
import requests
import json
import time

BASE_URL = "http://localhost:8000"

def test_system_status():
    print("🔍 Debugging System Status Endpoint")
    print("="*50)
    
    # Register and login a test user
    username = f"testuser_{int(time.time())}"
    password = "testpass123"
    
    # Register
    register_data = {
        "username": username,
        "password": password,
        "email": f"{username}@test.com"
    }
    
    response = requests.post(f"{BASE_URL}/register", json=register_data)
    print(f"Registration Status: {response.status_code}")
    
    # Login
    login_data = {
        "username": username,
        "password": password
    }
    
    response = requests.post(f"{BASE_URL}/login", data=login_data)
    print(f"Login Status: {response.status_code}")
    
    if response.status_code == 200:
        token_data = response.json()
        token = token_data["access_token"]
        print(f"✅ Got token")
        
        headers = {"Authorization": f"Bearer {token}"}
        
        # Test system status as non-admin user
        print("\n🔒 Testing System Status as non-admin user...")
        response = requests.get(f"{BASE_URL}/system/status", headers=headers)
        print(f"Status Code: {response.status_code}")
        print(f"Response: {response.text}")
        
        if response.status_code == 403:
            print("✅ Correctly returned 403 for non-admin user")
        elif response.status_code == 500:
            print("❌ Still returning 500 error instead of 403")
            # Let's check the server logs or response details
            try:
                error_detail = response.json()
                print(f"Error detail: {error_detail}")
            except:
                print(f"Raw response: {response.text}")
        else:
            print(f"❌ Unexpected status code: {response.status_code}")
            
        # Let's also check if the user has admin privileges
        print("\n👤 Checking user profile to see admin status...")
        profile_response = requests.get(f"{BASE_URL}/profile", headers=headers)
        if profile_response.status_code == 200:
            profile_data = profile_response.json()
            print(f"User profile: {json.dumps(profile_data, indent=2)}")
        
    else:
        print("❌ Failed to login")

if __name__ == "__main__":
    test_system_status()
