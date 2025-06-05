#!/usr/bin/env python3
"""
Test script for manual Instagram login endpoints
"""

import requests
import json
import time

BASE_URL = "http://localhost:8000"

def test_admin_login():
    """Test admin login to get a token"""
    print("🔐 Testing admin login...")
    
    response = requests.post(f"{BASE_URL}/login", json={
        "username": "admin",
        "password": "admin"
    })
    
    if response.status_code == 200:
        data = response.json()
        token = data.get("access_token")
        print(f"✅ Admin login successful, token: {token[:20]}...")
        return token
    else:
        print(f"❌ Admin login failed: {response.status_code} - {response.text}")
        return None

def test_open_manual_login(token):
    """Test opening manual Instagram login"""
    print("\n🌐 Testing manual Instagram login opening...")
    
    headers = {"Authorization": f"Bearer {token}"}
    response = requests.post(f"{BASE_URL}/instagram/open-manual-login", 
                           headers=headers,
                           json={"username": "test_user"})
    
    if response.status_code == 200:
        data = response.json()
        print(f"✅ Manual login opened: {data.get('message')}")
        print(f"📋 Instructions: {data.get('instructions')}")
        return True
    else:
        print(f"❌ Failed to open manual login: {response.status_code} - {response.text}")
        return False

def test_check_login_status(token):
    """Test checking login status"""
    print("\n🔍 Testing login status check...")
    
    headers = {"Authorization": f"Bearer {token}"}
    response = requests.get(f"{BASE_URL}/instagram/check-login-status", headers=headers)
    
    if response.status_code == 200:
        data = response.json()
        print(f"✅ Status check successful: {data.get('status')} - {data.get('message')}")
        return data
    else:
        print(f"❌ Status check failed: {response.status_code} - {response.text}")
        return None

def test_close_browser(token):
    """Test closing Instagram browser"""
    print("\n🔴 Testing browser close...")
    
    headers = {"Authorization": f"Bearer {token}"}
    response = requests.post(f"{BASE_URL}/instagram/close-browser", headers=headers)
    
    if response.status_code == 200:
        data = response.json()
        print(f"✅ Browser close: {data.get('message')}")
        return True
    else:
        print(f"❌ Browser close failed: {response.status_code} - {response.text}")
        return False

def main():
    print("🧪 Testing Manual Instagram Login Endpoints")
    print("=" * 50)
    
    # Test admin login
    token = test_admin_login()
    if not token:
        return
    
    # Test opening manual login
    if test_open_manual_login(token):
        print("\n⏳ Waiting 5 seconds before checking status...")
        time.sleep(5)
        
        # Test status check
        status_data = test_check_login_status(token)
        
        # Test closing browser
        test_close_browser(token)
    
    print("\n🎉 Manual login endpoint testing completed!")

if __name__ == "__main__":
    main()
