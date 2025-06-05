#!/usr/bin/env python3

import requests
import json

def test_mirzzassi_login():
    """Test mirzzassi Instagram login"""
    print("🔄 Testing mirzzassi Instagram login...")
    
    response = requests.post('http://localhost:8000/login-instagram', 
        json={'username': 'mirzzassi', 'password': 'password123'})
    
    print(f"Status: {response.status_code}")
    
    if response.status_code == 200:
        result = response.json()
        print("✅ Login successful!")
        if 'user_data' in result:
            user_data = result['user_data']
            print(f"Username: {user_data.get('username')}")
            print(f"Followers: {user_data.get('follower_count', 0)}")
            print(f"Following: {user_data.get('following_count', 0)}")
        return True
    elif response.status_code == 500:
        print("❌ Server error - session likely invalid")
        try:
            error_data = response.json()
            print(f"Error: {error_data}")
        except:
            print(f"Raw response: {response.text}")
        return False
    else:
        result = response.json()
        print(f"Error type: {result.get('error_type')}")
        print(f"Message: {result.get('message')}")
        if result.get('error_type') == 'challenge_required':
            print("⚠️ Challenge required - this is expected")
            return "challenge"
        return False

if __name__ == "__main__":
    result = test_mirzzassi_login()
    print(f"\nResult: {result}")
