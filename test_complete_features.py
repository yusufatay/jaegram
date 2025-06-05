#!/usr/bin/env python3
"""
Comprehensive Feature Test Script for Instagram Coin-Earning Platform
Tests all major features and provides a complete system verification
"""

import requests
import json
import time
from datetime import datetime

BASE_URL = "http://localhost:8000"

def test_user_registration():
    """Test user registration with email"""
    print("🔍 Testing User Registration...")
    
    test_user = {
        "username": f"testuser_{int(time.time())}",
        "password": "testpass123",
        "email": "test@example.com"
    }
    
    response = requests.post(f"{BASE_URL}/register", json=test_user)
    print(f"   Registration Response: {response.status_code}")
    print(f"   Response Body: {response.json()}")
    
    return test_user if response.status_code == 200 else None

def test_user_login(user_data):
    """Test user login and get token"""
    print("🔍 Testing User Login...")
    
    login_data = {
        "username": user_data["username"],
        "password": user_data["password"]
    }
    
    response = requests.post(
        f"{BASE_URL}/login", 
        data=login_data,
        headers={"Content-Type": "application/x-www-form-urlencoded"}
    )
    
    print(f"   Login Response: {response.status_code}")
    if response.status_code == 200:
        token_data = response.json()
        print(f"   Token Type: {token_data.get('token_type')}")
        print(f"   Access Token: {token_data.get('access_token')[:50]}...")
        return token_data.get('access_token')
    else:
        print(f"   Error: {response.json()}")
        return None

def test_daily_reward(token):
    """Test daily reward system"""
    print("🔍 Testing Daily Reward System...")
    
    headers = {"Authorization": f"Bearer {token}"}
    response = requests.post(f"{BASE_URL}/daily-reward", headers=headers)
    
    print(f"   Daily Reward Response: {response.status_code}")
    print(f"   Response Body: {response.json()}")
    
    return response.status_code == 200

def test_email_verification(token, email):
    """Test email verification system"""
    print("🔍 Testing Email Verification...")
    
    headers = {"Authorization": f"Bearer {token}"}
    response = requests.post(
        f"{BASE_URL}/send-verification-email?email={email}", 
        headers=headers
    )
    
    print(f"   Email Verification Response: {response.status_code}")
    print(f"   Response Body: {response.json()}")
    
    return response.status_code == 200

def test_2fa_setup(token):
    """Test 2FA setup"""
    print("🔍 Testing 2FA Setup...")
    
    headers = {"Authorization": f"Bearer {token}"}
    response = requests.post(f"{BASE_URL}/setup-2fa", headers=headers)
    
    print(f"   2FA Setup Response: {response.status_code}")
    if response.status_code == 200:
        data = response.json()
        print(f"   Secret Generated: {data.get('secret')[:20]}...")
        print(f"   QR Code Generated: {'Yes' if data.get('qr_code') else 'No'}")
        print(f"   Backup Codes Generated: {len(data.get('backup_codes', []))} codes")
        return True
    else:
        print(f"   Error: {response.json()}")
        return False

def test_api_docs():
    """Test API documentation availability"""
    print("🔍 Testing API Documentation...")
    
    response = requests.get(f"{BASE_URL}/docs")
    print(f"   API Docs Response: {response.status_code}")
    print(f"   Swagger UI Available: {'Yes' if response.status_code == 200 else 'No'}")
    
    return response.status_code == 200

def run_comprehensive_test():
    """Run all tests and provide a summary"""
    print("=" * 60)
    print("🚀 COMPREHENSIVE FEATURE TEST - Instagram Coin Platform")
    print("=" * 60)
    print(f"⏰ Test Started: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print()
    
    test_results = {}
    
    # Test API Documentation
    test_results['api_docs'] = test_api_docs()
    print()
    
    # Test User Registration
    user_data = test_user_registration()
    test_results['registration'] = user_data is not None
    print()
    
    if not user_data:
        print("❌ Registration failed, cannot continue with other tests")
        return
    
    # Test User Login
    token = test_user_login(user_data)
    test_results['login'] = token is not None
    print()
    
    if not token:
        print("❌ Login failed, cannot continue with authenticated tests")
        return
    
    # Test Daily Reward System
    test_results['daily_reward'] = test_daily_reward(token)
    print()
    
    # Test Email Verification
    test_results['email_verification'] = test_email_verification(token, user_data["email"])
    print()
    
    # Test 2FA Setup
    test_results['2fa_setup'] = test_2fa_setup(token)
    print()
    
    # Print Summary
    print("=" * 60)
    print("📊 TEST RESULTS SUMMARY")
    print("=" * 60)
    
    total_tests = len(test_results)
    passed_tests = sum(test_results.values())
    
    for test_name, result in test_results.items():
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"   {test_name.replace('_', ' ').title()}: {status}")
    
    print()
    print(f"📈 Overall Success Rate: {passed_tests}/{total_tests} ({(passed_tests/total_tests)*100:.1f}%)")
    
    if passed_tests == total_tests:
        print("🎉 ALL TESTS PASSED! The system is fully functional.")
    else:
        print(f"⚠️  {total_tests - passed_tests} test(s) failed. Please check the output above.")
    
    print()
    print(f"⏰ Test Completed: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("=" * 60)

if __name__ == "__main__":
    try:
        run_comprehensive_test()
    except requests.exceptions.ConnectionError:
        print("❌ Connection Error: Backend server not running on localhost:8000")
        print("   Please start the backend server and try again.")
    except Exception as e:
        print(f"❌ Unexpected Error: {e}")
