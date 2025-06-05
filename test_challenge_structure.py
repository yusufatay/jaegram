#!/usr/bin/env python3
"""
Simple challenge trigger test to examine response structure
"""

import requests
import json

def test_challenge_response():
    """Test and analyze challenge response structure"""
    
    print("🔍 Challenge Response Structure Test")
    print("=" * 50)
    
    # Test with known challenge account
    test_data = {
        "username": "luvmef",
        "password": "asgsag2"
    }
    
    try:
        print(f"📡 Sending login request for {test_data['username']}...")
        response = requests.post("http://localhost:8000/login-instagram", json=test_data)
        
        print(f"📊 Response Status: {response.status_code}")
        
        if response.status_code == 200:
            result = response.json()
            
            print(f"🎯 Challenge Required: {result.get('challenge_required', False)}")
            print(f"📝 Message: {result.get('message', 'N/A')}")
            
            if result.get("challenge_details"):
                challenge_data = result["challenge_details"]
                
                print(f"\n📦 Challenge Data Analysis:")
                print(f"   Top-level keys: {list(challenge_data.keys())}")
                
                # Check for different formats
                if "challenge" in challenge_data:
                    print(f"   🏛️ Legacy format detected")
                    challenge_obj = challenge_data["challenge"]
                    print(f"   Legacy challenge keys: {list(challenge_obj.keys())}")
                    
                    if "api_path" in challenge_obj:
                        print(f"   📍 API Path: {challenge_obj['api_path']}")
                    
                    if "challengeType" in challenge_obj:
                        print(f"   🔖 Challenge Type: {challenge_obj['challengeType']}")
                
                # Check for Bloks format
                bloks_keys = ["step_name", "step_data", "nonce_code", "challenge_context"]
                found_bloks = [key for key in bloks_keys if key in challenge_data]
                
                if found_bloks:
                    print(f"   🚀 Bloks format detected")
                    print(f"   Bloks keys found: {found_bloks}")
                    
                    if "step_name" in challenge_data:
                        print(f"   🎯 Step Name: {challenge_data['step_name']}")
                    
                    if "step_data" in challenge_data:
                        step_data = challenge_data["step_data"]
                        print(f"   📋 Step Data: {step_data}")
                        
                        if isinstance(step_data, dict):
                            if "contact_point" in step_data:
                                print(f"   📧 Contact Point: {step_data['contact_point']}")
                            if "form_type" in step_data:
                                print(f"   📝 Form Type: {step_data['form_type']}")
                
                print(f"\n📄 Full Challenge Data (formatted):")
                print(json.dumps(challenge_data, indent=2, default=str))
            
            else:
                print("❌ No challenge details in response")
                print(f"📄 Full Response: {json.dumps(result, indent=2)}")
                
        else:
            print(f"❌ Request failed with status {response.status_code}")
            try:
                error_result = response.json()
                print(f"Error: {json.dumps(error_result, indent=2)}")
            except:
                print(f"Raw response: {response.text}")
                
    except Exception as e:
        print(f"❌ Test failed: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_challenge_response()
