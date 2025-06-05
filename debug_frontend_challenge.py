#!/usr/bin/env python3
"""
Debug script to test what the frontend receives when a challenge is triggered
"""
import requests
import json

BASE_URL = "http://127.0.0.1:8000"

def test_instagram_challenge_response():
    """Test what response the frontend gets when challenge is triggered"""
    print("🔍 Testing Instagram Challenge Response")
    print("=" * 50)
    
    # Test with the account that triggers challenge
    instagram_login_data = {
        "username": "williamjohnson12935",
        "password": "gdzfhrdhzdffd"
    }
    
    try:
        response = requests.post(f"{BASE_URL}/login-instagram", json=instagram_login_data)
        print(f"📊 Response Status Code: {response.status_code}")
        print(f"📊 Response Headers: {dict(response.headers)}")
        
        try:
            response_data = response.json()
            print(f"📊 Response Data:")
            print(json.dumps(response_data, indent=2, ensure_ascii=False))
            
            # Check specific fields the frontend looks for
            print(f"\n🔍 Frontend Check Results:")
            print(f"   success: {response_data.get('success')}")
            print(f"   challenge_required: {response_data.get('challenge_required')}")
            print(f"   requires_challenge: {response_data.get('requires_challenge')}")
            print(f"   message: {response_data.get('message')}")
            print(f"   challenge_info: {response_data.get('challenge_info')}")
            print(f"   challenge_details: {response_data.get('challenge_details')}")
            
        except json.JSONDecodeError:
            print(f"❌ Response is not JSON: {response.text}")
            
    except Exception as e:
        print(f"❌ Error: {e}")

if __name__ == "__main__":
    test_instagram_challenge_response()
