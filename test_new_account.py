#!/usr/bin/env python3
"""
Test new Instagram account with modern scraper
"""
import asyncio
import sys
import os

# Add backend directory to path
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), 'backend'))

from modern_instagram_scraper import ModernInstagramScraper
import logging

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

async def test_instagram_account(username):
    """Test Instagram account scraping"""
    print(f"🔍 Testing Instagram account: @{username}")
    print("=" * 50)
    
    scraper = ModernInstagramScraper()
    
    try:
        result = await scraper.scrape_profile(username)
        
        if result.get("success"):
            profile = result.get("profile", {})
            print("✅ Successfully scraped profile!")
            print(f"📝 Username: {profile.get('username', 'N/A')}")
            print(f"👤 Full Name: {profile.get('full_name', 'N/A')}")
            print(f"📄 Bio: {profile.get('bio', 'N/A')}")
            print(f"🖼️  Profile Pic: {'✓' if profile.get('profile_pic_url') else '✗'}")
            print(f"👥 Followers: {profile.get('followers_count', 0)}")
            print(f"👥 Following: {profile.get('following_count', 0)}")
            print(f"📸 Posts: {profile.get('media_count', 0)}")
            print(f"🔒 Private: {'Yes' if profile.get('is_private') else 'No'}")
            print(f"✅ Verified: {'Yes' if profile.get('is_verified') else 'No'}")
            
            if profile.get('profile_pic_url'):
                print(f"🔗 Profile Pic URL: {profile['profile_pic_url']}")
            
            return True
        else:
            print(f"❌ Failed to scrape profile: {result.get('message', 'Unknown error')}")
            return False
            
    except Exception as e:
        print(f"❌ Error: {e}")
        return False

if __name__ == "__main__":
    username = "williamjohnson12935"
    asyncio.run(test_instagram_account(username))
