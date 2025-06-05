#!/usr/bin/env python3
"""
Complete End-to-End Challenge Test with New Bloks Format Support
"""

import requests
import json
import time

BASE_URL = "http://localhost:8000"

def test_complete_flow():
    """Test the complete challenge flow with real verification code"""
    print("🚀 Complete Challenge Flow Test")
    print("=" * 60)
    
    # Step 1: Trigger challenge
    print("1. 🔐 Triggering Instagram challenge...")
    
    login_data = {
        "username": "luvmef",
        "password": "asgsag2"
    }
    
    try:
        response = requests.post(f"{BASE_URL}/login-instagram", json=login_data)
        print(f"   📡 Status: {response.status_code}")
        
        if response.status_code == 200:
            result = response.json()
            
            if result.get("challenge_required"):
                print("✅ Challenge triggered successfully!")
                print(f"   📧 Contact: {result.get('challenge_details', {}).get('step_data', {}).get('contact_point', 'Unknown')}")
                print(f"   🔄 Step: {result.get('challenge_details', {}).get('step_name', 'Unknown')}")
                
                # Step 2: Get verification code from user
                print("\n2. 📬 Please check your email for verification code...")
                print("   Check: n******f@w*****.com")
                
                verification_code = input("\n   Enter verification code: ").strip()
                
                if not verification_code:
                    print("❌ No code entered, test cancelled")
                    return False
                
                # Step 3: Submit verification code
                print(f"\n3. 🔑 Submitting verification code: {verification_code}")
                
                challenge_data = {
                    "username": "luvmef",
                    "challenge_code": verification_code
                }
                
                challenge_response = requests.post(f"{BASE_URL}/login-instagram-challenge", json=challenge_data)
                print(f"   📡 Status: {challenge_response.status_code}")
                
                try:
                    challenge_result = challenge_response.json()
                    print(f"   📝 Response: {json.dumps(challenge_result, indent=2)}")
                    
                    if challenge_response.status_code == 200 and challenge_result.get("success"):
                        print("🎉 Challenge resolved successfully!")
                        print(f"   👤 Username: {challenge_result.get('username')}")
                        print(f"   🆔 User ID: {challenge_result.get('user_id')}")
                        return True
                    else:
                        print(f"❌ Challenge failed: {challenge_result.get('error', 'Unknown error')}")
                        return False
                        
                except Exception as e:
                    print(f"❌ Failed to parse challenge response: {e}")
                    print(f"   Raw response: {challenge_response.text}")
                    return False
            else:
                print("❌ Challenge not triggered")
                if result.get("success"):
                    print("   ℹ️  Login was successful without challenge")
                return False
        else:
            print(f"❌ Login request failed: {response.status_code}")
            try:
                error_result = response.json()
                print(f"   Error: {error_result}")
            except:
                print(f"   Raw response: {response.text}")
            return False
            
    except Exception as e:
        print(f"❌ Request failed: {e}")
        return False

def test_fake_code():
    """Test with fake code to verify error handling"""
    print("\n" + "=" * 60)
    print("🧪 Testing Error Handling with Fake Code")
    
    # First trigger challenge
    login_data = {"username": "luvmef", "password": "asgsag2"}
    
    try:
        response = requests.post(f"{BASE_URL}/login-instagram", json=login_data)
        if response.status_code == 200 and response.json().get("challenge_required"):
            print("✅ Challenge triggered for error test")
            
            # Submit fake code
            challenge_data = {"username": "luvmef", "challenge_code": "000000"}
            
            challenge_response = requests.post(f"{BASE_URL}/login-instagram-challenge", json=challenge_data)
            challenge_result = challenge_response.json()
            
            print(f"   📡 Status: {challenge_response.status_code}")
            print(f"   📝 Response: {json.dumps(challenge_result, indent=2)}")
            
            if not challenge_result.get("success"):
                print("✅ Error handling works correctly")
                return True
            else:
                print("❌ Fake code was accepted (unexpected)")
                return False
        else:
            print("❌ Could not trigger challenge for error test")
            return False
            
    except Exception as e:
        print(f"❌ Error test failed: {e}")
        return False

if __name__ == "__main__":
    print("🔧 Testing New Bloks Challenge Format Support")
    print("   - Handles both legacy and new challenge formats")
    print("   - Uses instagrapi's built-in challenge resolution")
    print("   - Comprehensive error handling")
    print()
    
    # Run tests
    success = test_complete_flow()
    
    if success:
        # Test error handling
        test_fake_code()
    
    print("\n" + "=" * 60)
    if success:
        print("🎉 All tests completed! Challenge resolution is working.")
    else:
        print("❌ Tests failed. Check the output above for details.")
    print("=" * 60)
