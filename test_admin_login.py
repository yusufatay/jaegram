#!/usr/bin/env python3
"""
Test script for admin login functionality
"""
import requests
import json
import time

BASE_URL = "http://localhost:8000"

def test_admin_login():
    """Test the admin login bypass functionality"""
    print("🔐 Testing Admin Login System")
    print("=" * 50)
    
    # Test admin login
    print("\n1. Testing admin login with admin/admin credentials...")
    admin_login_data = {
        "username": "admin",
        "password": "admin"
    }
    
    response = requests.post(f"{BASE_URL}/login-instagram", json=admin_login_data)
    print(f"Status Code: {response.status_code}")
    
    if response.status_code == 200:
        print("✅ Admin login successful!")
        login_data = response.json()
        
        print(f"👤 Username: {login_data.get('username')}")
        print(f"📋 Full Name: {login_data.get('full_name')}")
        print(f"🎯 User ID: {login_data.get('user_id')}")
        print(f"🔒 Token Type: {login_data.get('token_type')}")
        print(f"⚡ Is Admin: {login_data.get('user_data', {}).get('is_admin')}")
        print(f"🚫 Bypass Instagram: {login_data.get('user_data', {}).get('bypass_instagram')}")
        print(f"💰 Coin Balance: {login_data.get('user_data', {}).get('coin_balance')}")
        
        admin_token = login_data.get('access_token')
        if admin_token:
            print(f"🎫 Access Token: {admin_token[:20]}...")
            
            # Test admin profile endpoint
            print("\n2. Testing admin profile endpoint...")
            headers = {"Authorization": f"Bearer {admin_token}"}
            profile_response = requests.get(f"{BASE_URL}/profile", headers=headers)
            
            print(f"Profile Status Code: {profile_response.status_code}")
            
            if profile_response.status_code == 200:
                print("✅ Admin profile retrieved successfully!")
                profile_data = profile_response.json()
                
                print(f"👤 Profile Username: {profile_data.get('username')}")
                print(f"📋 Profile Full Name: {profile_data.get('full_name')}")
                print(f"💰 Profile Coin Balance: {profile_data.get('coin_balance')}")
                print(f"🛡️ Is Admin Platform: {profile_data.get('is_admin_platform')}")
                print(f"📊 Instagram Stats: {profile_data.get('instagram_stats')}")
                print(f"✅ Completed Tasks: {profile_data.get('completed_tasks')}")
                print(f"🔄 Active Tasks: {profile_data.get('active_tasks')}")
                
                # Test admin endpoints access
                print("\n3. Testing admin endpoints access...")
                
                # Test admin users endpoint
                admin_users_response = requests.get(f"{BASE_URL}/admin/users", headers=headers)
                print(f"Admin Users Endpoint: {admin_users_response.status_code}")
                
                if admin_users_response.status_code == 200:
                    print("✅ Admin has access to user management!")
                    users_data = admin_users_response.json()
                    print(f"Total Users in System: {len(users_data)}")
                    
                    # Show admin user in the list
                    admin_user_in_list = next((user for user in users_data if user.get('username') == 'admin'), None)
                    if admin_user_in_list:
                        print(f"Admin User Found: {admin_user_in_list}")
                else:
                    print(f"❌ Admin endpoint access failed: {admin_users_response.text}")
                
                # Test admin orders endpoint
                admin_orders_response = requests.get(f"{BASE_URL}/admin/orders", headers=headers)
                print(f"Admin Orders Endpoint: {admin_orders_response.status_code}")
                
                if admin_orders_response.status_code == 200:
                    print("✅ Admin has access to order management!")
                    orders_data = admin_orders_response.json()
                    print(f"Total Orders in System: {len(orders_data)}")
                else:
                    print(f"❌ Admin orders endpoint access failed: {admin_orders_response.text}")
                
            else:
                print(f"❌ Admin profile retrieval failed: {profile_response.text}")
        
    else:
        print(f"❌ Admin login failed: {response.text}")
        return False
    
    # Test with wrong admin credentials
    print("\n4. Testing with wrong admin credentials...")
    wrong_admin_data = {
        "username": "admin",
        "password": "wrongpassword"
    }
    
    response = requests.post(f"{BASE_URL}/login-instagram", json=wrong_admin_data)
    print(f"Wrong Password Status Code: {response.status_code}")
    
    if response.status_code != 200:
        print("✅ Wrong admin password correctly rejected!")
    else:
        print("❌ Wrong admin password was accepted (security issue!)")
    
    # Test with non-admin user trying to access admin endpoints
    print("\n5. Testing regular user access to admin endpoints...")
    
    # Create a test user
    test_user_data = {
        "username": f"testuser_{int(time.time())}",
        "password": "testpass123",
        "email": f"test_{int(time.time())}@example.com"
    }
    
    register_response = requests.post(f"{BASE_URL}/register", json=test_user_data)
    if register_response.status_code == 200:
        # Login with test user
        login_response = requests.post(f"{BASE_URL}/login", data={
            "username": test_user_data["username"],
            "password": test_user_data["password"]
        })
        
        if login_response.status_code == 200:
            test_token = login_response.json().get("access_token")
            test_headers = {"Authorization": f"Bearer {test_token}"}
            
            # Try to access admin endpoint
            admin_access_response = requests.get(f"{BASE_URL}/admin/users", headers=test_headers)
            print(f"Regular User Admin Access: {admin_access_response.status_code}")
            
            if admin_access_response.status_code == 403:
                print("✅ Regular user correctly denied admin access!")
            else:
                print("❌ Regular user gained admin access (security issue!)")
    
    print("\n" + "=" * 50)
    print("🎉 Admin Login System Test Complete!")
    return True

def test_server_health():
    """Test if server is running"""
    try:
        response = requests.get(f"{BASE_URL}/health", timeout=5)
        return response.status_code == 200
    except:
        return False

if __name__ == "__main__":
    print("🚀 Starting Admin Login System Test")
    
    # Check if server is running
    if not test_server_health():
        print("❌ Server is not running. Please start the backend server first:")
        print("   cd backend && python -m uvicorn app:app --reload --port 8000")
        exit(1)
    
    print("✅ Server is running")
    
    try:
        test_admin_login()
    except KeyboardInterrupt:
        print("\n⚠️  Test interrupted by user")
    except Exception as e:
        print(f"\n❌ Test failed with error: {e}")
        import traceback
        traceback.print_exc()
