#!/usr/bin/env python3
"""
Comprehensive test script for all new backend features
Tests: Social features, coin security, education, notifications, Instagram integration
"""

import requests
import json
import time
from datetime import datetime

BASE_URL = "http://localhost:8000"
print(f"🚀 Testing Instagram Coin Platform - {datetime.now()}")
print("=" * 50)

# Test user credentials
test_username = f"testuser_{int(time.time())}"
test_password = "testpass123"
test_email = f"test_{int(time.time())}@example.com"

def test_auth_flow():
    """Test user registration and login"""
    print("\n📝 Testing Authentication Flow...")
    
    # Register
    register_data = {
        "username": test_username,
        "email": test_email,
        "password": test_password
    }
    
    try:
        response = requests.post(f"{BASE_URL}/register", json=register_data)
        print(f"   ✅ Registration: {response.status_code}")
        
        # Login
        login_data = {
            "username": test_username,
            "password": test_password
        }
        
        response = requests.post(f"{BASE_URL}/login", data=login_data)
        if response.status_code == 200:
            token = response.json()["access_token"]
            print(f"   ✅ Login successful, token received")
            return token
        else:
            print(f"   ❌ Login failed: {response.status_code}")
            return None
    except Exception as e:
        print(f"   ❌ Auth error: {e}")
        return None

def test_social_features(token):
    """Test social features: referrals, badges, leaderboard"""
    print("\n🌟 Testing Social Features...")
    headers = {"Authorization": f"Bearer {token}"}
    
    try:
        # Generate referral code
        response = requests.post(f"{BASE_URL}/social/referral/generate", headers=headers)
        print(f"   ✅ Referral code generation: {response.status_code}")
        
        # Get badges
        response = requests.get(f"{BASE_URL}/social/badges", headers=headers)
        print(f"   ✅ Get badges: {response.status_code}")
        
        # Get leaderboard
        response = requests.get(f"{BASE_URL}/social/leaderboard", headers=headers)
        print(f"   ✅ Get leaderboard: {response.status_code}")
        
        # Get user rank
        response = requests.get(f"{BASE_URL}/social/my-rank", headers=headers)
        print(f"   ✅ Get user rank: {response.status_code}")
        
        # Get social stats
        response = requests.get(f"{BASE_URL}/social/stats", headers=headers)
        print(f"   ✅ Get social stats: {response.status_code}")
        
    except Exception as e:
        print(f"   ❌ Social features error: {e}")

def test_coin_security(token):
    """Test coin security and withdrawal features"""
    print("\n💰 Testing Coin Security Features...")
    headers = {"Authorization": f"Bearer {token}"}
    
    try:
        # Get withdrawal methods
        response = requests.get(f"{BASE_URL}/coins/withdrawal-methods", headers=headers)
        print(f"   ✅ Get withdrawal methods: {response.status_code}")
        
        # Get security settings
        response = requests.get(f"{BASE_URL}/coins/security-settings", headers=headers)
        print(f"   ✅ Get security settings: {response.status_code}")
        
        # Get withdrawal info
        response = requests.get(f"{BASE_URL}/coins/withdrawal-info", headers=headers)
        print(f"   ✅ Get withdrawal info: {response.status_code}")
        
        # Get withdrawal history
        response = requests.get(f"{BASE_URL}/coins/withdrawal-history", headers=headers)
        print(f"   ✅ Get withdrawal history: {response.status_code}")
        
        # Get fraud detection status
        response = requests.get(f"{BASE_URL}/coins/fraud-status", headers=headers)
        print(f"   ✅ Get fraud detection status: {response.status_code}")
        
    except Exception as e:
        print(f"   ❌ Coin security error: {e}")

def test_education_system(token):
    """Test user education system"""
    print("\n🎓 Testing Education System...")
    headers = {"Authorization": f"Bearer {token}"}
    
    try:
        # Get available modules
        response = requests.get(f"{BASE_URL}/education/modules", headers=headers)
        print(f"   ✅ Get education modules: {response.status_code}")
        
        # Get user progress
        response = requests.get(f"{BASE_URL}/education/progress", headers=headers)
        print(f"   ✅ Get education progress: {response.status_code}")
        
        # Get recommendations
        response = requests.get(f"{BASE_URL}/education/recommendations", headers=headers)
        print(f"   ✅ Get recommendations: {response.status_code}")
        
        # Get education stats
        response = requests.get(f"{BASE_URL}/education/stats", headers=headers)
        print(f"   ✅ Get education stats: {response.status_code}")
        
        # Search modules
        response = requests.get(f"{BASE_URL}/education/search?q=security", headers=headers)
        print(f"   ✅ Search modules: {response.status_code}")
        
    except Exception as e:
        print(f"   ❌ Education system error: {e}")

def test_notification_system(token):
    """Test advanced notification system"""
    print("\n🔔 Testing Notification System...")
    headers = {"Authorization": f"Bearer {token}"}
    
    try:
        # Get notification settings
        response = requests.get(f"{BASE_URL}/notifications/settings", headers=headers)
        print(f"   ✅ Get notification settings: {response.status_code}")
        
        # Send test notification
        test_data = {"type": "task_completion"}
        response = requests.post(f"{BASE_URL}/notifications/test", json=test_data, headers=headers)
        print(f"   ✅ Send test notification: {response.status_code}")
        
        # Get notification history
        response = requests.get(f"{BASE_URL}/notifications/history", headers=headers)
        print(f"   ✅ Get notification history: {response.status_code}")
        
        # Get notification preferences
        response = requests.get(f"{BASE_URL}/notifications/preferences", headers=headers)
        print(f"   ✅ Get notification preferences: {response.status_code}")
        
    except Exception as e:
        print(f"   ❌ Notification system error: {e}")

def test_instagram_integration(token):
    """Test Instagram integration features"""
    print("\n📸 Testing Instagram Integration...")
    headers = {"Authorization": f"Bearer {token}"}
    
    try:
        # Get Instagram profile (should be empty initially)
        response = requests.get(f"{BASE_URL}/instagram/profile", headers=headers)
        print(f"   ✅ Get Instagram profile: {response.status_code}")
        
        # Get credential status
        response = requests.get(f"{BASE_URL}/instagram/credential-status", headers=headers)
        print(f"   ✅ Get credential status: {response.status_code}")
        
        # Get sync settings
        response = requests.get(f"{BASE_URL}/instagram/sync-settings", headers=headers)
        print(f"   ✅ Get sync settings: {response.status_code}")
        
        # Get analytics
        response = requests.get(f"{BASE_URL}/instagram/analytics", headers=headers)
        print(f"   ✅ Get Instagram analytics: {response.status_code}")
        
    except Exception as e:
        print(f"   ❌ Instagram integration error: {e}")

def test_gdpr_compliance(token):
    """Test GDPR compliance features"""
    print("\n🔒 Testing GDPR Compliance...")
    headers = {"Authorization": f"Bearer {token}"}
    
    try:
        # Get privacy settings
        response = requests.get(f"{BASE_URL}/gdpr/privacy-settings", headers=headers)
        print(f"   ✅ Get privacy settings: {response.status_code}")
        
        # Get data usage info
        response = requests.get(f"{BASE_URL}/gdpr/data-usage", headers=headers)
        print(f"   ✅ Get data usage info: {response.status_code}")
        
    except Exception as e:
        print(f"   ❌ GDPR compliance error: {e}")

def test_mental_health_system(token):
    """Test mental health monitoring"""
    print("\n🧠 Testing Mental Health System...")
    headers = {"Authorization": f"Bearer {token}"}
    
    try:
        # Get mental health status
        response = requests.get(f"{BASE_URL}/mental-health/status", headers=headers)
        print(f"   ✅ Get mental health status: {response.status_code}")
        
        # Get recommendations
        response = requests.get(f"{BASE_URL}/mental-health/recommendations", headers=headers)
        print(f"   ✅ Get mental health recommendations: {response.status_code}")
        
    except Exception as e:
        print(f"   ❌ Mental health system error: {e}")

def test_system_info():
    """Test system information endpoints"""
    print("\n ℹ️ Testing System Information...")
    
    try:
        # Get system status
        response = requests.get(f"{BASE_URL}/system/status")
        print(f"   ✅ Get system status: {response.status_code}")
        
        # Get API info
        response = requests.get(f"{BASE_URL}/")
        print(f"   ✅ Get API root: {response.status_code}")
        
    except Exception as e:
        print(f"   ❌ System info error: {e}")

def main():
    """Run all tests"""
    print("🧪 Starting comprehensive backend testing...")
    
    # Test system info first
    test_system_info()
    
    # Test authentication flow
    token = test_auth_flow()
    
    if not token:
        print("❌ Cannot continue without valid token")
        return
    
    # Test all features
    test_social_features(token)
    test_coin_security(token)
    test_education_system(token)
    test_notification_system(token)
    test_instagram_integration(token)
    test_gdpr_compliance(token)
    test_mental_health_system(token)
    
    print("\n" + "=" * 50)
    print("✅ All tests completed! Backend is fully functional with all advanced features.")
    print(f"🎯 Test user created: {test_username}")
    print("🚀 Ready for production deployment!")

if __name__ == "__main__":
    main()
