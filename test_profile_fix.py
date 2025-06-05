#!/usr/bin/env python3
"""
Test profile endpoint to verify Instagram integration and 404 fix
"""
import requests
import json

BASE_URL = "http://localhost:8000"

def test_profile_endpoint():
    print("🧪 Testing Profile Endpoint Integration")
    print("=" * 50)
    
    # 1. Login first
    login_data = {
        "username": "testuser",
        "password": "testpass"
    }
    
    response = requests.post(f"{BASE_URL}/login", data=login_data)
    if response.status_code != 200:
        print("❌ Login failed")
        return
    
    token = response.json()["access_token"]
    headers = {"Authorization": f"Bearer {token}"}
    
    # 2. Test profile endpoint
    print("\n1. 👤 Testing Profile Endpoint")
    response = requests.get(f"{BASE_URL}/profile", headers=headers)
    print(f"   Status: {response.status_code}")
    
    if response.status_code == 200:
        profile_data = response.json()
        print("   ✅ Profile endpoint successful")
        print(f"   Username: {profile_data.get('username')}")
        print(f"   Full Name: {profile_data.get('full_name')}")
        print(f"   Profile Pic URL: {profile_data.get('profile_pic_url')}")
        print(f"   Followers Count: {profile_data.get('followers_count')}")
        print(f"   Following Count: {profile_data.get('following_count')}")
        print(f"   Instagram Stats: {profile_data.get('instagram_stats')}")
        
        # Check for broken URLs
        profile_pic = profile_data.get('profile_pic_url')
        if profile_pic:
            if "example.com/test_profile.jpg" in profile_pic:
                print("   ❌ Still returning broken URL!")
                return False
            else:
                print(f"   ✅ Valid profile pic URL: {profile_pic}")
        else:
            print("   ✅ No profile pic (null) - acceptable")
            
        return True
    else:
        print(f"   ❌ Profile endpoint failed: {response.text}")
        return False

    # 3. Test leaderboard endpoint
    print("\n2. 🏆 Testing Leaderboard Endpoint")
    response = requests.get(f"{BASE_URL}/social/leaderboard", headers=headers)
    print(f"   Status: {response.status_code}")
    
    if response.status_code == 200:
        leaderboard_data = response.json()
        print("   ✅ Leaderboard endpoint successful")
        print(f"   Total entries: {len(leaderboard_data)}")
        
        # Check profile pics in leaderboard
        broken_count = 0
        for entry in leaderboard_data:
            profile_pic = entry.get('profile_pic_url')
            if profile_pic and "example.com/test_profile.jpg" in profile_pic:
                broken_count += 1
        
        if broken_count > 0:
            print(f"   ❌ Found {broken_count} broken URLs in leaderboard")
            return False
        else:
            print("   ✅ No broken URLs in leaderboard")
            return True
    else:
        print(f"   ❌ Leaderboard endpoint failed: {response.text}")
        return False

if __name__ == "__main__":
    success = test_profile_endpoint()
    if success:
        print("\n🎉 All tests passed! 404 error should be resolved.")
    else:
        print("\n❌ Some tests failed. Check the output above.")
