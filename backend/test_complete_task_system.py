#!/usr/bin/env python3
"""
Test the task system
"""

import requests
import json

BASE_URL = "http://localhost:8000"

def test_login():
    """Test login and get token"""
    login_data = {
        "username": "testuser",
        "password": "testpassword"
    }
    
    response = requests.post(
        f"{BASE_URL}/login",
        data=login_data,
        headers={"Content-Type": "application/x-www-form-urlencoded"}
    )
    
    print(f"Login response status: {response.status_code}")
    print(f"Login response: {response.text}")
    
    if response.status_code == 200:
        return response.json()["access_token"]
    return None

def test_take_task(token):
    """Test taking a task"""
    headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json"
    }
    
    response = requests.post(f"{BASE_URL}/take-task", headers=headers)
    
    print(f"Take task response status: {response.status_code}")
    print(f"Take task response: {response.text}")
    
    return response

def main():
    print("=== Testing Task System ===")
    
    # Test login
    print("\n1. Testing login...")
    token = test_login()
    
    if not token:
        print("Login failed!")
        return
    
    print(f"Login successful! Token: {token[:20]}...")
    
    # Test take task
    print("\n2. Testing take task...")
    response = test_take_task(token)
    
    if response.status_code == 200:
        print("✅ Task taken successfully!")
        print(json.dumps(response.json(), indent=2))
    else:
        print("❌ Failed to take task")
        try:
            error_detail = response.json()
            print(f"Error: {error_detail}")
        except:
            print(f"Raw response: {response.text}")

if __name__ == "__main__":
    main()
