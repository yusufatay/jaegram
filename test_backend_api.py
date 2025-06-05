#!/usr/bin/env python3

import requests
import json

def test_instagram_login():
    """Test Instagram login via backend API"""
    try:
        print("🔄 Testing Instagram login via backend API...")
        
        # Test with mirzzassi credentials
        login_data = {
            "username": "mirzzassi", 
            "password": "password123"  # Replace with actual password
        }
        
        response = requests.post(
            "http://localhost:8000/login-instagram",
            json=login_data,
            headers={"Content-Type": "application/json"}
        )
        
        print(f"Status Code: {response.status_code}")
        
        if response.status_code == 200:
            result = response.json()
            print("✅ Instagram login successful!")
            print(json.dumps(result, indent=2))
            
            if "user_data" in result:
                user_data = result["user_data"]
                print(f"\n📊 Profile Data:")
                print(f"   - Username: {user_data.get('username')}")
                print(f"   - Followers: {user_data.get('follower_count', 0)}")
                print(f"   - Following: {user_data.get('following_count', 0)}")
                print(f"   - Posts: {user_data.get('media_count', 0)}")
                
        else:
            print(f"❌ Instagram login failed")
            try:
                error_data = response.json()
                print(json.dumps(error_data, indent=2))
                
                if error_data.get("error_type") == "challenge_required":
                    print("⚠️ Challenge required - this is expected for some accounts")
                    print("Challenge data:", error_data.get("challenge_data"))
                    
            except:
                print(f"Response text: {response.text}")
                
    except Exception as e:
        print(f"❌ Error testing Instagram login: {e}")

def test_test_user():
    """Test with the bypass test user"""
    try:
        print("\n🔄 Testing with test user...")
        
        login_data = {
            "username": "testuser",
            "password": "testpassword123"
        }
        
        response = requests.post(
            "http://localhost:8000/login-instagram", 
            json=login_data,
            headers={"Content-Type": "application/json"}
        )
        
        print(f"Status Code: {response.status_code}")
        
        if response.status_code == 200:
            result = response.json()
            print("✅ Test user login successful!")
            
            if result.get("followers_count") or result.get("user_data", {}).get("followers_count"):
                followers = result.get("followers_count") or result.get("user_data", {}).get("followers_count", 0)
                following = result.get("following_count") or result.get("user_data", {}).get("following_count", 0)
                print(f"   - Followers: {followers}")
                print(f"   - Following: {following}")
                
                if followers > 0 and following > 0:
                    print("✅ Profile data is being synced correctly!")
                else:
                    print("⚠️ Profile data shows 0|0 - sync issue")
        else:
            error_data = response.json()
            print(f"❌ Test user login failed: {error_data}")
            
    except Exception as e:
        print(f"❌ Error testing test user: {e}")

if __name__ == "__main__":
    print("=" * 60)
    print("BACKEND INSTAGRAM API TEST")
    print("=" * 60)
    
    # Test 1: Real Instagram login
    test_instagram_login()
    
    # Test 2: Test user bypass
    test_test_user()
    
    print("\n" + "=" * 60)
