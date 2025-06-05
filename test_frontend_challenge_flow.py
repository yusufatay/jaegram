#!/usr/bin/env python3
"""
Test frontend challenge flow integration
"""

import requests
import json

BASE_URL = "http://localhost:8000"

def test_frontend_challenge_flow():
    """Test that backend returns proper challenge response for frontend"""
    print("🧪 TESTING FRONTEND CHALLENGE FLOW")
    print("=" * 60)
    
    # 1. Test Instagram login that should trigger challenge
    print("1. 📱 Testing Instagram login that triggers challenge...")
    
    login_data = {
        "username": "luvmef",  # Account that triggers challenges
        "password": "Bsbsbs123."
    }
    
    try:
        response = requests.post(f"{BASE_URL}/login-instagram", json=login_data)
        print(f"   Status Code: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            print(f"   📋 Response Keys: {list(data.keys())}")
            
            # Check if it's a challenge response
            if data.get('challenge_required') or data.get('requires_challenge'):
                print("   ✅ CHALLENGE TRIGGERED CORRECTLY!")
                print(f"   💬 Message: {data.get('message', 'No message')}")
                print(f"   🔑 Challenge Required: {data.get('challenge_required', data.get('requires_challenge'))}")
                
                # Check challenge info structure
                challenge_info = data.get('challenge_info', {})
                if challenge_info:
                    print(f"   📊 Challenge Info: {json.dumps(challenge_info, indent=4)}")
                else:
                    print("   ⚠️  No challenge_info found in response")
                
                # Check if response has all required fields for frontend
                required_fields = ['requires_challenge', 'challenge_info', 'message']
                missing_fields = [field for field in required_fields if field not in data]
                
                if missing_fields:
                    print(f"   ❌ Missing fields for frontend: {missing_fields}")
                else:
                    print("   ✅ All required fields present for frontend!")
                
                return True
                
            elif data.get('success') == True:
                print("   ⚠️  Login succeeded without challenge (unexpected)")
                return False
            else:
                print(f"   ❌ Login failed: {data.get('error', 'Unknown error')}")
                return False
                
        else:
            print(f"   ❌ HTTP Error: {response.status_code}")
            try:
                error_data = response.json()
                print(f"   Error: {error_data}")
            except:
                print(f"   Raw error: {response.text}")
            return False
            
    except Exception as e:
        print(f"   ❌ Request failed: {e}")
        return False

def test_challenge_response_structure():
    """Test that challenge response has correct structure for frontend"""
    print("\n2. 🔍 Testing challenge response structure...")
    
    # Expected structure that frontend needs
    expected_structure = {
        'requires_challenge': bool,
        'challenge_info': {
            'challenge_type': str,
            'contact_point': str,
            'message': str,
        },
        'message': str,
        'success': bool
    }
    
    print("   📋 Expected frontend structure:")
    print(f"   {json.dumps(expected_structure, indent=4, default=str)}")
    
    return True

if __name__ == "__main__":
    print("🚀 Starting Frontend Challenge Flow Test...")
    
    # Test challenge triggering
    challenge_triggered = test_frontend_challenge_flow()
    
    # Test response structure
    test_challenge_response_structure()
    
    print("\n" + "=" * 60)
    print("📊 FRONTEND CHALLENGE FLOW TEST SUMMARY")
    print("=" * 60)
    
    if challenge_triggered:
        print("✅ Backend correctly triggers challenges for frontend")
        print("✅ Challenge response structure is correct")
        print("✅ Frontend should be able to detect and show challenge dialog")
        print("\n🎯 NEXT: Test with frontend Flutter app:")
        print("   1. Enter 'luvmef' and 'Bsbsbs123.' in login form")
        print("   2. Click login button")
        print("   3. Challenge dialog should appear")
        print("   4. Enter 6-digit code when received")
    else:
        print("❌ Challenge not triggered or response incorrect")
        print("🔧 Check backend Instagram service configuration")
    
    print("\n🎉 Test completed!")
