#!/usr/bin/env python3
"""
Enhanced Notification System - Complete Workflow Test
Tests real-time notifications, task completion workflow, and notification statistics
"""

import requests
import json
import asyncio
import websockets
import time
from datetime import datetime
import threading

# Configuration
BASE_URL = "http://localhost:8000"
WS_URL = "ws://localhost:8000"

class NotificationWorkflowTester:
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
            
            # Get user profile to get user_id
            profile = requests.get(f"{BASE_URL}/profile", headers=self.headers)
            if profile.status_code == 200:
                user_data = profile.json()
                self.user_id = user_data['id']
                print(f"✅ Logged in as: {user_data['username']} (ID: {self.user_id})")
                print(f"   Current balance: {user_data['coin_balance']} coins")
                return True
        
        print(f"❌ Login failed: {response.text}")
        return False
    
    async def websocket_listener(self):
        """Listen for real-time notifications via WebSocket"""
        try:
            uri = f"{WS_URL}/ws/notifications?token={self.token}"
            print(f"🔌 Connecting to WebSocket: {uri}")
            
            async with websockets.connect(uri) as websocket:
                print("✅ WebSocket connected - listening for real-time notifications...")
                
                async for message in websocket:
                    try:
                        notification = json.loads(message)
                        self.received_notifications.append(notification)
                        print(f"📡 Real-time notification received:")
                        print(f"   Type: {notification.get('type', 'unknown')}")
                        
                        if 'notification' in notification:
                            notif = notification['notification']
                            print(f"   Title: {notif.get('title', 'No title')}")
                            print(f"   Message: {notif.get('message', 'No message')}")
                            print(f"   Priority: {notif.get('priority', 'unknown')}")
                        
                        print(f"   Timestamp: {notification.get('timestamp', 'unknown')}")
                        print()
                        
                    except json.JSONDecodeError as e:
                        print(f"❌ Failed to parse WebSocket message: {e}")
                        print(f"   Raw message: {message}")
                        
        except Exception as e:
            print(f"❌ WebSocket error: {e}")
    
    def test_notification_stats(self):
        """Test notification statistics endpoint"""
        print("📊 Testing notification statistics...")
        response = requests.get(f"{BASE_URL}/notification-stats", headers=self.headers)
        
        if response.status_code == 200:
            stats = response.json()
            print("✅ Notification stats retrieved:")
            print(f"   Total notifications: {stats['total_notifications']}")
            print(f"   Unread count: {stats['unread_count']}")
            print(f"   Last notification: {stats['last_notification']}")
            print(f"   Types breakdown: {stats['notification_types']}")
            return stats
        else:
            print(f"❌ Stats failed: {response.text}")
            return None
    
    def test_task_assignment(self):
        """Test task assignment with enhanced notifications"""
        print("🎯 Testing task assignment...")
        response = requests.post(f"{BASE_URL}/take-task", headers=self.headers)
        
        if response.status_code == 200:
            task_data = response.json()
            print("✅ Task assigned successfully:")
            print(f"   Task ID: {task_data['task_id']}")
            print(f"   Order ID: {task_data['order_id']}")
            print(f"   Expires at: {task_data['expires_at']}")
            return task_data
        else:
            print(f"ℹ️  Task assignment: {response.text}")
            return None
    
    def test_daily_reward_simulation(self):
        """Simulate daily reward with enhanced notifications"""
        print("🎁 Testing daily reward system...")
        
        # First check current status
        status_response = requests.get(f"{BASE_URL}/daily-reward-status", headers=self.headers)
        if status_response.status_code == 200:
            status = status_response.json()
            print(f"   Current status: Can claim = {status.get('can_claim', False)}")
            print(f"   Current streak: {status.get('streak', 0)}")
            print(f"   Next reward: {status.get('next_reward', 0)} coins")
        
        # Try to claim reward
        reward_response = requests.post(f"{BASE_URL}/claim-daily-reward", headers=self.headers)
        
        if reward_response.status_code == 200:
            reward = reward_response.json()
            print("✅ Daily reward claimed:")
            print(f"   Coins awarded: {reward['coins_awarded']}")
            print(f"   Streak day: {reward['streak_day']}")
            print(f"   New balance: {reward['new_balance']}")
            print(f"   Message: {reward['message']}")
            return reward
        else:
            print(f"ℹ️  Daily reward status: {reward_response.text}")
            return None
    
    def test_notifications_history(self):
        """Check notification history"""
        print("📋 Checking notification history...")
        response = requests.get(f"{BASE_URL}/notifications", headers=self.headers)
        
        if response.status_code == 200:
            notifications = response.json()
            print(f"✅ Found {len(notifications)} notifications in history")
            
            # Show recent notifications
            for i, notif in enumerate(notifications[:3]):
                print(f"   {i+1}. {notif['message']}")
                print(f"      Type: {notif.get('type', 'unknown')} | Read: {notif.get('read', False)}")
                print(f"      Created: {notif['created_at']}")
            
            return notifications
        else:
            print(f"❌ Notifications failed: {response.text}")
            return []
    
    def test_create_order_with_notifications(self):
        """Test order creation which should trigger enhanced notifications"""
        print("📦 Testing order creation with notifications...")
        
        # Create a test order (this requires Instagram session, so it will likely fail)
        order_data = {
            "post_url": "https://www.instagram.com/p/test123/",
            "order_type": "like",
            "target_count": 5
        }
        
        response = requests.post(f"{BASE_URL}/create-order", headers=self.headers, json=order_data)
        
        if response.status_code == 200:
            order = response.json()
            print("✅ Order created successfully:")
            print(f"   Order ID: {order['order_id']}")
            print(f"   Message: {order['message']}")
            return order
        else:
            print(f"ℹ️  Order creation: {response.text}")
            return None
    
    async def run_complete_test(self):
        """Run complete notification workflow test"""
        print("🚀 Starting Enhanced Notification System Workflow Test")
        print("=" * 60)
        
        # Login first
        if not self.login():
            return
        
        print()
        
        # Start WebSocket listener in background
        websocket_task = asyncio.create_task(self.websocket_listener())
        
        # Give WebSocket time to connect
        await asyncio.sleep(2)
        
        print("📈 Running notification workflow tests...")
        print()
        
        # Test 1: Initial stats
        initial_stats = self.test_notification_stats()
        print()
        
        # Test 2: Task assignment
        task_data = self.test_task_assignment()
        print()
        
        # Wait a bit for real-time notifications
        await asyncio.sleep(1)
        
        # Test 3: Daily reward
        reward_data = self.test_daily_reward_simulation()
        print()
        
        # Wait a bit for real-time notifications
        await asyncio.sleep(1)
        
        # Test 4: Order creation
        order_data = self.test_create_order_with_notifications()
        print()
        
        # Wait a bit for real-time notifications
        await asyncio.sleep(1)
        
        # Test 5: Check notification history
        notifications = self.test_notifications_history()
        print()
        
        # Test 6: Final stats
        print("📊 Final notification statistics:")
        final_stats = self.test_notification_stats()
        print()
        
        # Summary of real-time notifications received
        print("📡 Real-time Notifications Received via WebSocket:")
        if self.received_notifications:
            for i, notif in enumerate(self.received_notifications):
                print(f"   {i+1}. Type: {notif.get('type', 'unknown')}")
                if 'notification' in notif:
                    n = notif['notification']
                    print(f"      Title: {n.get('title', 'No title')}")
                    print(f"      Message: {n.get('message', 'No message')}")
        else:
            print("   No real-time notifications received")
        
        print()
        print("🎯 Test Summary:")
        print(f"   - WebSocket notifications received: {len(self.received_notifications)}")
        if initial_stats and final_stats:
            print(f"   - Notification count change: {initial_stats['total_notifications']} → {final_stats['total_notifications']}")
        print(f"   - Task assignment: {'✅ Success' if task_data else '❌ Failed'}")
        print(f"   - Daily reward: {'✅ Success' if reward_data else 'ℹ️ Already claimed'}")
        print(f"   - Order creation: {'✅ Success' if order_data else 'ℹ️ Requires Instagram'}")
        
        print()
        print("✅ Enhanced Notification System Workflow Test Complete!")
        
        # Cancel WebSocket task
        websocket_task.cancel()

def main():
    """Main test function"""
    tester = NotificationWorkflowTester()
    asyncio.run(tester.run_complete_test())

if __name__ == "__main__":
    main()
