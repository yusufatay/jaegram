#!/usr/bin/env python3
"""
Test Task Completion and Level-up Notifications
Simulates task completion to test enhanced notifications
"""

import requests
import json
import asyncio
import websockets
import sqlite3
from datetime import datetime, timedelta

# Configuration
BASE_URL = "http://localhost:8000"
WS_URL = "ws://localhost:8000"
DB_PATH = "/home/mirza/Desktop/instagram_puan_iskelet/backend/instagram_platform.db"

class TaskCompletionTester:
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
    
    def simulate_task_completion_in_db(self):
        """Directly mark an active task as completed in database to trigger notifications"""
        try:
            conn = sqlite3.connect(DB_PATH)
            cursor = conn.cursor()
            
            # Find an active task for the user
            cursor.execute("""
                SELECT id, order_id FROM tasks 
                WHERE assigned_user_id = ? AND status = 'assigned'
                LIMIT 1
            """, (self.user_id,))
            
            task = cursor.fetchone()
            if not task:
                print("❌ No active tasks found to complete")
                return None
            
            task_id, order_id = task
            print(f"🎯 Found active task: ID {task_id}, Order ID {order_id}")
            
            # Mark task as completed
            cursor.execute("""
                UPDATE tasks 
                SET status = 'completed', completed_at = ?
                WHERE id = ?
            """, (datetime.now(), task_id))
            
            conn.commit()
            conn.close()
            
            print(f"✅ Task {task_id} marked as completed in database")
            return {'task_id': task_id, 'order_id': order_id}
            
        except Exception as e:
            print(f"❌ Database error: {e}")
            return None
    
    def trigger_task_completion_api(self, task_id, order_id):
        """Call task completion API to trigger enhanced notifications"""
        print(f"📡 Triggering task completion API for task {task_id}...")
        
        # The correct way to call the complete-task endpoint
        response = requests.post(f"{BASE_URL}/complete-task", 
                                headers=self.headers, 
                                json={"task_id": task_id})
        
        if response.status_code == 200:
            result = response.json()
            print("✅ Task completion API triggered successfully:")
            print(f"   Message: {result.get('message', 'No message')}")
            return result
        else:
            print(f"❌ Task completion API failed: {response.text}")
            return None
    
    def reset_daily_reward(self):
        """Reset daily reward claim time to allow testing"""
        try:
            conn = sqlite3.connect(DB_PATH)
            cursor = conn.cursor()
            
            # Set last_daily_reward to yesterday
            yesterday = datetime.now() - timedelta(days=1)
            cursor.execute("""
                UPDATE users 
                SET last_daily_reward = ?
                WHERE id = ?
            """, (yesterday, self.user_id))
            
            conn.commit()
            conn.close()
            print("✅ Daily reward reset - can claim again")
            return True
            
        except Exception as e:
            print(f"❌ Failed to reset daily reward: {e}")
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
    
    async def run_task_completion_test(self):
        """Run complete task completion test with notifications"""
        print("🚀 Starting Task Completion Notification Test")
        print("=" * 60)
        
        # Login
        if not self.login():
            return
        
        print()
        
        # Start WebSocket listener
        websocket_task = asyncio.create_task(self.websocket_listener())
        await asyncio.sleep(2)  # Let WebSocket connect
        
        print("🎯 Testing Task Completion Workflow...")
        print()
        
        # Reset daily reward for testing
        self.reset_daily_reward()
        print()
        
        # Test daily reward first
        print("🎁 Testing daily reward notifications...")
        reward_response = requests.post(f"{BASE_URL}/claim-daily-reward", headers=self.headers)
        if reward_response.status_code == 200:
            reward = reward_response.json()
            print(f"✅ Daily reward claimed: {reward['coins_awarded']} coins")
        else:
            print(f"ℹ️  Daily reward: {reward_response.text}")
        
        await asyncio.sleep(2)  # Wait for notifications
        print()
        
        # Simulate task completion
        print("🔧 Simulating task completion...")
        task_info = self.simulate_task_completion_in_db()
        
        if task_info:
            await asyncio.sleep(1)
            
            # Trigger completion notifications via API
            completion_result = self.trigger_task_completion_api(
                task_info['task_id'], 
                task_info['order_id']
            )
            
            await asyncio.sleep(3)  # Wait for all notifications
        
        print()
        
        # Check final profile
        print("👤 Final profile check...")
        profile = requests.get(f"{BASE_URL}/profile", headers=self.headers)
        if profile.status_code == 200:
            user_data = profile.json()
            print(f"   New balance: {user_data['coin_balance']} coins")
            print(f"   Completed tasks: {user_data['completed_tasks']}")
            print(f"   Active tasks: {user_data['active_tasks']}")
        
        print()
        
        # Summary
        print("📡 Real-time Notifications Received:")
        if self.received_notifications:
            for i, notif in enumerate(self.received_notifications):
                print(f"   {i+1}. Type: {notif.get('type', 'unknown')}")
                if 'notification' in notif:
                    n = notif['notification']
                    print(f"      Title: {n.get('title', 'No title')}")
                    print(f"      Priority: {n.get('priority', 'unknown')}")
        else:
            print("   No notifications received")
        
        print()
        print(f"✅ Task Completion Test Complete! ({len(self.received_notifications)} notifications)")
        
        # Cancel WebSocket
        websocket_task.cancel()

def main():
    tester = TaskCompletionTester()
    asyncio.run(tester.run_task_completion_test())

if __name__ == "__main__":
    main()
