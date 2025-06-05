#!/usr/bin/env python3
"""
Test script for the enhanced badge system integration
"""
import asyncio
import requests
import json
from datetime import datetime

# Base URL for the API
BASE_URL = "http://localhost:8000"

def test_badge_endpoints():
    """Test the new badge endpoints"""
    print("🔍 Testing Badge System Integration...")
    
    # Test 1: Get all badge categories
    print("\n1. Testing /badges/categories endpoint...")
    try:
        response = requests.get(f"{BASE_URL}/badges/categories")
        if response.status_code == 200:
            data = response.json()
            print(f"✅ Categories retrieved: {len(data.get('categories', []))} categories")
            for category in data.get('categories', []):
                print(f"   - {category['name']}: {category['description']}")
        else:
            print(f"❌ Failed: {response.status_code} - {response.text}")
    except Exception as e:
        print(f"❌ Error: {e}")
    
    # Test 2: Check if badge initialization endpoint exists
    print("\n2. Testing badge endpoints availability...")
    endpoints_to_test = [
        "/badges/categories",
        "/badges/leaderboard"
    ]
    
    for endpoint in endpoints_to_test:
        try:
            response = requests.get(f"{BASE_URL}{endpoint}")
            if response.status_code in [200, 401, 403]:  # 401/403 is ok for auth-protected endpoints
                print(f"✅ {endpoint} - Available")
            else:
                print(f"❌ {endpoint} - Status: {response.status_code}")
        except Exception as e:
            print(f"❌ {endpoint} - Error: {e}")

def test_badge_system_features():
    """Test badge system features that don't require authentication"""
    print("\n🏆 Testing Badge System Features...")
    
    # Test badge categories
    print("\n3. Testing badge categories...")
    try:
        response = requests.get(f"{BASE_URL}/badges/categories")
        if response.status_code == 200:
            data = response.json()
            categories = data.get('categories', [])
            
            if categories:
                print(f"✅ Found {len(categories)} badge categories:")
                for cat in categories:
                    print(f"   📂 {cat['name']}: {cat['description']}")
                    print(f"      Color: {cat['color']}, Icon: {cat['icon']}")
            else:
                print("⚠️  No categories found - system may need initialization")
        else:
            print(f"❌ Categories endpoint failed: {response.status_code}")
    except Exception as e:
        print(f"❌ Categories test error: {e}")
    
    # Test leaderboard (should work without auth but might be empty)
    print("\n4. Testing badge leaderboard...")
    try:
        response = requests.get(f"{BASE_URL}/badges/leaderboard")
        if response.status_code == 200:
            data = response.json()
            users = data.get('users', [])
            print(f"✅ Leaderboard retrieved: {len(users)} users")
            if users:
                for i, user in enumerate(users[:3], 1):
                    print(f"   {i}. {user.get('username', 'Unknown')} - {user.get('total_badges', 0)} badges")
            else:
                print("   📊 Leaderboard is empty (no users with badges yet)")
        else:
            print(f"❌ Leaderboard failed: {response.status_code}")
    except Exception as e:
        print(f"❌ Leaderboard test error: {e}")

def show_integration_summary():
    """Show a summary of the integration"""
    print("\n" + "="*60)
    print("🎖️  BADGE SYSTEM INTEGRATION SUMMARY")
    print("="*60)
    
    integration_features = [
        "✅ Enhanced badge system imported and initialized",
        "✅ Badge checking integrated with task completion",
        "✅ Badge checking integrated with daily rewards",
        "✅ New badge management endpoints added:",
        "   • /badges/initialize - Initialize badge system",
        "   • /badges/check/{user_id} - Check and award badges",
        "   • /badges/award-special - Award special badges",
        "   • /badges/progress - Get user badge progress",
        "   • /badges/leaderboard - Badge leaderboard",
        "   • /badges/categories - Get badge categories",
        "✅ Background badge checking (non-blocking)",
        "✅ Error handling and logging implemented",
        "✅ Integration with existing notification system"
    ]
    
    for feature in integration_features:
        print(feature)
    
    print("\n📋 NEXT STEPS:")
    next_steps = [
        "1. Start the backend server: python app.py",
        "2. Initialize badges: POST /badges/initialize (admin only)",
        "3. Test task completion badge awarding",
        "4. Test daily reward badge awarding", 
        "5. Verify badge progress tracking",
        "6. Test frontend badge display integration"
    ]
    
    for step in next_steps:
        print(step)

def main():
    """Main test function"""
    print("🚀 Badge System Integration Test")
    print("="*40)
    
    # Test if server is running
    try:
        response = requests.get(f"{BASE_URL}/health", timeout=5)
        print("✅ Server is running")
    except Exception as e:
        print(f"❌ Server not reachable: {e}")
        print("💡 Please start the server with: python app.py")
        return
    
    # Run tests
    test_badge_endpoints()
    test_badge_system_features()
    show_integration_summary()
    
    print(f"\n🎯 Test completed at {datetime.now()}")

if __name__ == "__main__":
    main()
