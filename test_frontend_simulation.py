#!/usr/bin/env python3
"""
Test script to simulate what the frontend Flutter app does when receiving a challenge
"""
import requests
import json

BASE_URL = "http://127.0.0.1:8000"

def test_frontend_challenge_simulation():
    """Simulate the frontend Instagram service processing challenge response"""
    print("🎯 Simulating Frontend Challenge Processing")
    print("=" * 50)
    
    # Make the same request the frontend would make
    instagram_login_data = {
        "username": "williamjohnson12935",
        "password": "gdzfhrdhzdffd"
    }
    
    try:
        response = requests.post(f"{BASE_URL}/login-instagram", json=instagram_login_data)
        response_data = response.json()
        
        print(f"📊 Raw Backend Response:")
        print(f"   success: {response_data.get('success')}")
        print(f"   challenge_required: {response_data.get('challenge_required')}")
        
        # Simulate frontend service processing (the logic we just fixed)
        if response.status_code == 200:
            if response_data.get('challenge_required') == True or response_data.get('requires_challenge') == True:
                # Extract contact point from challenge details
                challenge_details = response_data.get('challenge_details', {})
                step_data = challenge_details.get('step_data', {})
                contact_point = step_data.get('contact_point', response_data.get('contact_point', ''))
                form_type = step_data.get('form_type', 'email')
                
                processed_response = {
                    'success': False,
                    'requires_challenge': True,
                    'challenge_info': {
                        'challenge_url': response_data.get('challenge_url'),
                        'challenge_details': challenge_details,
                        'username': response_data.get('username', 'williamjohnson12935'),
                        'message': response_data.get('message'),
                        'challenge_type': form_type,
                        'contact_point': contact_point,
                        'step_name': challenge_details.get('step_name', 'verify_email'),
                        'nonce_code': challenge_details.get('nonce_code', ''),
                        'challenge_context': challenge_details.get('challenge_context', ''),
                    },
                    'error': response_data.get('message', 'Challenge required'),
                }
                
                print(f"\n✅ Frontend Processed Response:")
                print(f"   success: {processed_response.get('success')}")
                print(f"   requires_challenge: {processed_response.get('requires_challenge')}")
                print(f"   challenge_type: {processed_response['challenge_info']['challenge_type']}")
                print(f"   contact_point: {processed_response['challenge_info']['contact_point']}")
                print(f"   message: {processed_response['challenge_info']['message']}")
                
                # Check if login screen would trigger challenge dialog
                if processed_response.get('requires_challenge') == True:
                    print(f"\n🎉 SUCCESS! Login screen would now show challenge dialog!")
                    print(f"   Dialog message: {processed_response['challenge_info']['message']}")
                    print(f"   Contact point: {processed_response['challenge_info']['contact_point']}")
                else:
                    print(f"\n❌ Challenge dialog would NOT be triggered")
            else:
                print(f"\n❌ No challenge detected in response")
        else:
            print(f"\n❌ HTTP error: {response.status_code}")
            
    except Exception as e:
        print(f"❌ Error: {e}")

if __name__ == "__main__":
    test_frontend_challenge_simulation()
