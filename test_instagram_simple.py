#!/usr/bin/env python3
"""
Simple Instagram Authentication Test
"""
import requests
import json

BASE_URL = "http://localhost:8000"

def simple_instagram_test():
    print("📸 Simple Instagram Auth Test")
    print("="*40)
    
    # Test Instagram credentials
    instagram_data = {
        "username": "luvmef",
        "password": "asgsag2"
    }
    
    print("🔐 Testing Instagram login...")
    response = requests.post(f"{BASE_URL}/login-instagram", json=instagram_data)
    print(f"Status: {response.status_code}")
    print(f"Response: {response.text}")
    
    if "challenge" in response.text.lower():
        print("\n🔍 Challenge detected!")
        print("Check your email for verification code")

if __name__ == "__main__":
    simple_instagram_test()
