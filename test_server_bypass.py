#!/usr/bin/env python3
"""
Test script to verify Instagram bypass functionality with the server running.
This script starts the server and runs API tests to verify bypass works.
"""

import asyncio
import aiohttp
import json
import time
import subprocess
import sys
import signal
import os
from pathlib import Path

# Add backend to Python path
backend_path = Path(__file__).parent / "backend"
sys.path.insert(0, str(backend_path))

class ServerBypassTester:
    def __init__(self):
        self.base_url = "http://localhost:8000"
        self.server_process = None
        self.test_results = []
        
    async def start_server(self):
        """Start the FastAPI server in background"""
        print("🚀 Starting FastAPI server...")
        
        # Change to backend directory
        backend_dir = Path(__file__).parent / "backend"
        
        # Start server process
        self.server_process = subprocess.Popen([
            sys.executable, "-m", "uvicorn", "app:app", 
            "--host", "0.0.0.0", "--port", "8000", "--reload"
        ], cwd=str(backend_dir), stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        
        # Wait for server to start
        await asyncio.sleep(3)
        
        # Check if server is running
        try:
            async with aiohttp.ClientSession() as session:
                async with session.get(f"{self.base_url}/health") as response:
                    if response.status == 200:
                        print("✅ Server started successfully!")
                        return True
        except Exception as e:
            print(f"❌ Server failed to start: {e}")
            return False
            
        return False
    
    def stop_server(self):
        """Stop the FastAPI server"""
        if self.server_process:
            print("🛑 Stopping server...")
            self.server_process.terminate()
            self.server_process.wait()
            print("✅ Server stopped")
    
    async def test_user_login_bypass(self):
        """Test that test user can login with bypass"""
        print("\n🧪 Testing user login bypass...")
        
        try:
            async with aiohttp.ClientSession() as session:
                login_data = {
                    "username": "testuser",
                    "password": "testpassword123"
                }
                
                async with session.post(f"{self.base_url}/api/users/login", json=login_data) as response:
                    result = await response.json()
                    
                    if response.status == 200 and result.get("success"):
                        print("✅ Test user login bypass: SUCCESS")
                        print(f"   User ID: {result.get('user_id')}")
                        print(f"   Bypass Mode: {result.get('bypass_mode', False)}")
                        self.test_results.append(("User Login Bypass", True, "Test user login successful"))
                        return result.get('user_id')
                    else:
                        print(f"❌ Test user login bypass: FAILED - {result}")
                        self.test_results.append(("User Login Bypass", False, str(result)))
                        return None
                        
        except Exception as e:
            print(f"❌ Test user login bypass: ERROR - {e}")
            self.test_results.append(("User Login Bypass", False, str(e)))
            return None
    
    async def test_instagram_connection_bypass(self, user_id):
        """Test Instagram connection with bypass"""
        print("\n🧪 Testing Instagram connection bypass...")
        
        try:
            async with aiohttp.ClientSession() as session:
                connection_data = {
                    "username": "testuser",
                    "password": "testpassword123"
                }
                
                async with session.post(f"{self.base_url}/api/instagram/connect", json=connection_data) as response:
                    result = await response.json()
                    
                    if response.status == 200 and result.get("success"):
                        print("✅ Instagram connection bypass: SUCCESS")
                        print(f"   Test Mode: {result.get('test_mode', False)}")
                        print(f"   Message: {result.get('message')}")
                        self.test_results.append(("Instagram Connection Bypass", True, "Connection successful"))
                        return True
                    else:
                        print(f"❌ Instagram connection bypass: FAILED - {result}")
                        self.test_results.append(("Instagram Connection Bypass", False, str(result)))
                        return False
                        
        except Exception as e:
            print(f"❌ Instagram connection bypass: ERROR - {e}")
            self.test_results.append(("Instagram Connection Bypass", False, str(e)))
            return False
    
    async def test_instagram_like_bypass(self, user_id):
        """Test Instagram like action with bypass"""
        print("\n🧪 Testing Instagram like action bypass...")
        
        try:
            async with aiohttp.ClientSession() as session:
                like_data = {
                    "user_id": user_id,
                    "post_url": "https://www.instagram.com/p/test_post_123/",
                    "task_id": 1
                }
                
                async with session.post(f"{self.base_url}/api/instagram/like", json=like_data) as response:
                    result = await response.json()
                    
                    if response.status == 200 and result.get("success"):
                        print("✅ Instagram like bypass: SUCCESS")
                        print(f"   Test Mode: {result.get('test_mode', False)}")
                        print(f"   Message: {result.get('message')}")
                        self.test_results.append(("Instagram Like Bypass", True, "Like action successful"))
                        return True
                    else:
                        print(f"❌ Instagram like bypass: FAILED - {result}")
                        self.test_results.append(("Instagram Like Bypass", False, str(result)))
                        return False
                        
        except Exception as e:
            print(f"❌ Instagram like bypass: ERROR - {e}")
            self.test_results.append(("Instagram Like Bypass", False, str(e)))
            return False
    
    async def test_instagram_follow_bypass(self, user_id):
        """Test Instagram follow action with bypass"""
        print("\n🧪 Testing Instagram follow action bypass...")
        
        try:
            async with aiohttp.ClientSession() as session:
                follow_data = {
                    "user_id": user_id,
                    "target_username": "target_test_user",
                    "task_id": 2
                }
                
                async with session.post(f"{self.base_url}/api/instagram/follow", json=follow_data) as response:
                    result = await response.json()
                    
                    if response.status == 200 and result.get("success"):
                        print("✅ Instagram follow bypass: SUCCESS")
                        print(f"   Test Mode: {result.get('test_mode', False)}")
                        print(f"   Message: {result.get('message')}")
                        self.test_results.append(("Instagram Follow Bypass", True, "Follow action successful"))
                        return True
                    else:
                        print(f"❌ Instagram follow bypass: FAILED - {result}")
                        self.test_results.append(("Instagram Follow Bypass", False, str(result)))
                        return False
                        
        except Exception as e:
            print(f"❌ Instagram follow bypass: ERROR - {e}")
            self.test_results.append(("Instagram Follow Bypass", False, str(e)))
            return False
    
    async def test_normal_user_validation(self):
        """Test that normal users still require real Instagram credentials"""
        print("\n🧪 Testing normal user validation (should fail)...")
        
        try:
            async with aiohttp.ClientSession() as session:
                connection_data = {
                    "username": "normal_user",
                    "password": "normal_password"
                }
                
                async with session.post(f"{self.base_url}/api/instagram/connect", json=connection_data) as response:
                    result = await response.json()
                    
                    if response.status != 200 or not result.get("success"):
                        print("✅ Normal user validation: SUCCESS (correctly rejected)")
                        print(f"   Error: {result.get('error', 'Unknown error')}")
                        self.test_results.append(("Normal User Validation", True, "Correctly rejected non-test user"))
                        return True
                    else:
                        print(f"❌ Normal user validation: FAILED (should have been rejected) - {result}")
                        self.test_results.append(("Normal User Validation", False, "Normal user was incorrectly accepted"))
                        return False
                        
        except Exception as e:
            print(f"❌ Normal user validation: ERROR - {e}")
            self.test_results.append(("Normal User Validation", False, str(e)))
            return False
    
    def print_results(self):
        """Print comprehensive test results"""
        print("\n" + "="*60)
        print("🎯 INSTAGRAM BYPASS TEST RESULTS")
        print("="*60)
        
        passed = 0
        total = len(self.test_results)
        
        for test_name, success, details in self.test_results:
            status = "✅ PASS" if success else "❌ FAIL"
            print(f"{status} {test_name}")
            print(f"     Details: {details}")
            if success:
                passed += 1
        
        print("\n" + "-"*60)
        print(f"📊 SUMMARY: {passed}/{total} tests passed ({passed/total*100:.1f}%)")
        
        if passed == total:
            print("🎉 ALL TESTS PASSED! Instagram bypass system is working correctly.")
        else:
            print("⚠️  Some tests failed. Check the details above.")
        
        print("="*60)
    
    async def run_all_tests(self):
        """Run comprehensive bypass tests"""
        print("🧪 INSTAGRAM BYPASS COMPREHENSIVE TEST")
        print("="*50)
        
        try:
            # Start server
            if not await self.start_server():
                print("❌ Failed to start server. Aborting tests.")
                return
            
            # Test user login
            user_id = await self.test_user_login_bypass()
            if not user_id:
                print("❌ Cannot proceed without successful user login")
                return
            
            # Test Instagram connection
            await self.test_instagram_connection_bypass(user_id)
            
            # Test Instagram actions
            await self.test_instagram_like_bypass(user_id)
            await self.test_instagram_follow_bypass(user_id)
            
            # Test normal user validation
            await self.test_normal_user_validation()
            
            # Print results
            self.print_results()
            
        except KeyboardInterrupt:
            print("\n🛑 Tests interrupted by user")
        except Exception as e:
            print(f"❌ Unexpected error during tests: {e}")
        finally:
            # Always stop server
            self.stop_server()

async def main():
    """Main test function"""
    tester = ServerBypassTester()
    await tester.run_all_tests()

if __name__ == "__main__":
    # Set up signal handler for graceful shutdown
    def signal_handler(sig, frame):
        print("\n🛑 Received interrupt signal. Shutting down...")
        sys.exit(0)
    
    signal.signal(signal.SIGINT, signal_handler)
    
    # Run tests
    asyncio.run(main())
