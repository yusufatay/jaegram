#!/usr/bin/env python3
"""
Script to test the created test user login functionality.
This will verify that the test user can log in without Instagram verification.
"""

import requests
import json

# Test configuration
BASE_URL = "http://localhost:8000"  # Adjust if your server runs on a different port
TEST_USERNAME = "testuser"
TEST_PASSWORD = "testpassword123"

def test_user_login():
    """Test login with the created test user"""
    print("Testing test user login...")
    
    # Prepare login data
    login_data = {
        "username": TEST_USERNAME,
        "password": TEST_PASSWORD
    }
    
    try:
        # Test login endpoint
        response = requests.post(
            f"{BASE_URL}/login",
            data=login_data,
            headers={"Content-Type": "application/x-www-form-urlencoded"}
        )
        
        print(f"Login response status: {response.status_code}")
        print(f"Login response: {response.text}")
        
        if response.status_code == 200:
            response_data = response.json()
            access_token = response_data.get("access_token")
            
            if access_token:
                print("✅ LOGIN SUCCESSFUL!")
                print(f"Access token received: {access_token[:50]}...")
                
                # Test authenticated endpoint
                test_authenticated_endpoint(access_token)
            else:
                print("❌ Login successful but no access token received")
        else:
            print(f"❌ Login failed with status {response.status_code}")
            print(f"Error: {response.text}")
            
    except requests.exceptions.ConnectionError:
        print("❌ Cannot connect to server. Make sure the backend is running on http://localhost:8000")
    except Exception as e:
        print(f"❌ Error during login test: {e}")

def test_authenticated_endpoint(access_token):
    """Test an authenticated endpoint using the received token"""
    print("\nTesting authenticated endpoint...")
    
    headers = {
        "Authorization": f"Bearer {access_token}",
        "Content-Type": "application/json"
    }
    
    try:
        # Test user profile endpoint
        response = requests.get(f"{BASE_URL}/user/profile", headers=headers)
        
        print(f"Profile response status: {response.status_code}")
        print(f"Profile response: {response.text}")
        
        if response.status_code == 200:
            print("✅ AUTHENTICATED REQUEST SUCCESSFUL!")
            profile_data = response.json()
            print(f"User ID: {profile_data.get('id')}")
            print(f"Username: {profile_data.get('username')}")
            print(f"Instagram Username: {profile_data.get('instagram_username')}")
            print(f"Instagram PK: {profile_data.get('instagram_pk')}")
            print(f"Coin Balance: {profile_data.get('coin_balance')}")
        else:
            print(f"❌ Authenticated request failed with status {response.status_code}")
            
    except Exception as e:
        print(f"❌ Error during authenticated request: {e}")

def test_instagram_endpoints(access_token):
    """Test Instagram-related endpoints"""
    print("\nTesting Instagram-related endpoints...")
    
    headers = {
        "Authorization": f"Bearer {access_token}",
        "Content-Type": "application/json"
    }
    
    try:
        # Test Instagram status endpoint
        response = requests.get(f"{BASE_URL}/instagram/status", headers=headers)
        
        print(f"Instagram status response: {response.status_code}")
        print(f"Instagram status: {response.text}")
        
        if response.status_code == 200:
            print("✅ Instagram status check successful!")
        else:
            print(f"❌ Instagram status check failed")
            
    except Exception as e:
        print(f"❌ Error during Instagram endpoint test: {e}")

if __name__ == "__main__":
    print("="*60)
    print("TEST USER LOGIN VERIFICATION")
    print("="*60)
    print(f"Testing login for user: {TEST_USERNAME}")
    print(f"Server URL: {BASE_URL}")
    print("="*60)
    
    test_user_login()
    
    print("\n" + "="*60)
    print("TEST COMPLETED")
    print("="*60)
