#!/usr/bin/env python3
"""
Complete Enhanced Notification System Test
Tests task assignment, completion, level-up, and achievement notifications
"""

import requests
import json
import asyncio
import websockets
import time
from datetime import datetime

# Configuration
BASE_URL = "http://localhost:8000"
WS_URL = "ws://localhost:8000"

class CompleteNotificationTester:
    def __init__(self):
        self.token = None
        self.user_id = None
        self.headers = {}
        self.received_notifications = []
        
    def login(self):
        """Login and get authentication token"""
        print("🔐 Logging in...")
        response = requests.post(f"{BASE_URL}/login", data={
            'username': 'luvmef',
            'password': 'asgsag2'
        })
        
        if response.status_code == 200:
            data = response.json()
            self.token = data['access_token']
            self.headers = {'Authorization': f'Bearer {self.token}'}
            
            # Get user profile
            profile = requests.get(f"{BASE_URL}/profile", headers=self.headers)
            if profile.status_code == 200:
                user_data = profile.json()
                self.user_id = user_data['id']
                print(f"✅ Logged in as: {user_data['username']} (ID: {self.user_id})")
                print(f"   Current balance: {user_data['coin_balance']} coins")
                print(f"   Completed tasks: {user_data['completed_tasks']}")
                print(f"   Active tasks: {user_data['active_tasks']}")
                return True
        
        print(f"❌ Login failed: {response.text}")
        return False
    
    async def websocket_listener(self):
        """Listen for real-time notifications"""
        try:
            uri = f"{WS_URL}/ws/notifications?token={self.token}"
            
            async with websockets.connect(uri) as websocket:
                print("🔌 WebSocket connected - listening for notifications...")
                
                async for message in websocket:
                    try:
                        notification = json.loads(message)
                        self.received_notifications.append(notification)
                        
                        print(f"📡 REAL-TIME NOTIFICATION:")
                        print(f"   Type: {notification.get('type', 'unknown')}")
                        
                        if 'notification' in notification:
                            notif = notification['notification']
                            print(f"   Title: {notif.get('title', 'No title')}")
                            print(f"   Message: {notif.get('message', 'No message')}")
                            print(f"   Priority: {notif.get('priority', 'unknown')}")
                            print(f"   Category: {notif.get('category', 'unknown')}")
                        
                        print(f"   Timestamp: {notification.get('timestamp', 'unknown')}")
                        print("-" * 50)
                        
                    except json.JSONDecodeError as e:
                        print(f"❌ Failed to parse notification: {e}")
                        
        except Exception as e:
            print(f"❌ WebSocket error: {e}")
    
    def take_new_task(self):
        """Take a new task to test completion"""
        print("🎯 Taking a new task...")
        response = requests.post(f"{BASE_URL}/take-task", headers=self.headers)
        
        if response.status_code == 200:
            task_data = response.json()
            print(f"✅ Task taken successfully:")
            print(f"   Task ID: {task_data['task_id']}")
            print(f"   Order ID: {task_data['order_id']}")
            print(f"   Expires at: {task_data['expires_at']}")
            return task_data
        else:
            print(f"❌ Failed to take task: {response.text}")
            return None
    
    def complete_task(self, task_id):
        """Complete the task to trigger notifications"""
        print(f"✅ Completing task {task_id}...")
        response = requests.post(f"{BASE_URL}/complete-task", 
                                headers=self.headers, 
                                json={"task_id": task_id})
        
        if response.status_code == 200:
            result = response.json()
            print(f"✅ Task completed successfully:")
            print(f"   Message: {result.get('message', 'No message')}")
            print(f"   Coins earned: {result.get('coins_earned', 0)}")
            print(f"   New balance: {result.get('new_balance', 0)}")
            
            # Check for special achievements
            if result.get('level_up'):
                print(f"🎉 LEVEL UP! New level: {result.get('new_level')}")
            if result.get('bonus_coins'):
                print(f"🎁 Bonus coins earned: {result.get('bonus_coins')}")
            if result.get('achievement'):
                print(f"🏆 Achievement unlocked: {result.get('achievement')}")
                
            return result
        else:
            print(f"❌ Task completion failed: {response.text}")
            return None
    
    def test_daily_reward(self):
        """Test daily reward notifications"""
        print("🎁 Testing daily reward...")
        response = requests.post(f"{BASE_URL}/claim-daily-reward", headers=self.headers)
        
        if response.status_code == 200:
            reward = response.json()
            print(f"✅ Daily reward claimed:")
            print(f"   Coins awarded: {reward['coins_awarded']}")
            print(f"   Streak day: {reward['streak_day']}")
            print(f"   New balance: {reward['new_balance']}")
            return reward
        else:
            print(f"ℹ️  Daily reward: {response.text}")
            return None
    
    def get_notification_stats(self):
        """Get notification statistics"""
        response = requests.get(f"{BASE_URL}/notification-stats", headers=self.headers)
        
        if response.status_code == 200:
            stats = response.json()
            print(f"📊 Notification Stats:")
            print(f"   Total: {stats['total_notifications']}")
            print(f"   Unread: {stats['unread_count']}")
            print(f"   Types: {stats['notification_types']}")
            return stats
        else:
            print(f"❌ Stats failed: {response.text}")
            return None
    
    async def run_complete_test(self):
        """Run complete enhanced notification test"""
        print("🚀 Starting Complete Enhanced Notification System Test")
        print("=" * 60)
        
        # Login
        if not self.login():
            return
        
        print()
        
        # Start WebSocket listener
        websocket_task = asyncio.create_task(self.websocket_listener())
        await asyncio.sleep(2)  # Let WebSocket connect
        
        print("🎯 Running Enhanced Notification Test Workflow...")
        print()
        
        # Test 1: Initial stats
        print("📊 Initial notification stats:")
        initial_stats = self.get_notification_stats()
        print()
        
        await asyncio.sleep(1)
        
        # Test 2: Take a new task (if available)
        task_data = self.take_new_task()
        print()
        
        await asyncio.sleep(2)  # Wait for task assignment notifications
        
        # Test 3: Complete the task (if we got one)
        if task_data:
            completion_result = self.complete_task(task_data['task_id'])
            print()
            
            await asyncio.sleep(3)  # Wait for completion notifications
        
        # Test 4: Try daily reward
        reward_result = self.test_daily_reward()
        print()
        
        await asyncio.sleep(2)  # Wait for reward notifications
        
        # Test 5: Final stats
        print("📊 Final notification stats:")
        final_stats = self.get_notification_stats()
        print()
        
        # Test 6: Check current profile
        print("👤 Final profile:")
        profile = requests.get(f"{BASE_URL}/profile", headers=self.headers)
        if profile.status_code == 200:
            user_data = profile.json()
            print(f"   Balance: {user_data['coin_balance']} coins")
            print(f"   Completed tasks: {user_data['completed_tasks']}")
            print(f"   Active tasks: {user_data['active_tasks']}")
        print()
        
        # Summary
        print("📡 Real-time Notifications Summary:")
        if self.received_notifications:
            for i, notif in enumerate(self.received_notifications):
                notif_data = notif.get('notification', {})
                print(f"   {i+1}. {notif_data.get('title', 'No title')}")
                print(f"      Priority: {notif_data.get('priority', 'unknown')}")
                print(f"      Type: {notif.get('type', 'unknown')}")
        else:
            print("   No real-time notifications received")
        
        print()
        print(f"🎯 Test Results:")
        print(f"   - Real-time notifications: {len(self.received_notifications)}")
        print(f"   - Task assignment: {'✅ Success' if task_data else '❌ No tasks available'}")
        print(f"   - Task completion: {'✅ Success' if task_data and completion_result else '❌ No task to complete'}")
        print(f"   - Daily reward: {'✅ Success' if reward_result else 'ℹ️ Already claimed'}")
        if initial_stats and final_stats:
            print(f"   - Notification count change: {initial_stats['total_notifications']} → {final_stats['total_notifications']}")
        
        print()
        print("✅ Complete Enhanced Notification System Test Finished!")
        
        # Cancel WebSocket
        websocket_task.cancel()

def main():
    tester = CompleteNotificationTester()
    asyncio.run(tester.run_complete_test())

if __name__ == "__main__":
    main()
