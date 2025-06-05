#!/usr/bin/env python3
"""
Test Script for Empty Instagram Account Handling
This tests the enhanced Instagram scraping system with proper empty account detection
"""
import requests
import json
import time

BASE_URL = "http://localhost:8000"

def test_empty_account_handling():
    """Test the enhanced empty account detection and handling"""
    print("🧪 Testing Enhanced Instagram Empty Account Handling")
    print("=" * 60)
    
    # Using the same test account that we know is empty
    instagram_username = "semihulusoyw"
    instagram_password = "m.m.123456"
    
    print(f"📸 Testing with empty Instagram account: {instagram_username}")
    print("-" * 60)
    
    # 1. Test Instagram Login
    print("\n1. 📸 Testing Instagram Login...")
    instagram_login_data = {
        "username": instagram_username,
        "password": instagram_password
    }
    
    response = requests.post(f"{BASE_URL}/login-instagram", json=instagram_login_data)
    print(f"   Status: {response.status_code}")
    
    if response.status_code == 200:
        print("   ✅ Login successful!")
        login_data = response.json()
        token = login_data.get("access_token")
        
        if not token:
            print("   ❌ No access token received")
            return
            
        headers = {"Authorization": f"Bearer {token}"}
        
        # 2. Test Profile Data with Empty Account Detection
        print("\n2. 👤 Testing Enhanced Profile Data...")
        response = requests.get(f"{BASE_URL}/user/instagram-profile", headers=headers)
        print(f"   Status: {response.status_code}")
        
        if response.status_code == 200:
            profile_data = response.json()
            print("   ✅ Profile data retrieved successfully!")
            
            profile = profile_data.get("profile", {})
            print(f"   📊 Username: {profile.get('username')}")
            print(f"   📊 Full Name: {profile.get('full_name')}")
            print(f"   📊 Posts: {profile.get('media_count', 0)}")
            print(f"   📊 Verified: {profile.get('is_verified', False)}")
            print(f"   📊 Account Status: {profile.get('account_status', 'unknown')}")
            print(f"   📊 Status Message: {profile.get('account_status_message', 'N/A')}")
            
            # Check for enhanced empty account handling
            if profile.get("account_status") == "new_empty":
                print("   🎯 Empty account detected and handled correctly!")
                if "empty_account_notice" in profile:
                    print(f"   💡 Notice: {profile['empty_account_notice']}")
            elif profile.get("account_status") == "active":
                print("   🎯 Account status: Active with content")
            else:
                print("   ⚠️  Unknown account status")
                
        else:
            print(f"   ❌ Profile data failed: {response.text}")
        
        # 3. Test Manual Profile Refresh
        print("\n3. 🔄 Testing Manual Profile Refresh...")
        response = requests.post(f"{BASE_URL}/user/refresh-instagram-profile", headers=headers)
        print(f"   Status: {response.status_code}")
        
        if response.status_code == 200:
            refresh_data = response.json()
            print(f"   ✅ Refresh successful: {refresh_data.get('message', 'No message')}")
        else:
            print(f"   ❌ Refresh failed: {response.text}")
            
        # 4. Test Instagram Credentials
        print("\n4. 🔑 Testing Instagram Credentials...")
        response = requests.get(f"{BASE_URL}/user/instagram-credentials", headers=headers)
        print(f"   Status: {response.status_code}")
        
        if response.status_code == 200:
            cred_data = response.json()
            print(f"   ✅ Credentials retrieved!")
            print(f"   📊 Connected: {cred_data.get('instagram_connected', False)}")
            print(f"   📊 Username: {cred_data.get('instagram_username', 'N/A')}")
            print(f"   📊 Session Valid: {cred_data.get('session_valid', False)}")
            print(f"   📊 Last Sync: {cred_data.get('last_sync', 'Never')}")
        else:
            print(f"   ❌ Credentials failed: {response.text}")
            
    else:
        print(f"   ❌ Login failed: {response.text}")
    
    print("\n" + "=" * 60)
    print("🏁 Test completed!")

if __name__ == "__main__":
    try:
        test_empty_account_handling()
    except KeyboardInterrupt:
        print("\n⚠️  Test interrupted by user")
    except Exception as e:
        print(f"\n❌ Test failed with error: {e}")
        import traceback
        traceback.print_exc()
