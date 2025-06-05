#!/usr/bin/env python3
"""
Real challenge resolution test
"""

import requests
import json

def test_real_challenge():
    """Test real challenge resolution with actual code"""
    
    print("🔥 Real Challenge Resolution Test")
    print("=" * 50)
    
    # Use challenge data from server logs - we can see it's working and expecting email
    # The contact point is: n******f@w*****.com
    
    print("📧 Testing with challenge code for luvmef account")
    print("Contact point: n******f@w*****.com")
    print()
    
    # We'll test the challenge resolution endpoint directly
    challenge_data = {
        "username": "luvmef",
        "challenge_code": "123456"  # You need to get the real code from email
    }
    
    print(f"🚀 Testing challenge resolution...")
    print(f"Username: {challenge_data['username']}")
    print(f"Code: {challenge_data['challenge_code']}")
    print()
    
    # Note: You need to get the actual 6-digit code from the email n******f@w*****.com
    print("⚡ To complete the test:")
    print("1. Check the email n******f@w*****.com for Instagram verification code")
    print("2. Replace '123456' in this script with the real 6-digit code")
    print("3. Run this script again")
    print()
    
    print("📱 When you have the real code, you can test like this:")
    print(f"curl -X POST http://localhost:8000/login-instagram-challenge \\")
    print(f"  -H 'Content-Type: application/json' \\")
    print(f"  -d '{json.dumps(challenge_data)}'")
    print()
    
    try:
        print("📡 Sending challenge resolution request...")
        response = requests.post("http://localhost:8000/login-instagram-challenge", json=challenge_data)
        
        print(f"📊 Response Status: {response.status_code}")
        
        if response.status_code == 200:
            result = response.json()
            print(f"✅ Challenge resolution result:")
            print(json.dumps(result, indent=2, ensure_ascii=False))
        else:
            print(f"❌ Request failed with status {response.status_code}")
            try:
                error_result = response.json()
                print(f"Error: {json.dumps(error_result, indent=2, ensure_ascii=False)}")
            except:
                print(f"Raw response: {response.text}")
                
    except Exception as e:
        print(f"❌ Test failed: {e}")

if __name__ == "__main__":
    test_real_challenge()
