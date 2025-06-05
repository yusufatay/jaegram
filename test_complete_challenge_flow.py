#!/usr/bin/env python3
"""
Complete End-to-End Challenge Resolution Flow Test

This script tests the entire Instagram challenge verification process:
1. Trigger challenge with login attempt
2. Receive challenge response with contact point
3. Submit verification code (user input required)
4. Verify successful authentication
"""

import requests
import json
import time

# Backend API base URL
BASE_URL = "http://localhost:8000"

def test_login_trigger_challenge():
    """Test login that should trigger a challenge"""
    print("🔄 Step 1: Testing login that triggers challenge...")
    
    login_data = {
        "username": "luvmef",
        "password": "asgsag2"
    }
    
    try:
        response = requests.post(f"{BASE_URL}/login-instagram", json=login_data)
        print(f"📡 Response Status: {response.status_code}")
        print(f"📝 Response Headers: {dict(response.headers)}")
        
        if response.status_code == 200:
            data = response.json()
            print(f"📋 Response Data: {json.dumps(data, indent=2)}")
            
            if data.get("challenge_required"):
                print("✅ Challenge required detected successfully!")
                return data
            else:
                print("❌ Expected challenge but got successful login")
                return None
        else:
            print(f"❌ Unexpected status code: {response.status_code}")
            print(f"📋 Response: {response.text}")
            return None
            
    except Exception as e:
        print(f"❌ Login request failed: {e}")
        return None

def test_challenge_resolution(username, verification_code):
    """Test challenge resolution with verification code"""
    print(f"🔄 Step 2: Testing challenge resolution for {username}...")
    
    challenge_data = {
        "username": username,
        "challenge_code": verification_code
    }
    
    try:
        response = requests.post(f"{BASE_URL}/login-instagram-challenge", json=challenge_data)
        print(f"📡 Response Status: {response.status_code}")
        print(f"📝 Response Headers: {dict(response.headers)}")
        
        data = response.json()
        print(f"📋 Response Data: {json.dumps(data, indent=2)}")
        
        if response.status_code == 200 and data.get("success"):
            print("✅ Challenge resolved successfully!")
            return True
        else:
            print(f"❌ Challenge resolution failed: {data.get('message', 'Unknown error')}")
            return False
            
    except Exception as e:
        print(f"❌ Challenge resolution request failed: {e}")
        return False

def test_post_challenge_login(username, password):
    """Test login after successful challenge resolution"""
    print(f"🔄 Step 3: Testing login after challenge resolution...")
    
    login_data = {
        "username": username,
        "password": password
    }
    
    try:
        response = requests.post(f"{BASE_URL}/instagram/login", json=login_data)
        print(f"📡 Response Status: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            print(f"📋 Response Data: {json.dumps(data, indent=2)}")
            
            if data.get("success") and not data.get("challenge_required"):
                print("✅ Post-challenge login successful!")
                return True
            elif data.get("challenge_required"):
                print("⚠️ Another challenge required - this may be normal")
                return False
            else:
                print("❌ Post-challenge login failed")
                return False
        else:
            print(f"❌ Post-challenge login failed with status: {response.status_code}")
            return False
            
    except Exception as e:
        print(f"❌ Post-challenge login request failed: {e}")
        return False

def main():
    print("🚀 Starting Complete Instagram Challenge Flow Test")
    print("=" * 60)
    
    # Step 1: Trigger challenge
    challenge_data = test_login_trigger_challenge()
    if not challenge_data:
        print("❌ Test failed at challenge trigger step")
        return
    
    print("\n" + "=" * 60)
    
    # Extract challenge details
    challenge_details = challenge_data.get("challenge_details", {})
    contact_point = challenge_details.get("step_data", {}).get("contact_point", "Unknown")
    
    print(f"📧 Challenge sent to: {contact_point}")
    print("\n🔑 Please check your email/SMS for the verification code")
    print("📱 The code should arrive within a few minutes")
    
    # Get verification code from user
    verification_code = input("\n📝 Enter the verification code you received: ").strip()
    
    if not verification_code:
        print("❌ No verification code provided")
        return
    
    print(f"🔢 Using verification code: {verification_code}")
    print("\n" + "=" * 60)
    
    # Step 2: Resolve challenge
    success = test_challenge_resolution("luvmef", verification_code)
    if not success:
        print("❌ Test failed at challenge resolution step")
        print("💡 The verification code might be incorrect or expired")
        return
    
    print("\n" + "=" * 60)
    
    # Step 3: Test post-challenge login
    time.sleep(2)  # Brief pause before retry
    post_login_success = test_post_challenge_login("luvmef", "asgsag2")
    
    print("\n" + "=" * 60)
    print("📊 TEST SUMMARY:")
    print(f"✅ Challenge Trigger: Success")
    print(f"{'✅' if success else '❌'} Challenge Resolution: {'Success' if success else 'Failed'}")
    print(f"{'✅' if post_login_success else '❌'} Post-Challenge Login: {'Success' if post_login_success else 'Failed'}")
    
    if success and post_login_success:
        print("\n🎉 ALL TESTS PASSED! Instagram challenge flow is working correctly!")
    elif success:
        print("\n⚠️ Challenge resolution works, but post-challenge login may need investigation")
    else:
        print("\n❌ Challenge resolution failed - check verification code or implementation")

if __name__ == "__main__":
    main()
