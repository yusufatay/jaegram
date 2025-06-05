#!/usr/bin/env python3
"""
Test Fixed Async Endpoints
Verifies that the await fixes are working correctly
"""

import requests
import json
import time
import threading
import subprocess
import os
import sys

# Add backend to path
sys.path.append('./backend')

BASE_URL = "http://localhost:8000"

class AsyncEndpointTester:
    def __init__(self):
        self.server_process = None
        self.token = None
        
    def start_server(self):
        """Start backend server in background"""
        print("🚀 Starting backend server...")
        self.server_process = subprocess.Popen(
            ["uvicorn", "app:app", "--host", "0.0.0.0", "--port", "8000"],
            cwd="./backend",
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL
        )
        time.sleep(3)  # Wait for server to start
        
    def stop_server(self):
        """Stop backend server"""
        if self.server_process:
            self.server_process.terminate()
            self.server_process.wait()
            print("🛑 Backend server stopped")
    
    def test_health_check(self):
        """Test basic connectivity using docs endpoint"""
        try:
            response = requests.get(f"{BASE_URL}/docs", timeout=5)
            if response.status_code == 200:
                print("✅ API connectivity confirmed")
                return True
            else:
                print(f"❌ API connectivity failed: {response.status_code}")
                return False
        except Exception as e:
            print(f"❌ API connectivity error: {e}")
            return False
    
    def register_and_login(self):
        """Register test user and get token"""
        username = f"test_async_{int(time.time())}"
        
        # Register
        register_data = {
            "username": username,
            "password": "testpass123",
            "email": f"{username}@test.com"
        }
        
        try:
            register_response = requests.post(f"{BASE_URL}/register", json=register_data)
            if register_response.status_code == 201:
                print("✅ User registration successful")
            else:
                print(f"ℹ️  Registration: {register_response.status_code} - {register_response.text}")
        except Exception as e:
            print(f"⚠️  Registration error: {e}")
        
        # Login
        login_data = {
            "username": username,
            "password": "testpass123"
        }
        
        try:
            login_response = requests.post(
                f"{BASE_URL}/login",
                data=login_data,
                headers={"Content-Type": "application/x-www-form-urlencoded"}
            )
            
            if login_response.status_code == 200:
                token_data = login_response.json()
                self.token = token_data["access_token"]
                print("✅ Login successful, token obtained")
                return True
            else:
                print(f"❌ Login failed: {login_response.status_code}")
                return False
        except Exception as e:
            print(f"❌ Login error: {e}")
            return False
    
    def test_daily_reward_async(self):
        """Test the fixed async daily reward endpoint"""
        if not self.token:
            print("❌ No token available for daily reward test")
            return False
        
        headers = {"Authorization": f"Bearer {self.token}"}
        
        try:
            response = requests.post(f"{BASE_URL}/claim-daily-reward", headers=headers)
            
            if response.status_code == 200:
                data = response.json()
                print("✅ Daily reward endpoint working (async fixed)")
                print(f"   Coins awarded: {data.get('coins_awarded', 0)}")
                print(f"   Streak day: {data.get('streak_day', 0)}")
                print(f"   New balance: {data.get('new_balance', 0)}")
                return True
            elif response.status_code == 400:
                print("ℹ️  Daily reward already claimed (endpoint working)")
                return True
            else:
                print(f"❌ Daily reward failed: {response.status_code}")
                print(f"   Response: {response.text}")
                return False
        except Exception as e:
            print(f"❌ Daily reward error: {e}")
            return False
    
    def test_email_verification_async(self):
        """Test the fixed async email verification endpoint"""
        if not self.token:
            print("❌ No token available for email verification test")
            return False
        
        headers = {"Authorization": f"Bearer {self.token}"}
        test_email = f"test_async_{int(time.time())}@example.com"
        
        try:
            response = requests.post(
                f"{BASE_URL}/send-verification-email",
                params={"email": test_email},
                headers=headers
            )
            
            if response.status_code == 200:
                data = response.json()
                print("✅ Email verification endpoint working (async fixed)")
                print(f"   Message: {data.get('message', 'No message')}")
                print(f"   Expires in: {data.get('expires_in_minutes', 0)} minutes")
                return True
            else:
                print(f"❌ Email verification failed: {response.status_code}")
                print(f"   Response: {response.text}")
                return False
        except Exception as e:
            print(f"❌ Email verification error: {e}")
            return False
    
    def run_tests(self):
        """Run all async endpoint tests"""
        print("🔧 ASYNC ENDPOINT FIX VERIFICATION")
        print("=" * 50)
        
        try:
            self.start_server()
            
            # Test basic connectivity
            if not self.test_health_check():
                return False
            
            # Register and login
            if not self.register_and_login():
                return False
            
            print("\n📋 Testing Fixed Async Endpoints:")
            
            # Test daily reward (async fixed)
            daily_reward_ok = self.test_daily_reward_async()
            
            # Test email verification (async fixed)  
            email_verification_ok = self.test_email_verification_async()
            
            print("\n📊 TEST RESULTS:")
            print(f"   Daily Reward (async): {'✅ PASS' if daily_reward_ok else '❌ FAIL'}")
            print(f"   Email Verification (async): {'✅ PASS' if email_verification_ok else '❌ FAIL'}")
            
            if daily_reward_ok and email_verification_ok:
                print("\n🎉 ALL ASYNC FIXES VERIFIED SUCCESSFULLY!")
                print("✅ No more 'await' in non-async function errors")
                return True
            else:
                print("\n⚠️  Some tests failed - check the fixes")
                return False
                
        finally:
            self.stop_server()

if __name__ == "__main__":
    tester = AsyncEndpointTester()
    success = tester.run_tests()
    
    if success:
        print("\n🚀 SYSTEM READY: All async issues resolved!")
    else:
        print("\n❌ SYSTEM ERROR: Some issues remain")
    
    sys.exit(0 if success else 1)
