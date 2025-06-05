#!/usr/bin/env python3
"""
Advanced Instagram Integration Test Script
- Handles 2FA and challenge responses
- Tests complete Instagram workflow
- Real API integration
"""
import requests
import json
import time
import sys

BASE_URL = "http://localhost:8000"

def test_complete_instagram_integration():
    print("🚀 Advanced Instagram Integration Test")
    print("="*60)
    
    # Real Instagram credentials
    instagram_username = "luvmef"
    instagram_password = "asgsag2"
    
    # Platform test user
    platform_username = f"testuser_{int(time.time())}"
    platform_password = "testpass123"
    
    print(f"📝 Creating platform user: {platform_username}")
    print(f"📸 Testing Instagram user: {instagram_username}")
    print("-" * 60)
    
    # 1. Platform Registration
    print("\n1. 🔐 Platform Registration & Login")
    register_data = {
        "username": platform_username,
        "password": platform_password,
        "email": f"{platform_username}@test.com"
    }
    
    response = requests.post(f"{BASE_URL}/register", json=register_data)
    print(f"   Registration: {response.status_code}")
    
    # Login to get platform token
    login_data = {
        "username": platform_username,
        "password": platform_password
    }
    
    response = requests.post(f"{BASE_URL}/login", data=login_data)
    print(f"   Login: {response.status_code}")
    
    if response.status_code != 200:
        print("❌ Platform login failed")
        return False
    
    platform_token = response.json()["access_token"]
    headers = {"Authorization": f"Bearer {platform_token}"}
    print("   ✅ Platform authentication successful")
    
    # 2. Instagram Authentication
    print("\n2. 📸 Instagram Authentication")
    instagram_login_data = {
        "username": instagram_username,
        "password": instagram_password
    }
    
    response = requests.post(f"{BASE_URL}/login-instagram", json=instagram_login_data)
    print(f"   Instagram Login Status: {response.status_code}")
    
    if response.status_code == 200:
        print("   ✅ Instagram login successful!")
        instagram_data = response.json()
        print(f"   👤 Username: {instagram_data.get('username')}")
        print(f"   📋 Full Name: {instagram_data.get('full_name')}")
        print(f"   👥 Followers: {instagram_data.get('followers_count')}")
        print(f"   🔗 Following: {instagram_data.get('following_count')}")
        
        instagram_token = instagram_data.get('access_token')
        if instagram_token:
            headers = {"Authorization": f"Bearer {instagram_token}"}
        
    elif response.status_code == 400:
        # Challenge required
        try:
            error_data = response.json()
            if "challenge" in error_data.get("detail", "").lower():
                print("   🔐 Instagram Challenge Required")
                print("   📧 Please check your email/SMS for verification code")
                
                # Ask user for challenge code
                challenge_code = input("   Enter verification code (6 digits): ").strip()
                
                if challenge_code and len(challenge_code) == 6:
                    print(f"   📝 Submitting challenge code: {challenge_code}")
                    
                    challenge_data = {
                        "username": instagram_username,
                        "password": instagram_password,
                        "challenge_code": challenge_code
                    }
                    
                    response = requests.post(f"{BASE_URL}/login-instagram-challenge", json=challenge_data)
                    print(f"   Challenge Response: {response.status_code}")
                    
                    if response.status_code == 200:
                        print("   ✅ Instagram challenge completed successfully!")
                        instagram_data = response.json()
                        print(f"   👤 Username: {instagram_data.get('username')}")
                        print(f"   📋 Full Name: {instagram_data.get('full_name')}")
                        instagram_token = instagram_data.get('access_token')
                        if instagram_token:
                            headers = {"Authorization": f"Bearer {instagram_token}"}
                    else:
                        print("   ❌ Challenge failed")
                        print(f"   Error: {response.text}")
                        return False
                else:
                    print("   ❌ Invalid challenge code")
                    return False
            else:
                print(f"   ❌ Instagram login error: {error_data}")
                return False
        except:
            print(f"   ❌ Instagram login failed: {response.text}")
            return False
    else:
        print(f"   ❌ Instagram login failed: {response.text}")
        return False
    
    # 3. Test Instagram Profile Data
    print("\n3. 👤 Testing Instagram Profile Data Retrieval")
    response = requests.get(f"{BASE_URL}/profile", headers=headers)
    print(f"   Profile Status: {response.status_code}")
    
    if response.status_code == 200:
        profile_data = response.json()
        print(f"   ✅ Profile retrieved successfully")
        print(f"   Username: {profile_data.get('username')}")
        print(f"   Coins: {profile_data.get('coins', 0)}")
        print(f"   Instagram Connected: {profile_data.get('instagram_username')}")
    else:
        print(f"   ❌ Profile retrieval failed: {response.text}")
    
    # 4. Test Task System (if we have Instagram connection)
    print("\n4. 🎯 Testing Task System Integration")
    # Create a sample order to see if task system works
    order_data = {
        "url": "https://www.instagram.com/p/sample_post/",
        "order_type": "like",
        "target_count": 5,
        "description": "Test Instagram like order"
    }
    
    response = requests.post(f"{BASE_URL}/orders", json=order_data, headers=headers)
    print(f"   Order Creation: {response.status_code}")
    
    if response.status_code == 200:
        order_response = response.json()
        print(f"   ✅ Order created successfully")
        print(f"   Order ID: {order_response.get('order_id')}")
        print(f"   Tasks Generated: {order_response.get('tasks_created', 0)}")
    else:
        print(f"   ❌ Order creation failed: {response.text}")
    
    # 5. Test Available Tasks
    print("\n5. 📋 Testing Available Tasks")
    response = requests.get(f"{BASE_URL}/tasks/available", headers=headers)
    print(f"   Available Tasks Status: {response.status_code}")
    
    if response.status_code == 200:
        tasks_data = response.json()
        print(f"   ✅ Available tasks retrieved")
        print(f"   Total Available: {len(tasks_data.get('tasks', []))}")
        
        if tasks_data.get('tasks'):
            task = tasks_data['tasks'][0]
            print(f"   Sample Task ID: {task.get('id')}")
            print(f"   Task Type: {task.get('task_type')}")
            print(f"   Reward: {task.get('coin_reward')} coins")
    else:
        print(f"   ❌ Available tasks retrieval failed: {response.text}")
    
    # 6. Test Instagram Verification
    print("\n6. 🔍 Testing Instagram Verification System")
    verification_data = {
        "instagram_username": instagram_username,
        "amount": 50
    }
    
    response = requests.post(f"{BASE_URL}/coins/verify-instagram", json=verification_data, headers=headers)
    print(f"   Instagram Verification: {response.status_code}")
    
    if response.status_code == 200:
        verify_response = response.json()
        print(f"   ✅ Instagram verification completed")
        print(f"   Profile Verified: {verify_response.get('profile_verified', False)}")
        print(f"   Posts Count: {verify_response.get('posts_count', 0)}")
    else:
        print(f"   ❌ Instagram verification failed: {response.text}")
    
    print("\n" + "="*60)
    print("🎉 Advanced Instagram Integration Test Completed!")
    print("="*60)
    return True

if __name__ == "__main__":
    try:
        test_complete_instagram_integration()
    except KeyboardInterrupt:
        print("\n⚠️  Test interrupted by user")
    except Exception as e:
        print(f"\n❌ Test failed with error: {e}")
        import traceback
        traceback.print_exc()
