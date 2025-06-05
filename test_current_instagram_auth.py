#!/usr/bin/env python3

import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), 'backend'))

import asyncio
import json
import logging
from instagrapi import Client
from instagrapi.exceptions import LoginRequired, ChallengeRequired, ClientError

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

async def test_current_session():
    """Test the current Instagram session"""
    try:
        print("🔄 Testing current Instagram session...")
        
        # Load existing session
        session_file = "session_mirzzassi.json"
        if not os.path.exists(session_file):
            print("❌ Session file not found")
            return
        
        client = Client()
        client.load_settings(session_file)
        
        print(f"✅ Session loaded from {session_file}")
        
        # Test session validity
        try:
            account_info = client.account_info()
            print(f"✅ Session is valid!")
            print(f"   - User ID: {account_info.pk}")
            print(f"   - Username: {account_info.username}")
            print(f"   - Full Name: {account_info.full_name}")
            
            # Test user_info call with fixed PK conversion
            print("\n🔄 Testing user_info call with PK conversion fix...")
            user_info = client.user_info(int(account_info.pk))  # Convert to int
            print(f"✅ user_info call successful!")
            print(f"   - Followers: {user_info.follower_count}")
            print(f"   - Following: {user_info.following_count}")
            print(f"   - Posts: {user_info.media_count}")
            
            return True
            
        except LoginRequired as e:
            print(f"❌ Session expired - LoginRequired: {e}")
            return False
        except ChallengeRequired as e:
            print(f"⚠️ Challenge required: {e}")
            return False
        except ClientError as e:
            print(f"❌ Client error: {e}")
            return False
        except Exception as e:
            print(f"❌ Unexpected error: {e}")
            return False
            
    except Exception as e:
        print(f"❌ Error loading session: {e}")
        return False

async def test_fresh_login():
    """Test fresh Instagram login"""
    try:
        print("\n🔄 Testing fresh Instagram login...")
        
        client = Client()
        
        # Set enhanced settings
        client.set_settings({
            "user_agent": "Instagram 295.0.0.32.119 Android (33/13; 420dpi; 1080x2340; samsung; SM-G973F; beyond1lte; qcom; en_US; 474393099)",
            "device_settings": {
                "cpu": "h1",
                "dpi": "420dpi", 
                "model": "SM-G973F",
                "device": "beyond1lte",
                "resolution": "1080x2340",
                "app_version": "295.0.0.32.119",
                "android_version": 33,
                "android_release": "13.0",
                "manufacturer": "samsung"
            },
            "country": "US",
            "country_code": 1,
            "locale": "en_US",
            "timezone_offset": -25200
        })
        
        # Test credentials (replace with actual test credentials)
        username = "mirzzassi"
        password = "password123"  # This would need to be the actual password
        
        print(f"Attempting login for {username}...")
        
        try:
            client.login(username, password)
            print("✅ Fresh login successful!")
            
            account_info = client.account_info()
            print(f"   - User ID: {account_info.pk}")
            print(f"   - Username: {account_info.username}")
            
            # Save new session
            client.dump_settings("session_mirzzassi_fresh.json")
            print("✅ New session saved")
            
            return True
            
        except LoginRequired as e:
            print(f"❌ Login required: {e}")
            return False
        except ChallengeRequired as e:
            print(f"⚠️ Challenge required: {e}")
            return False
        except ClientError as e:
            print(f"❌ Client error: {e}")
            return False
            
    except Exception as e:
        print(f"❌ Error during fresh login: {e}")
        return False

async def test_instagram_service():
    """Test the Instagram service directly"""
    try:
        print("\n🔄 Testing Instagram service...")
        
        # Import our Instagram service
        from instagram_service import InstagramAPIService
        
        service = InstagramAPIService()
        
        # Test with mirzzassi account
        result = await service.authenticate_user("mirzzassi", "password123")
        
        print("Instagram service result:")
        print(json.dumps(result, indent=2, default=str))
        
        if result.get("success"):
            print("✅ Instagram service authentication successful!")
            if "user_data" in result:
                user_data = result["user_data"]
                print(f"   - Username: {user_data.get('username')}")
                print(f"   - Followers: {user_data.get('follower_count')}")
                print(f"   - Following: {user_data.get('following_count')}")
                print(f"   - Posts: {user_data.get('media_count')}")
        else:
            print(f"❌ Instagram service authentication failed: {result.get('message')}")
            if result.get("error_type") == "challenge_required":
                print("⚠️ Challenge required - this is expected behavior")
        
        return result.get("success", False)
        
    except Exception as e:
        print(f"❌ Error testing Instagram service: {e}")
        return False

async def main():
    """Main test function"""
    print("=" * 60)
    print("INSTAGRAM AUTHENTICATION TEST")
    print("=" * 60)
    
    # Test 1: Current session
    session_valid = await test_current_session()
    
    # Test 2: Instagram service
    service_works = await test_instagram_service()
    
    print("\n" + "=" * 60)
    print("TEST SUMMARY")
    print("=" * 60)
    print(f"Current session valid: {'✅' if session_valid else '❌'}")
    print(f"Instagram service works: {'✅' if service_works else '❌'}")
    
    if session_valid and service_works:
        print("\n🎉 All tests passed! Instagram authentication is working.")
    elif service_works:
        print("\n⚠️ Instagram service is working but session needs refresh.")
    else:
        print("\n❌ Instagram authentication needs attention.")

if __name__ == "__main__":
    asyncio.run(main())
