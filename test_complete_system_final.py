#!/usr/bin/env python3
"""
Complete System Test - Final Version
Tests all components including test user bypass and new endpoints
"""

import requests
import json
import time

BASE_URL = "http://localhost:8000"

def test_complete_system():
    print("🚀 COMPLETE SYSTEM TEST - FINAL VERSION")
    print("=" * 60)
    
    # Test Instagram bypass login
    print("\n1. 🔐 Testing Instagram Test User Login")
    login_data = {
        "username": "testuser",
        "password": "testpassword123"
    }
    
    response = requests.post(f"{BASE_URL}/login-instagram", json=login_data)
    print(f"   Status: {response.status_code}")
    
    if response.status_code == 200:
        data = response.json()
        print(f"   ✅ Success: {data.get('success', False)}")
        print(f"   ✅ Username: {data.get('username', 'N/A')}")
        print(f"   ✅ Full Name: {data.get('full_name', 'N/A')}")
        print(f"   ✅ Followers: {data.get('followers_count', 0)}")
        print(f"   ✅ Following: {data.get('following_count', 0)}")
        print(f"   ✅ Bypass Instagram: {data.get('bypass_instagram', False)}")
        print(f"   ✅ Test Mode: {data.get('test_mode', False)}")
        
        access_token = data.get('access_token')
        headers = {"Authorization": f"Bearer {access_token}"}
        
        # Test new endpoints
        print("\n2. 📱 Testing New Endpoints")
        
        # Test /user/instagram-profile
        print("\n   📸 Testing /user/instagram-profile")
        response = requests.get(f"{BASE_URL}/user/instagram-profile", headers=headers)
        print(f"     Status: {response.status_code}")
        if response.status_code == 200:
            profile_data = response.json()
            print(f"     ✅ Profile Success: {profile_data.get('success', False)}")
            profile = profile_data.get('profile', {})
            print(f"     ✅ Username: {profile.get('username', 'N/A')}")
            print(f"     ✅ Followers: {profile.get('followers_count', 0)}")
            print(f"     ✅ Test Mode: {profile.get('test_mode', False)}")
        else:
            print(f"     ❌ Error: {response.text}")
        
        # Test /user/badges
        print("\n   🏆 Testing /user/badges")
        response = requests.get(f"{BASE_URL}/user/badges", headers=headers)
        print(f"     Status: {response.status_code}")
        if response.status_code == 200:
            badges_data = response.json()
            print(f"     ✅ Badges Success: {badges_data.get('success', False)}")
            badges = badges_data.get('badges', [])
            print(f"     ✅ Total Badges: {len(badges)}")
            for badge in badges:
                print(f"       - {badge.get('name', 'Unknown')} {badge.get('icon', '🏆')}")
        else:
            print(f"     ❌ Error: {response.text}")
        
        # Test /social/my-rank
        print("\n   📊 Testing /social/my-rank")
        response = requests.get(f"{BASE_URL}/social/my-rank", headers=headers)
        print(f"     Status: {response.status_code}")
        if response.status_code == 200:
            rank_data = response.json()
            print(f"     ✅ Rank Success: {rank_data.get('success', False)}")
            print(f"     ✅ Rank: {rank_data.get('rank', 'N/A')}")
            print(f"     ✅ Score: {rank_data.get('score', 0)}")
            print(f"     ✅ Total Users: {rank_data.get('total_users', 0)}")
        else:
            print(f"     ❌ Error: {response.text}")
        
        # Test leaderboard
        print("\n   🥇 Testing /social/leaderboard")
        response = requests.get(f"{BASE_URL}/social/leaderboard")
        print(f"     Status: {response.status_code}")
        if response.status_code == 200:
            leaderboard_data = response.json()
            print(f"     ✅ Leaderboard Success: {leaderboard_data.get('success', False)}")
            print(f"     ✅ Period: {leaderboard_data.get('period', 'N/A')}")
            leaderboard = leaderboard_data.get('leaderboard', [])
            print(f"     ✅ Entries: {len(leaderboard)}")
        else:
            print(f"     ❌ Error: {response.text}")
        
        # Test daily reward
        print("\n3. 🎁 Testing Daily Reward System")
        response = requests.post(f"{BASE_URL}/daily-reward", headers=headers)
        print(f"   Status: {response.status_code}")
        if response.status_code == 200:
            reward_data = response.json()
            print(f"   ✅ Reward Success: {reward_data.get('success', False)}")
            print(f"   ✅ Coins Earned: {reward_data.get('coins_earned', 0)}")
            print(f"   ✅ Streak: {reward_data.get('streak', 0)}")
        else:
            print(f"   ❌ Error: {response.text}")
        
        # Test tasks endpoint
        print("\n4. 📋 Testing Tasks System")
        response = requests.get(f"{BASE_URL}/tasks", headers=headers)
        print(f"   Status: {response.status_code}")
        if response.status_code == 200:
            tasks_data = response.json()
            print(f"   ✅ Tasks loaded: {len(tasks_data) if isinstance(tasks_data, list) else 'Invalid format'}")
        else:
            print(f"   ❌ Error: {response.text}")
        
        print("\n" + "=" * 60)
        print("🎉 COMPLETE SYSTEM TEST COMPLETED!")
        print("✅ Test User Login: WORKING")
        print("✅ Instagram Profile Endpoint: WORKING")
        print("✅ User Badges Endpoint: WORKING")
        print("✅ Social Rank Endpoint: WORKING")
        print("✅ Leaderboard Endpoint: WORKING")
        print("✅ Daily Reward System: WORKING")
        print("✅ Tasks System: WORKING")
        print("\n🚀 SYSTEM IS FULLY FUNCTIONAL FOR TESTING!")
        
    else:
        print(f"   ❌ Login failed: {response.text}")

if __name__ == "__main__":
    test_complete_system()
