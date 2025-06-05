#!/usr/bin/env python3
"""
Live test of Instagram bypass functionality using correct class names.
Tests the bypass system by directly importing and testing the components.
"""

import sys
import os
import asyncio
from pathlib import Path

# Add backend to Python path
backend_path = Path(__file__).parent / "backend"
sys.path.insert(0, str(backend_path))

from instagram_service import InstagramAPIService
from models import User, SessionLocal

class MockUser:
    """Mock user object for testing"""
    def __init__(self, username, instagram_pk=None):
        self.username = username
        self.instagram_pk = instagram_pk or "12345678901"

async def test_instagram_service_bypass():
    """Test Instagram service bypass functionality"""
    print("🧪 TESTING INSTAGRAM API SERVICE BYPASS")
    print("="*50)
    
    # Initialize Instagram service
    instagram_service = InstagramAPIService()
    
    test_results = []
    
    # Create mock test user
    test_user = MockUser("testuser", "12345678901")
    mock_db = None  # We won't use the database for these tests
    
    # Test 1: Profile data bypass
    print("\n👤 Testing profile data bypass...")
    try:
        result = await instagram_service.get_user_profile_data(test_user, mock_db)
        if result.get("success") and result.get("test_mode"):
            print("✅ Profile data bypass: SUCCESS")
            print(f"   Followers: {result.get('data', {}).get('follower_count')}")
            print(f"   Following: {result.get('data', {}).get('following_count')}")
            test_results.append(("Profile Data Bypass", True))
        else:
            print(f"❌ Profile data bypass: FAILED - {result}")
            test_results.append(("Profile Data Bypass", False))
    except Exception as e:
        print(f"❌ Profile data bypass: ERROR - {e}")
        test_results.append(("Profile Data Bypass", False))
    
    # Test 2: Like action bypass
    print("\n❤️ Testing like action bypass...")
    try:
        result = await instagram_service.validate_like_action(test_user, "https://www.instagram.com/p/test123/", mock_db)
        if result.get("success") and result.get("test_mode"):
            print("✅ Like action bypass: SUCCESS")
            print(f"   Media ID: {result.get('media_id')}")
            print(f"   Like count: {result.get('like_count')}")
            test_results.append(("Like Action Bypass", True))
        else:
            print(f"❌ Like action bypass: FAILED - {result}")
            test_results.append(("Like Action Bypass", False))
    except Exception as e:
        print(f"❌ Like action bypass: ERROR - {e}")
        test_results.append(("Like Action Bypass", False))
    
    # Test 3: Follow action bypass
    print("\n👥 Testing follow action bypass...")
    try:
        result = await instagram_service.validate_follow_action(test_user, "https://www.instagram.com/target_user_123/", mock_db)
        if result.get("success") and result.get("test_mode"):
            print("✅ Follow action bypass: SUCCESS")
            print(f"   Target: {result.get('target_username')}")
            print(f"   Target ID: {result.get('target_user_id')}")
            test_results.append(("Follow Action Bypass", True))
        else:
            print(f"❌ Follow action bypass: FAILED - {result}")
            test_results.append(("Follow Action Bypass", False))
    except Exception as e:
        print(f"❌ Follow action bypass: ERROR - {e}")
        test_results.append(("Follow Action Bypass", False))
    
    # Test 4: Profile info bypass
    print("\n📊 Testing profile info bypass...")
    try:
        result = await instagram_service.get_profile_info("testuser")
        if result.get("success") and result.get("test_mode"):
            print("✅ Profile info bypass: SUCCESS")
            print(f"   Username: {result.get('username')}")
            print(f"   Follower count: {result.get('follower_count')}")
            test_results.append(("Profile Info Bypass", True))
        else:
            print(f"❌ Profile info bypass: FAILED - {result}")
            test_results.append(("Profile Info Bypass", False))
    except Exception as e:
        print(f"❌ Profile info bypass: ERROR - {e}")
        test_results.append(("Profile Info Bypass", False))
    
    # Test 5: Normal user validation (should fail)
    print("\n🚫 Testing normal user validation (should fail)...")
    try:
        normal_user = MockUser("normal_user", "98765432109")
        result = await instagram_service.get_user_profile_data(normal_user, mock_db)
        if not result.get("success") or not result.get("test_mode"):
            print("✅ Normal user validation: SUCCESS (correctly rejected)")
            print(f"   Error: {result.get('error', 'API call failed as expected')}")
            test_results.append(("Normal User Validation", True))
        else:
            print(f"❌ Normal user validation: FAILED (should have been rejected) - {result}")
            test_results.append(("Normal User Validation", False))
    except Exception as e:
        print(f"✅ Normal user validation: SUCCESS (exception as expected) - {e}")
        test_results.append(("Normal User Validation", True))
    
    # Print results
    print("\n" + "="*60)
    print("🎯 INSTAGRAM API SERVICE BYPASS TEST RESULTS")
    print("="*60)
    
    passed = sum(1 for _, success in test_results if success)
    total = len(test_results)
    
    for test_name, success in test_results:
        status = "✅ PASS" if success else "❌ FAIL"
        print(f"{status} {test_name}")
    
    print("\n" + "-"*60)
    print(f"📊 SUMMARY: {passed}/{total} tests passed ({passed/total*100:.1f}%)")
    
    if passed == total:
        print("🎉 ALL TESTS PASSED! Instagram bypass system is working correctly.")
    else:
        print("⚠️  Some tests failed. Check the details above.")
    
    return passed == total

def test_database_test_user():
    """Test that test user exists in database"""
    print("\n🗄️ TESTING DATABASE TEST USER")
    print("="*40)
    
    try:
        db = SessionLocal()
        
        # Check if test user exists
        test_user = db.query(User).filter(User.username == "testuser").first()
        
        if test_user:
            print("✅ Test user found in database")
            print(f"   ID: {test_user.id}")
            print(f"   Username: {test_user.username}")
            print(f"   Instagram PK: {test_user.instagram_pk}")
            print(f"   Coins: {test_user.coins}")
            return True
        else:
            print("❌ Test user not found in database")
            return False
            
    except Exception as e:
        print(f"❌ Database error: {e}")
        return False
    finally:
        db.close()

async def main():
    """Main test function"""
    print("🧪 COMPREHENSIVE INSTAGRAM BYPASS TEST")
    print("="*50)
    
    # Test database test user
    db_success = test_database_test_user()
    
    # Test Instagram service bypass
    service_success = await test_instagram_service_bypass()
    
    # Final summary
    print("\n" + "="*60)
    print("🏁 FINAL SUMMARY")
    print("="*60)
    
    if db_success:
        print("✅ Database test user: READY")
    else:
        print("❌ Database test user: NOT READY")
    
    if service_success:
        print("✅ Instagram API service bypass: WORKING")
    else:
        print("❌ Instagram API service bypass: NOT WORKING")
    
    if db_success and service_success:
        print("\n🎉 COMPLETE BYPASS SYSTEM: FULLY OPERATIONAL!")
        print("   The test user can now perform Instagram actions without real credentials.")
        print("   Ready for integration testing with the full application.")
    else:
        print("\n⚠️  BYPASS SYSTEM: NEEDS ATTENTION")
        print("   Some components are not working correctly.")
    
    print("="*60)

if __name__ == "__main__":
    asyncio.run(main())
