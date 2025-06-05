#!/usr/bin/env python3

import requests
import json
import time

def test_challenge_resolution():
    """Test Instagram challenge resolution for mirzzassi"""
    try:
        print("🔄 Testing Instagram challenge resolution for mirzzassi...")
        
        # Step 1: Trigger challenge
        login_data = {
            "username": "mirzzassi", 
            "password": "Samasandik.123"  # Use correct password
        }
        
        response = requests.post(
            "http://localhost:8000/login-instagram",
            json=login_data,
            headers={"Content-Type": "application/json"}
        )
        
        print(f"Initial login status: {response.status_code}")
        result = response.json()
        
        if result.get("requires_challenge"):
            print("✅ Challenge required - this is expected!")
            print(f"Challenge type: {result.get('error_type')}")
            print(f"Message: {result.get('message')}")
            
            # The system should display a challenge code
            print("\n⚠️ Look for the challenge code display in the console above")
            print("📱 Check if Instagram app/website shows a verification prompt")
            
            return True
        elif result.get("success"):
            print("✅ Login successful without challenge!")
            if "user_data" in result:
                user_data = result["user_data"]
                print(f"   - Username: {user_data.get('username')}")
                print(f"   - Followers: {user_data.get('follower_count', 0)}")
                print(f"   - Following: {user_data.get('following_count', 0)}")
            return True
        else:
            print(f"❌ Login failed: {result}")
            return False
            
    except Exception as e:
        print(f"❌ Error: {e}")
        return False

def test_database_sync():
    """Test if the database sync is working"""
    try:
        print("\n🔄 Testing database sync with test user...")
        
        # Login with test user to verify sync
        login_data = {
            "username": "testuser",
            "password": "testpassword123"
        }
        
        response = requests.post(
            "http://localhost:8000/login-instagram",
            json=login_data,
            headers={"Content-Type": "application/json"}
        )
        
        if response.status_code == 200:
            result = response.json()
            print("✅ Test user login successful!")
            
            # Extract access token
            access_token = result.get("access_token")
            if access_token:
                print(f"✅ Access token received: {access_token[:20]}...")
                
                # Test profile endpoint to see if data is synced
                profile_response = requests.get(
                    "http://localhost:8000/profile",
                    headers={"Authorization": f"Bearer {access_token}"}
                )
                
                if profile_response.status_code == 200:
                    profile_data = profile_response.json()
                    print("✅ Profile data retrieved!")
                    
                    # Check Instagram stats
                    ig_stats = profile_data.get("instagram_stats")
                    if ig_stats:
                        print(f"📊 Instagram Stats:")
                        print(f"   - Followers: {ig_stats.get('followers_count', 0)}")
                        print(f"   - Following: {ig_stats.get('following_count', 0)}")
                        print(f"   - Posts: {ig_stats.get('media_count', 0)}")
                        
                        if ig_stats.get('followers_count', 0) > 0:
                            print("✅ Database sync is working correctly!")
                            return True
                        else:
                            print("⚠️ Instagram stats show 0 - potential sync issue")
                    else:
                        print("⚠️ No Instagram stats in profile")
                else:
                    print(f"❌ Profile request failed: {profile_response.status_code}")
            else:
                print("⚠️ No access token in response")
        else:
            print(f"❌ Test user login failed: {response.status_code}")
            
        return False
        
    except Exception as e:
        print(f"❌ Error testing database sync: {e}")
        return False

def main():
    print("=" * 60)
    print("INSTAGRAM AUTHENTICATION & DATABASE SYNC TEST")
    print("=" * 60)
    
    # Test 1: Database sync verification
    sync_works = test_database_sync()
    
    # Test 2: Challenge resolution for real account
    challenge_works = test_challenge_resolution()
    
    print("\n" + "=" * 60)
    print("TEST SUMMARY")
    print("=" * 60)
    print(f"Database sync works: {'✅' if sync_works else '❌'}")
    print(f"Challenge system works: {'✅' if challenge_works else '❌'}")
    
    if sync_works and challenge_works:
        print("\n🎉 Both database sync and challenge system are working!")
        print("💡 Next step: Complete Instagram challenge for mirzzassi to test real data sync")
    elif sync_works:
        print("\n✅ Database sync is working correctly")
        print("⚠️ Instagram authentication needs manual challenge completion")
    else:
        print("\n❌ Issues detected - check the logs above")

if __name__ == "__main__":
    main()
