#!/usr/bin/env python3
"""
Test the challenge URL extraction fix
"""

import requests
import json
import time

def test_challenge_trigger():
    """Test triggering a challenge to see the URL structure"""
    base_url = "http://localhost:8000"
    
    print("🧪 Testing Challenge URL Fix")
    print("=" * 50)
    
    # Test credentials that we know triggers a challenge
    test_username = "luvmef"
    test_password = "asgsag2"
    
    print(f"1. Testing Instagram login with challenge-triggering account: {test_username}")
    
    # Step 1: Attempt login (should trigger challenge)
    login_data = {
        "username": test_username,
        "password": test_password
    }
    
    try:
        response = requests.post(f"{base_url}/login-instagram", json=login_data)
        print(f"   Status Code: {response.status_code}")
        
        if response.status_code == 200:
            result = response.json()
            print(f"   Response: {json.dumps(result, indent=2)}")
            
            if result.get("challenge_required"):
                print("✅ Challenge properly triggered!")
                print(f"   Challenge URL: {result.get('challenge_url')}")
                print(f"   Challenge Details Keys: {list(result.get('challenge_details', {}).keys())}")
                
                # Check if we have the challenge structure we need
                challenge_details = result.get('challenge_details', {})
                if 'challenge' in challenge_details:
                    print(f"   Challenge structure keys: {list(challenge_details['challenge'].keys())}")
                    if 'api_path' in challenge_details['challenge']:
                        print(f"   API Path: {challenge_details['challenge']['api_path']}")
                
                return True
            else:
                print("❌ Challenge not triggered")
                return False
        else:
            print(f"❌ Login failed with status {response.status_code}")
            try:
                error_result = response.json()
                print(f"   Error: {error_result}")
            except:
                print(f"   Raw response: {response.text}")
            return False
            
    except Exception as e:
        print(f"❌ Error during login test: {e}")
        return False

def test_challenge_resolution_with_manual_code():
    """Test challenge resolution - requires manual input"""
    base_url = "http://localhost:8000"
    
    print("\n2. Testing challenge resolution (requires manual verification code)")
    
    # This will test our new challenge resolution logic
    challenge_data = {
        "username": "luvmef",
        "challenge_code": input("Please enter the verification code from your email: ").strip()
    }
    
    if not challenge_data["challenge_code"]:
        print("❌ No verification code provided, skipping test")
        return False
    
    try:
        response = requests.post(f"{base_url}/login-instagram-challenge", json=challenge_data)
        print(f"   Status Code: {response.status_code}")
        
        result = response.json()
        print(f"   Response: {json.dumps(result, indent=2)}")
        
        if response.status_code == 200 and result.get("success"):
            print("✅ Challenge resolved successfully!")
            return True
        else:
            print(f"❌ Challenge resolution failed: {result.get('message', 'Unknown error')}")
            return False
            
    except Exception as e:
        print(f"❌ Challenge resolution request failed: {e}")
        return False

if __name__ == "__main__":
    print("🚀 Challenge URL Fix Test")
    print()
    
    # First test: trigger challenge
    challenge_triggered = test_challenge_trigger()
    
    if challenge_triggered:
        # Second test: resolve challenge (manual input required)
        test_challenge_resolution_with_manual_code()
    
    print("\n" + "=" * 50)
    print("🔧 Challenge URL extraction fix implemented:")
    print("   - Fixed challenge URL extraction from client.challenge_url")
    print("   - Added fallback to stored_last_json['challenge']['api_path']")
    print("   - Implemented proper HTTP session for code submission")
    print("   - Added comprehensive error handling and response parsing")
    print("   - Fixed challenge response structure validation")
