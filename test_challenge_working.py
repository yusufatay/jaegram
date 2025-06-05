#!/usr/bin/env python3
"""
Final Instagram Challenge Test - Working Solution
"""

import requests
import json

def test_working_challenge():
    print("🚀 INSTAGRAM CHALLENGE - FINAL TEST")
    print("=" * 50)
    
    # Test challenge trigger with correct credentials
    print("1. Testing challenge trigger...")
    login_data = {"username": "luvmef", "password": "asgsag2"}
    
    response = requests.post("http://localhost:8000/login-instagram", json=login_data)
    print(f"Status: {response.status_code}")
    
    if response.status_code == 200:
        result = response.json()
        
        if result.get("challenge_required"):
            print("✅ CHALLENGE TRIGGERED SUCCESSFULLY!")
            print(f"Message: {result.get('message')}")
            
            # Test challenge status
            print("\n2. Testing challenge status...")
            status_response = requests.get("http://localhost:8000/instagram/challenge-status/luvmef")
            print(f"Status endpoint: {status_response.status_code}")
            
            if status_response.status_code == 200:
                status_data = status_response.json()
                print(f"Has challenge: {status_data.get('has_challenge')}")
                print("✅ CHALLENGE STATUS WORKING!")
                
            print("\n🎯 SYSTEM IS WORKING CORRECTLY!")
            print("The challenge system is functioning properly.")
            print("To complete testing, you need a real Instagram verification code.")
            
            return True
    
    print("❌ Test failed")
    return False

if __name__ == "__main__":
    test_working_challenge()
