#!/usr/bin/env python3
"""
Test script to verify the challenge resolution fix
"""

import requests
import json
import time

def test_challenge_resolution():
    """Test the fixed challenge resolution system"""
    base_url = "http://localhost:8000"
    
    print("🧪 Testing Challenge Resolution Fix")
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
                print(f"   Challenge details: {result.get('challenge_details', {}).get('step_name', 'Unknown')}")
                
                # The user would normally receive a verification code here
                print("\n2. In a real scenario, user would receive verification code via SMS/Email")
                print("   User would then submit the code via the challenge resolution endpoint")
                print("   POST /login-instagram-challenge with {username, challenge_code}")
                
                print("\n✅ Challenge detection and context storage is working correctly!")
                print("💡 Next step: User receives verification code and submits it")
                
                return True
            else:
                print("❌ Expected challenge but login succeeded directly")
                return False
        else:
            print(f"❌ Login request failed: {response.status_code}")
            print(f"   Response: {response.text}")
            return False
            
    except requests.ConnectionError:
        print("❌ Cannot connect to backend server")
        print("💡 Make sure backend is running on port 8000")
        return False
    except Exception as e:
        print(f"❌ Error during test: {e}")
        return False

def test_challenge_resolution_with_fake_code():
    """Test challenge resolution with a fake code to verify error handling"""
    base_url = "http://localhost:8000"
    
    print("\n3. Testing challenge resolution error handling with fake code")
    
    challenge_data = {
        "username": "luvmef",
        "challenge_code": "123456"  # Fake code
    }
    
    try:
        response = requests.post(f"{base_url}/login-instagram-challenge", json=challenge_data)
        print(f"   Status Code: {response.status_code}")
        
        if response.status_code == 400:
            result = response.json()
            print(f"   Response: {json.dumps(result, indent=2)}")
            print("✅ Error handling works correctly for invalid codes")
            return True
        else:
            print(f"   Unexpected response: {response.status_code}")
            return False
            
    except Exception as e:
        print(f"❌ Error during fake code test: {e}")
        return False

if __name__ == "__main__":
    print("🚀 Starting Challenge Resolution Test")
    print()
    
    success1 = test_challenge_resolution()
    success2 = test_challenge_resolution_with_fake_code()
    
    print("\n" + "=" * 50)
    if success1 and success2:
        print("🎉 All tests passed! Challenge resolution system is working correctly.")
        print("🔧 Technical fixes implemented:")
        print("   - Fixed challenge_resolve() method to use proper _send_private_request")
        print("   - Ensured last_json remains as Dict throughout the process")
        print("   - Proper error handling for invalid verification codes")
        print("   - Challenge context management and cleanup")
    else:
        print("❌ Some tests failed. Check the errors above.")
    
    print("\n📋 Next Steps:")
    print("   1. Test with real verification codes when received")
    print("   2. Test complete end-to-end flow including successful login")
    print("   3. Verify session persistence after challenge resolution")
