#!/usr/bin/env python3
"""
Test challenge resolution with current verification code
"""

import requests
import json
import time

def test_challenge_resolution():
    print("🔍 Instagram Challenge Resolution Test")
    print("=" * 50)
    
    # Check current challenge status
    print("1. 📊 Checking current challenge status...")
    try:
        status_response = requests.get("http://localhost:8000/instagram/challenge-status/luvmef", timeout=10)
        if status_response.status_code == 200:
            status_data = status_response.json()
            print(f"   ✅ Challenge exists: {status_data.get('has_challenge', False)}")
            if status_data.get('challenge_data'):
                challenge_data = status_data['challenge_data']
                print(f"   📧 Step: {challenge_data.get('step_name', 'N/A')}")
                if 'step_data' in challenge_data:
                    step_data = challenge_data['step_data']
                    print(f"   📧 Contact: {step_data.get('contact_point', 'N/A')}")
                    print(f"   📝 Form type: {step_data.get('form_type', 'N/A')}")
        else:
            print(f"   ❌ Status check failed: {status_response.status_code}")
            return
    except Exception as e:
        print(f"   ❌ Status check error: {e}")
        return
    
    # Test with the provided verification code
    print("\n2. 🔐 Challenge Resolution")
    print("   The account needs email verification.")
    print("   Contact point: n******f@w*****.com")
    
    # Test both the old code and a fresh approach
    verification_codes = ["742856", "000000"]  # Add more codes if needed
    
    for i, verification_code in enumerate(verification_codes):
        print(f"\n   🧪 Test {i+1}: Trying verification code: {verification_code}")
        
        if not verification_code or len(verification_code) != 6 or not verification_code.isdigit():
            print("   ❌ Invalid verification code format (should be 6 digits)")
            continue
    
        print(f"\n   ⚡ Testing challenge resolution with code: {verification_code}")
        
        try:
            challenge_data = {
                "username": "luvmef",
                "challenge_code": verification_code
            }
            
            response = requests.post("http://localhost:8000/login-instagram-challenge", 
                                   json=challenge_data, 
                                   timeout=30)
            
            print(f"   📊 Response Status: {response.status_code}")
            
            if response.status_code == 200:
                result = response.json()
                if result.get("success"):
                    print("   🎉 SUCCESS! Challenge resolved!")
                    print(f"   👤 Username: {result.get('user_data', {}).get('username', 'N/A')}")
                    print(f"   👥 Followers: {result.get('user_data', {}).get('follower_count', 'N/A')}")
                    return True
                else:
                    print(f"   ❌ Challenge failed: {result.get('message', 'Unknown error')}")
            else:
                print(f"   ❌ Request failed with status {response.status_code}")
                try:
                    error_result = response.json()
                    print(f"   Error: {error_result.get('detail', response.text)}")
                except:
                    print(f"   Raw response: {response.text}")
            
        except Exception as e:
            print(f"   ❌ Request error: {e}")
        
        # Small delay between attempts
        time.sleep(2)
    
    print("\n3. 🔍 Post-resolution status check...")
    try:
        final_status = requests.get("http://localhost:8000/instagram/challenge-status/luvmef", timeout=10)
        if final_status.status_code == 200:
            final_data = final_status.json()
            print(f"   Challenge still exists: {final_data.get('has_challenge', False)}")
        else:
            print(f"   Status check failed: {final_status.status_code}")
    except Exception as e:
        print(f"   Status check error: {e}")

if __name__ == "__main__":
    test_challenge_resolution()
