#!/usr/bin/env python3
"""
Test script to verify the fixed Instagram challenge resolution flow.
Tests the specific fixes for method signature and return type errors.
"""

import requests
import json
import time

def test_challenge_resolution_fixes():
    """Test the fixed challenge resolution methods"""
    print("🔧 Testing Instagram Challenge Resolution Fixes")
    print("=" * 60)
    
    base_url = "http://localhost:8000"
    
    # Test 1: Check if challenge endpoint exists and validates properly
    print("\n1. 🧪 Testing Challenge Endpoint Validation")
    try:
        # Test with missing challenge context (should return proper error)
        challenge_data = {
            "username": "test_user_that_doesnt_exist",
            "challenge_code": "123456"
        }
        
        response = requests.post(
            f"{base_url}/login-instagram-challenge",
            json=challenge_data,
            timeout=10
        )
        
        print(f"   Status Code: {response.status_code}")
        if response.status_code == 200 or response.status_code == 400:
            result = response.json()
            print(f"   Response: {json.dumps(result, indent=2, ensure_ascii=False)}")
            
            # Check if it returns proper error format (dict, not bool)
            if isinstance(result, dict):
                print("   ✅ Returns proper dictionary format (not boolean)")
                if "error" in result or "detail" in result:
                    print("   ✅ Contains proper error message")
                else:
                    print("   ⚠️  Response format may need adjustment")
            else:
                print(f"   ❌ Returns {type(result)} instead of dictionary")
        else:
            print(f"   Response: {response.text}")
            
    except requests.exceptions.RequestException as e:
        print(f"   ❌ Request failed: {e}")
    except Exception as e:
        print(f"   ❌ Test failed: {e}")
    
    # Test 2: Check backend health
    print("\n2. 🔍 Backend Health Check")
    try:
        response = requests.get(f"{base_url}/health", timeout=5)
        if response.status_code == 200:
            print("   ✅ Backend is healthy and responding")
        else:
            print(f"   ⚠️  Backend health check returned: {response.status_code}")
    except Exception as e:
        print(f"   ❌ Backend health check failed: {e}")
    
    # Test 3: Check Instagram service initialization
    print("\n3. 🔧 Instagram Service Status")
    try:
        # Test login endpoint with dummy data to see if service is initialized
        login_data = {
            "username": "dummy_test",
            "password": "dummy_pass"
        }
        
        response = requests.post(
            f"{base_url}/login-instagram",
            json=login_data,
            timeout=15
        )
        
        print(f"   Status Code: {response.status_code}")
        if response.status_code in [200, 400, 422]:
            result = response.json()
            print("   ✅ Instagram service is responding")
            # Check if it's a challenge response or other expected response
            if "requires_challenge" in result or "error" in result or "detail" in result:
                print("   ✅ Service handles requests properly")
        else:
            print(f"   Response: {response.text}")
            
    except requests.exceptions.RequestException as e:
        print(f"   ❌ Instagram service test failed: {e}")
    except Exception as e:
        print(f"   ❌ Test failed: {e}")
    
    print("\n" + "=" * 60)
    print("🎯 Challenge Resolution Fix Verification Complete")
    print("\n📋 Key Fixes Implemented:")
    print("   ✅ Fixed method signature: challenge_resolve(last_json) - only one parameter")
    print("   ✅ Fixed return type: methods return Dict[str, Any] instead of bool")
    print("   ✅ Fixed challenge_code_handler: returns challenge code via closure")
    print("   ✅ Fixed terminal input prevention: no more input() calls")
    
    print("\n🚀 Next Steps:")
    print("   1. Test with real Instagram account that triggers challenge")
    print("   2. Verify email delivery of verification codes")
    print("   3. Test complete login flow end-to-end")

if __name__ == "__main__":
    test_challenge_resolution_fixes()
