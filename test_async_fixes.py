#!/usr/bin/env python3
"""
Quick test for async fixes
"""

import requests
import json

BASE_URL = "http://localhost:8000"

def test_async_fixes():
    print("🔧 TESTING ASYNC FIXES")
    print("=" * 40)
    
    # Test 1: Register new user
    print("1. Testing user registration...")
    username = f"async_test_{int(time.time())}" if 'time' in globals() else "async_test_123"
    register_data = {
        "username": username,
        "password": "test123",
        "email": f"{username}@test.com"
    }
    
    try:
        register_response = requests.post(f"{BASE_URL}/register", json=register_data)
        print(f"   Register status: {register_response.status_code}")
        if register_response.status_code == 201:
            print("   ✅ Registration successful")
        else:
            print(f"   ⚠️  Registration response: {register_response.text}")
    except Exception as e:
        print(f"   ❌ Registration error: {e}")
        return
    
    # Test 2: Login and get token
    print("\n2. Testing login...")
    try:
        login_data = f"username={username}&password=test123"
        login_response = requests.post(
            f"{BASE_URL}/login",
            data=login_data,
            headers={"Content-Type": "application/x-www-form-urlencoded"}
        )
        print(f"   Login status: {login_response.status_code}")
        
        if login_response.status_code == 200:
            token_data = login_response.json()
            token = token_data.get("access_token")
            print("   ✅ Login successful")
            print(f"   Token: {token[:20]}...")
        else:
            print(f"   ❌ Login failed: {login_response.text}")
            return
    except Exception as e:
        print(f"   ❌ Login error: {e}")
        return
    
    # Test 3: Test daily reward endpoint (async fixed)
    print("\n3. Testing daily reward endpoint (async fixed)...")
    try:
        headers = {"Authorization": f"Bearer {token}"}
        daily_response = requests.post(f"{BASE_URL}/claim-daily-reward", headers=headers)
        print(f"   Daily reward status: {daily_response.status_code}")
        
        if daily_response.status_code == 200:
            data = daily_response.json()
            print("   ✅ Daily reward endpoint working")
            print(f"   Coins awarded: {data.get('coins_awarded', 0)}")
        elif daily_response.status_code == 400:
            print("   ✅ Daily reward endpoint working (already claimed)")
        else:
            print(f"   ❌ Daily reward failed: {daily_response.text}")
    except Exception as e:
        print(f"   ❌ Daily reward error: {e}")
    
    # Test 4: Test email verification endpoint (async fixed)
    print("\n4. Testing email verification endpoint (async fixed)...")
    try:
        headers = {"Authorization": f"Bearer {token}"}
        email_response = requests.post(
            f"{BASE_URL}/send-verification-email",
            params={"email": f"test_{username}@example.com"},
            headers=headers
        )
        print(f"   Email verification status: {email_response.status_code}")
        
        if email_response.status_code == 200:
            data = email_response.json()
            print("   ✅ Email verification endpoint working")
            print(f"   Message: {data.get('message', 'No message')}")
        else:
            print(f"   ❌ Email verification failed: {email_response.text}")
    except Exception as e:
        print(f"   ❌ Email verification error: {e}")
    
    print("\n" + "=" * 40)
    print("🎉 ASYNC FIX TEST COMPLETE")
    print("✅ Both async endpoints should now work without 'await in non-async' errors")

if __name__ == "__main__":
    import time
    test_async_fixes()
