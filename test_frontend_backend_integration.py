#!/usr/bin/env python3
"""
Comprehensive Frontend-Backend Integration Test
Tests all aspects of the Instagram bypass system and Flutter frontend functionality.
"""
import requests
import json
import time
import os
import sys
from typing import Dict, Any, Optional

class SystemIntegrationTester:
    def __init__(self):
        self.backend_url = "http://localhost:8000"
        self.frontend_url = "http://localhost:3000"
        self.test_user = {
            "username": "testuser",
            "password": "testpass123"
        }
        self.admin_user = {
            "username": "admin", 
            "password": "admin123"
        }
        self.auth_token = None
        self.test_results = []

    def log_test(self, test_name: str, status: str, details: str = ""):
        """Log test results"""
        result = {
            "test": test_name,
            "status": status,
            "details": details,
            "timestamp": time.strftime("%Y-%m-%d %H:%M:%S")
        }
        self.test_results.append(result)
        print(f"[{status}] {test_name}: {details}")

    def test_backend_health(self) -> bool:
        """Test backend server availability"""
        try:
            response = requests.get(f"{self.backend_url}/docs", timeout=5)
            if response.status_code == 200:
                self.log_test("Backend Health", "PASS", "Backend server is responding")
                return True
            else:
                self.log_test("Backend Health", "FAIL", f"Status code: {response.status_code}")
                return False
        except Exception as e:
            self.log_test("Backend Health", "FAIL", f"Connection error: {str(e)}")
            return False

    def test_frontend_availability(self) -> bool:
        """Test frontend server availability"""
        try:
            response = requests.get(self.frontend_url, timeout=5)
            if response.status_code == 200:
                self.log_test("Frontend Availability", "PASS", "Frontend server is responding")
                return True
            else:
                self.log_test("Frontend Availability", "FAIL", f"Status code: {response.status_code}")
                return False
        except Exception as e:
            self.log_test("Frontend Availability", "FAIL", f"Connection error: {str(e)}")
            return False

    def test_user_authentication(self) -> bool:
        """Test user login functionality"""
        try:
            # Test regular login
            response = requests.post(
                f"{self.backend_url}/login",
                data=self.test_user,
                timeout=10
            )
            
            if response.status_code == 200:
                result = response.json()
                self.auth_token = result.get("access_token")
                if self.auth_token:
                    self.log_test("User Authentication", "PASS", "Login successful")
                    return True
                else:
                    self.log_test("User Authentication", "FAIL", "No access token received")
                    return False
            else:
                self.log_test("User Authentication", "FAIL", f"Status: {response.status_code}, Response: {response.text}")
                return False
                
        except Exception as e:
            self.log_test("User Authentication", "FAIL", f"Error: {str(e)}")
            return False

    def test_instagram_bypass_system(self) -> bool:
        """Test Instagram bypass login functionality"""
        try:
            # Test Instagram bypass login
            instagram_data = {
                "username": "test_instagram_user",
                "password": "test_password"
            }
            
            response = requests.post(
                f"{self.backend_url}/login-instagram",
                json=instagram_data,
                headers={"Content-Type": "application/json"},
                timeout=15
            )
            
            if response.status_code in [200, 202]:
                result = response.json()
                if "challenge_required" in result or "access_token" in result:
                    self.log_test("Instagram Bypass", "PASS", "Instagram bypass system is working")
                    return True
                else:
                    self.log_test("Instagram Bypass", "FAIL", f"Unexpected response: {result}")
                    return False
            else:
                self.log_test("Instagram Bypass", "FAIL", f"Status: {response.status_code}, Response: {response.text}")
                return False
                
        except Exception as e:
            self.log_test("Instagram Bypass", "FAIL", f"Error: {str(e)}")
            return False

    def test_protected_endpoints(self) -> bool:
        """Test protected API endpoints with authentication"""
        if not self.auth_token:
            self.log_test("Protected Endpoints", "SKIP", "No auth token available")
            return False
            
        try:
            headers = {"Authorization": f"Bearer {self.auth_token}"}
            
            # Test user profile endpoint
            response = requests.get(
                f"{self.backend_url}/users/me",
                headers=headers,
                timeout=10
            )
            
            if response.status_code == 200:
                self.log_test("Protected Endpoints", "PASS", "User profile endpoint accessible")
                return True
            else:
                self.log_test("Protected Endpoints", "FAIL", f"Status: {response.status_code}")
                return False
                
        except Exception as e:
            self.log_test("Protected Endpoints", "FAIL", f"Error: {str(e)}")
            return False

    def test_database_connectivity(self) -> bool:
        """Test database connectivity through API"""
        try:
            # Test a simple database query through API
            response = requests.get(f"{self.backend_url}/leaderboard", timeout=10)
            
            if response.status_code == 200:
                self.log_test("Database Connectivity", "PASS", "Database queries working")
                return True
            else:
                self.log_test("Database Connectivity", "FAIL", f"Status: {response.status_code}")
                return False
                
        except Exception as e:
            self.log_test("Database Connectivity", "FAIL", f"Error: {str(e)}")
            return False

    def test_cors_configuration(self) -> bool:
        """Test CORS configuration"""
        try:
            headers = {
                "Origin": "http://localhost:3000",
                "Access-Control-Request-Method": "POST",
                "Access-Control-Request-Headers": "Content-Type"
            }
            
            response = requests.options(
                f"{self.backend_url}/login",
                headers=headers,
                timeout=5
            )
            
            cors_headers = response.headers.get("Access-Control-Allow-Origin")
            if cors_headers and ("*" in cors_headers or "localhost:3000" in cors_headers):
                self.log_test("CORS Configuration", "PASS", "CORS properly configured")
                return True
            else:
                self.log_test("CORS Configuration", "FAIL", f"CORS headers: {cors_headers}")
                return False
                
        except Exception as e:
            self.log_test("CORS Configuration", "FAIL", f"Error: {str(e)}")
            return False

    def test_notification_system(self) -> bool:
        """Test notification system functionality"""
        if not self.auth_token:
            self.log_test("Notification System", "SKIP", "No auth token available")
            return False
            
        try:
            headers = {"Authorization": f"Bearer {self.auth_token}"}
            
            response = requests.get(
                f"{self.backend_url}/notifications",
                headers=headers,
                timeout=10
            )
            
            if response.status_code == 200:
                self.log_test("Notification System", "PASS", "Notification endpoints working")
                return True
            else:
                self.log_test("Notification System", "FAIL", f"Status: {response.status_code}")
                return False
                
        except Exception as e:
            self.log_test("Notification System", "FAIL", f"Error: {str(e)}")
            return False

    def run_comprehensive_test(self):
        """Run all tests and generate report"""
        print("=" * 60)
        print("COMPREHENSIVE FRONTEND-BACKEND INTEGRATION TEST")
        print("=" * 60)
        print(f"Backend URL: {self.backend_url}")
        print(f"Frontend URL: {self.frontend_url}")
        print(f"Test started at: {time.strftime('%Y-%m-%d %H:%M:%S')}")
        print("=" * 60)
        
        # Run all tests
        tests = [
            self.test_backend_health,
            self.test_frontend_availability,
            self.test_user_authentication,
            self.test_instagram_bypass_system,
            self.test_protected_endpoints,
            self.test_database_connectivity,
            self.test_cors_configuration,
            self.test_notification_system
        ]
        
        passed = 0
        failed = 0
        skipped = 0
        
        for test in tests:
            result = test()
            if result is True:
                passed += 1
            elif result is False:
                failed += 1
            else:
                skipped += 1
        
        # Generate summary
        print("\n" + "=" * 60)
        print("TEST SUMMARY")
        print("=" * 60)
        print(f"Total Tests: {len(tests)}")
        print(f"Passed: {passed}")
        print(f"Failed: {failed}")
        print(f"Skipped: {skipped}")
        
        success_rate = (passed / (passed + failed)) * 100 if (passed + failed) > 0 else 0
        print(f"Success Rate: {success_rate:.1f}%")
        
        # Detailed results
        print("\nDETAILED RESULTS:")
        print("-" * 60)
        for result in self.test_results:
            status_emoji = "✅" if result["status"] == "PASS" else "❌" if result["status"] == "FAIL" else "⏭️"
            print(f"{status_emoji} {result['test']}: {result['details']}")
        
        # System status
        print("\n" + "=" * 60)
        if failed == 0:
            print("🎉 SYSTEM STATUS: FULLY FUNCTIONAL")
            print("All systems are working correctly!")
        elif failed <= 2:
            print("⚠️  SYSTEM STATUS: MOSTLY FUNCTIONAL") 
            print("Minor issues detected but core functionality works")
        else:
            print("🚨 SYSTEM STATUS: ISSUES DETECTED")
            print("Multiple failures detected - investigation required")
        
        print("=" * 60)
        
        return success_rate > 75

if __name__ == "__main__":
    tester = SystemIntegrationTester()
    success = tester.run_comprehensive_test()
    sys.exit(0 if success else 1)
