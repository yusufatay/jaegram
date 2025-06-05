#!/usr/bin/env python3
"""
Test script for real Instagram integration
"""
import requests
import json
import time

BASE_URL = "http://localhost:8000"

def test_instagram_integration():
    print("📸 Testing Real Instagram Integration")
    print("="*50)
    
    # Instagram credentials provided by user
    instagram_username = "luvmef"
    instagram_password = "asgsag2"
    
    # Platform credentials
    platform_username = f"testuser_{int(time.time())}"
    platform_password = "testpass123"
    
    # 1. Register and login to platform
    print("1. 📝 Registering platform user...")
    register_data = {
        "username": platform_username,
        "password": platform_password,
        "email": f"{platform_username}@test.com"
    }
    
    response = requests.post(f"{BASE_URL}/register", json=register_data)
    print(f"Registration Status: {response.status_code}")
    
    # Login to get token
    login_data = {
        "username": platform_username,
        "password": platform_password
    }
    
    response = requests.post(f"{BASE_URL}/login", data=login_data)
    print(f"Login Status: {response.status_code}")
    
    if response.status_code != 200:
        print("❌ Failed to login to platform")
        return
    
    token_data = response.json()
    token = token_data["access_token"]
    print(f"✅ Platform login successful")
    
    headers = {"Authorization": f"Bearer {token}"}
    
    # 2. Test Instagram login endpoint
    print("\n2. 📸 Testing Instagram login...")
    instagram_login_data = {
        "username": instagram_username,
        "password": instagram_password
    }
    
    response = requests.post(f"{BASE_URL}/login-instagram", json=instagram_login_data)
    print(f"Instagram Login Status: {response.status_code}")
    print(f"Response: {response.text}")
    
    if response.status_code == 200:
        print("✅ Instagram login successful!")
        instagram_data = response.json()
        print(f"Instagram User ID: {instagram_data.get('user_id')}")
        print(f"Username: {instagram_data.get('username')}")
        print(f"Full Name: {instagram_data.get('full_name')}")
        print(f"Followers: {instagram_data.get('followers_count')}")
        print(f"Following: {instagram_data.get('following_count')}")
    else:
        print("❌ Instagram login failed")
        try:
            error_data = response.json()
            print(f"Error: {error_data}")
        except:
            print(f"Raw response: {response.text}")
    
    # 3. Test Instagram verification for withdrawal
    print("\n3. 💰 Testing Instagram verification for withdrawal...")
    verification_data = {
        "instagram_username": instagram_username,
        "amount": 100
    }
    
    response = requests.post(f"{BASE_URL}/coins/verify-instagram", json=verification_data, headers=headers)
    print(f"Instagram Verification Status: {response.status_code}")
    print(f"Response: {response.text}")
    
    # 4. Test Instagram profile fetch
    print("\n4. 👤 Testing Instagram profile fetch...")
    response = requests.get(f"{BASE_URL}/instagram/profile/{instagram_username}")
    print(f"Profile Fetch Status: {response.status_code}")
    if response.status_code == 200:
        profile_data = response.json()
        print(f"Profile data: {json.dumps(profile_data, indent=2)}")
    else:
        print(f"Profile fetch failed: {response.text}")

if __name__ == "__main__":
    test_instagram_integration()
