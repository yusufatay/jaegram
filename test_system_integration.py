#!/usr/bin/env python3
"""
Complete system integration test for Instagram Coin Platform
Tests all major functionality including login, statistics, notifications, etc.
"""

import requests
import json
import time
from datetime import datetime

BASE_URL = "http://localhost:8000"

class InstagramCoinPlatformTester:
    def __init__(self):
        self.token = None
        self.test_results = []
    
    def log_test(self, test_name, success, details=""):
        """Log test results"""
        status = "✅ PASS" if success else "❌ FAIL"
        timestamp = datetime.now().strftime("%H:%M:%S")
        result = f"[{timestamp}] {status} - {test_name}"
        if details:
            result += f" - {details}"
        print(result)
        self.test_results.append((test_name, success, details))
    
    def test_login(self):
        """Test user login functionality"""
        print("\n🔐 Testing Login System...")
        
        # Test regular login
        login_data = {
            "username": "luvmef",
            "password": "asgsag2"
        }
        
        try:
            response = requests.post(
                f"{BASE_URL}/login",
                data=login_data,
                headers={"Content-Type": "application/x-www-form-urlencoded"}
            )
            
            if response.status_code == 200:
                token_data = response.json()
                self.token = token_data.get('access_token')
                self.log_test("Platform Login", True, f"Token received: {self.token[:20]}...")
                return True
            else:
                self.log_test("Platform Login", False, f"Status: {response.status_code}, Response: {response.text}")
                return False
                
        except Exception as e:
            self.log_test("Platform Login", False, f"Exception: {str(e)}")
            return False
    
    def test_profile(self):
        """Test profile endpoint"""
        if not self.token:
            self.log_test("Profile Fetch", False, "No token available")
            return False
        
        try:
            headers = {"Authorization": f"Bearer {self.token}"}
            response = requests.get(f"{BASE_URL}/profile", headers=headers)
            
            if response.status_code == 200:
                profile = response.json()
                expected_fields = ['id', 'username', 'coin_balance', 'completed_tasks']
                missing_fields = [field for field in expected_fields if field not in profile]
                
                if not missing_fields:
                    self.log_test("Profile Fetch", True, f"User: {profile.get('username')}, Coins: {profile.get('coin_balance')}")
                    return True
                else:
                    self.log_test("Profile Fetch", False, f"Missing fields: {missing_fields}")
                    return False
            else:
                self.log_test("Profile Fetch", False, f"Status: {response.status_code}")
                return False
                
        except Exception as e:
            self.log_test("Profile Fetch", False, f"Exception: {str(e)}")
            return False
    
    def test_statistics(self):
        """Test statistics endpoint"""
        if not self.token:
            self.log_test("Statistics Fetch", False, "No token available")
            return False
        
        try:
            headers = {"Authorization": f"Bearer {self.token}"}
            response = requests.get(f"{BASE_URL}/statistics", headers=headers)
            
            if response.status_code == 200:
                stats = response.json()
                expected_fields = ['total_earnings', 'completed_tasks', 'task_distribution', 'weekly_earnings']
                missing_fields = [field for field in expected_fields if field not in stats]
                
                if not missing_fields:
                    task_dist = stats.get('task_distribution', {})
                    self.log_test("Statistics Fetch", True, f"Earnings: {stats.get('total_earnings')}, Tasks: {len(task_dist)} types")
                    
                    # Verify task_distribution contains numeric values (should be convertible to float)
                    try:
                        for key, value in task_dist.items():
                            float(value)  # This should work after our fixes
                        self.log_test("Task Distribution Type Cast", True, "All values are numeric")
                        return True
                    except (ValueError, TypeError) as e:
                        self.log_test("Task Distribution Type Cast", False, f"Type error: {str(e)}")
                        return False
                else:
                    self.log_test("Statistics Fetch", False, f"Missing fields: {missing_fields}")
                    return False
            else:
                self.log_test("Statistics Fetch", False, f"Status: {response.status_code}")
                return False
                
        except Exception as e:
            self.log_test("Statistics Fetch", False, f"Exception: {str(e)}")
            return False
    
    def test_notifications(self):
        """Test notifications endpoint"""
        if not self.token:
            self.log_test("Notifications Fetch", False, "No token available")
            return False
        
        try:
            headers = {"Authorization": f"Bearer {self.token}"}
            response = requests.get(f"{BASE_URL}/notifications", headers=headers)
            
            if response.status_code == 200:
                notifications = response.json()
                if isinstance(notifications, list):
                    if notifications:
                        first_notif = notifications[0]
                        expected_fields = ['id', 'message', 'is_read', 'created_at']
                        missing_fields = [field for field in expected_fields if field not in first_notif]
                        
                        if not missing_fields:
                            unread_count = sum(1 for n in notifications if not n.get('is_read', True))
                            self.log_test("Notifications Fetch", True, f"Count: {len(notifications)}, Unread: {unread_count}")
                            return True
                        else:
                            self.log_test("Notifications Fetch", False, f"Missing fields in notification: {missing_fields}")
                            return False
                    else:
                        self.log_test("Notifications Fetch", True, "Empty notifications list (valid)")
                        return True
                else:
                    self.log_test("Notifications Fetch", False, f"Expected list, got: {type(notifications)}")
                    return False
            else:
                self.log_test("Notifications Fetch", False, f"Status: {response.status_code}")
                return False
                
        except Exception as e:
            self.log_test("Notifications Fetch", False, f"Exception: {str(e)}")
            return False
    
    def test_instagram_login_endpoint(self):
        """Test Instagram login endpoint (should fail with invalid credentials)"""
        try:
            login_data = {
                "username": "test_user",
                "password": "test_pass"
            }
            
            response = requests.post(
                f"{BASE_URL}/login-instagram",
                json=login_data,
                headers={"Content-Type": "application/json"}
            )
            
            # We expect this to fail with invalid credentials, but the endpoint should respond properly
            if response.status_code in [400, 401, 422]:
                response_data = response.json()
                if "message" in response_data or "detail" in response_data:
                    self.log_test("Instagram Login Endpoint", True, "Properly rejects invalid credentials")
                    return True
                else:
                    self.log_test("Instagram Login Endpoint", False, "Missing error message in response")
                    return False
            else:
                self.log_test("Instagram Login Endpoint", False, f"Unexpected status: {response.status_code}")
                return False
                
        except Exception as e:
            self.log_test("Instagram Login Endpoint", False, f"Exception: {str(e)}")
            return False
    
    def run_all_tests(self):
        """Run all system tests"""
        print("🚀 Starting Instagram Coin Platform Integration Tests")
        print(f"⏰ Test Started: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print(f"🎯 Target: {BASE_URL}")
        
        # Test sequence
        tests = [
            self.test_login,
            self.test_profile,
            self.test_statistics,
            self.test_notifications,
            self.test_instagram_login_endpoint,
        ]
        
        passed = 0
        failed = 0
        
        for test in tests:
            if test():
                passed += 1
            else:
                failed += 1
        
        # Summary
        print(f"\n📊 Test Summary:")
        print(f"✅ Passed: {passed}")
        print(f"❌ Failed: {failed}")
        print(f"📈 Success Rate: {(passed/(passed+failed)*100):.1f}%")
        
        if failed == 0:
            print("\n🎉 All tests passed! System is working correctly.")
        else:
            print(f"\n⚠️  {failed} test(s) failed. Check the details above.")
        
        return failed == 0

if __name__ == "__main__":
    tester = InstagramCoinPlatformTester()
    success = tester.run_all_tests()
    exit(0 if success else 1)
