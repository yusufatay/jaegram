#!/usr/bin/env python3
"""
Test Instagram login bypass for test user
"""

import requests
import json

BASE_URL = "http://localhost:8000"
TEST_USERNAME = "testuser"
TEST_PASSWORD = "testpassword123"

def test_instagram_bypass():
    """Test Instagram login bypass for test user"""
    print("🚀 Testing Instagram Login Bypass for Test User")
    print("=" * 60)
    
    # Test Instagram login endpoint with test user credentials
    print(f"📸 Testing Instagram login for test user: {TEST_USERNAME}")
    
    instagram_login_data = {
        "username": TEST_USERNAME,
        "password": TEST_PASSWORD
    }
    
    try:
        response = requests.post(f"{BASE_URL}/login-instagram", json=instagram_login_data)
        print(f"📊 Response Status: {response.status_code}")
        
        if response.status_code == 200:
            print("✅ INSTAGRAM LOGIN BYPASS SUCCESSFUL!")
            response_data = response.json()
            
            print("\n📋 Response Data:")
            print(f"   🔑 Access Token: {'✓ Present' if response_data.get('access_token') else '✗ Missing'}")
            print(f"   👤 User ID: {response_data.get('user_id')}")
            print(f"   📱 Instagram Username: {response_data.get('username')}")
            print(f"   📋 Full Name: {response_data.get('full_name')}")
            print(f"   👥 Followers: {response_data.get('followers_count')}")
            print(f"   🔗 Following: {response_data.get('following_count')}")
            print(f"   💬 Message: {response_data.get('message')}")
            
            user_data = response_data.get('user_data', {})
            print(f"   🧪 Test Mode: {user_data.get('test_mode')}")
            print(f"   ⚡ Bypass Instagram: {user_data.get('bypass_instagram')}")
            print(f"   💰 Coins: {user_data.get('coins')}")
            
            # Test an authenticated endpoint with the token
            access_token = response_data.get('access_token')
            if access_token:
                print("\n🔐 Testing authenticated endpoint with bypass token...")
                headers = {"Authorization": f"Bearer {access_token}"}
                
                profile_response = requests.get(f"{BASE_URL}/profile", headers=headers)
                print(f"   Profile endpoint status: {profile_response.status_code}")
                
                if profile_response.status_code == 200:
                    profile_data = profile_response.json()
                    print(f"   ✅ Profile data retrieved successfully")
                    print(f"   Username: {profile_data.get('username')}")
                    print(f"   Instagram Username: {profile_data.get('instagram_username')}")
                    print(f"   Coin Balance: {profile_data.get('coin_balance')}")
                else:
                    print(f"   ❌ Profile endpoint failed: {profile_response.text}")
            
            return True
            
        else:
            print("❌ INSTAGRAM LOGIN BYPASS FAILED")
            print(f"Error Response: {response.text}")
            return False
            
    except Exception as e:
        print(f"❌ Error during test: {e}")
        return False

def test_normal_instagram_credentials():
    """Test with fake Instagram credentials to verify normal flow still works"""
    print("\n" + "=" * 60)
    print("🔍 Testing Normal Instagram Flow (should fail)")
    
    fake_instagram_data = {
        "username": "fake_instagram_user",
        "password": "fake_password"
    }
    
    try:
        response = requests.post(f"{BASE_URL}/login-instagram", json=fake_instagram_data)
        print(f"📊 Response Status: {response.status_code}")
        
        if response.status_code in [400, 401, 404]:
            print("✅ Normal Instagram flow correctly rejects fake credentials")
        else:
            print(f"⚠️  Unexpected response: {response.text}")
            
    except Exception as e:
        print(f"❌ Error during normal flow test: {e}")

if __name__ == "__main__":
    print("🧪 INSTAGRAM LOGIN BYPASS TEST")
    print("=" * 60)
    
    success = test_instagram_bypass()
    test_normal_instagram_credentials()
    
    print("\n" + "=" * 60)
    print("📋 TEST SUMMARY")
    print("=" * 60)
    
    if success:
        print("✅ Test user Instagram bypass: WORKING")
        print("✅ Mock Instagram data: PROVIDED")
        print("✅ Authentication token: GENERATED")
        print("✅ Test completed successfully!")
    else:
        print("❌ Test user Instagram bypass: FAILED")
        print("❌ Check server logs for details")
    
    print("=" * 60)
