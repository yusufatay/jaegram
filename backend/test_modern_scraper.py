#!/usr/bin/env python3
"""
Test script for the modern Instagram scraper
"""

import sys
import os
sys.path.append(os.path.dirname(__file__))

import asyncio
from modern_instagram_scraper import scrape_instagram_profile_modern
from enhanced_instagram_collector import enhanced_instagram_collector

async def test_modern_scraper():
    """Test the modern scraper with various Instagram usernames"""
    
    # Test usernames (public profiles)
    test_usernames = [
        "instagram",  # Instagram's official account
        "semihulusoyw",  # The problematic account mentioned in conversation
        "cristiano",  # Large public account
        "nasa"  # Another well-known public account
    ]
    
    print("🔍 Testing Modern Instagram Scraper")
    print("=" * 50)
    
    for username in test_usernames:
        print(f"\n📱 Testing username: {username}")
        print("-" * 30)
        
        try:
            # Test modern scraper directly
            result = scrape_instagram_profile_modern(username)
            
            if result.get("success"):
                profile = result["profile"]
                print(f"✅ Success!")
                print(f"   Username: {profile.get('username', 'N/A')}")
                print(f"   Full Name: {profile.get('full_name', 'N/A')}")
                print(f"   Bio: {profile.get('bio', 'N/A')[:50]}{'...' if len(profile.get('bio', '')) > 50 else ''}")
                print(f"   Profile Picture: {'✓' if profile.get('profile_pic_url') else '✗'}")
                if profile.get('profile_pic_url'):
                    print(f"   Picture URL: {profile['profile_pic_url'][:80]}...")
                print(f"   Followers: {profile.get('followers_count', 0):,}")
                print(f"   Following: {profile.get('following_count', 0):,}")
                print(f"   Posts: {profile.get('media_count', 0):,}")
                print(f"   Private: {profile.get('is_private', False)}")
                print(f"   Verified: {profile.get('is_verified', False)}")
            else:
                print(f"❌ Failed: {result.get('message', 'Unknown error')}")
                
        except Exception as e:
            print(f"💥 Exception: {e}")
    
    print("\n" + "=" * 50)
    print("🔍 Testing Enhanced Collector (with modern scraper fallback)")
    print("=" * 50)
    
    # Test the enhanced collector which should use the modern scraper
    for username in test_usernames[:2]:  # Test fewer for enhanced collector
        print(f"\n📱 Testing enhanced collector for: {username}")
        print("-" * 30)
        
        try:
            result = await enhanced_instagram_collector.scrape_public_profile(username)
            
            if result.get("success"):
                print(f"✅ Success!")
                print(f"   Profile Picture: {'✓' if result.get('profile_pic_url') else '✗'}")
                if result.get('profile_pic_url'):
                    print(f"   Picture URL: {result['profile_pic_url'][:80]}...")
                print(f"   Followers: {result.get('followers_count', 0):,}")
                print(f"   Posts: {result.get('media_count', 0):,}")
            else:
                print(f"❌ Failed: {result.get('message', 'Unknown error')}")
                
        except Exception as e:
            print(f"💥 Exception: {e}")

if __name__ == "__main__":
    asyncio.run(test_modern_scraper())
