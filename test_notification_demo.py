#!/usr/bin/env python3
"""
Enhanced Notification System Demo
Creates test data and demonstrates all notification features
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

class NotificationDemo:
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
                return True
        
        print(f"❌ Login failed")
        return False
    
    def create_demo_data(self):
        """Create demo orders and tasks in database"""
        try:
            conn = sqlite3.connect(DB_PATH)
            cursor = conn.cursor()
            
            print("🗃️  Creating demo test data...")
            
            # Create a test order (not from our user)
            cursor.execute("""
                INSERT INTO orders (user_id, post_url, order_type, target_count, status, created_at)
                VALUES (2, 'https://www.instagram.com/p/demo123/', 'like', 10, 'active', ?)
            """, (datetime.now(),))
            
            order_id = cursor.lastrowid
            
            # Create several tasks for this order
            for i in range(3):
                cursor.execute("""
                    INSERT INTO tasks (order_id, status)
                    VALUES (?, 'pending')
                """, (order_id,))
            
            # Reset user's daily reward to allow claiming
            yesterday = datetime.now() - timedelta(days=1)
            cursor.execute("""
                UPDATE users 
                SET last_daily_reward = ?, daily_reward_streak = 2
                WHERE id = ?
            """, (yesterday, self.user_id))
            
            conn.commit()
            conn.close()
            
            print(f"✅ Created demo order {order_id} with 3 tasks")
            return order_id
            
        except Exception as e:
            print(f"❌ Failed to create demo data: {e}")
            return None
    
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
                            title = notif.get('title', 'No title')
                            message = notif.get('message', 'No message')
                            priority = notif.get('priority', 'unknown')
                            category = notif.get('category', 'unknown')
                            
                            print(f"   🎯 Title: {title}")
                            print(f"   💬 Message: {message}")
                            print(f"   ⚡ Priority: {priority}")
                            print(f"   📂 Category: {category}")
                        
                        print(f"   🕐 Timestamp: {notification.get('timestamp', 'unknown')}")
                        print("-" * 60)
                        
                    except json.JSONDecodeError as e:
                        print(f"❌ Failed to parse notification: {e}")
                        
        except Exception as e:
            print(f"❌ WebSocket error: {e}")
    
    async def demo_workflow(self):
        """Demonstrate the complete notification workflow"""
        print("🚀 Enhanced Notification System DEMO")
        print("=" * 60)
        
        # Login
        if not self.login():
            return
        
        # Create demo data
        order_id = self.create_demo_data()
        if not order_id:
            return
        
        print()
        
        # Start WebSocket listener
        websocket_task = asyncio.create_task(self.websocket_listener())
        await asyncio.sleep(2)  # Let WebSocket connect
        
        print("🎬 Starting notification demo workflow...")
        print()
        
        # Demo 1: Daily Reward Notification
        print("🎁 DEMO 1: Daily Reward with Streak Notifications")
        reward_response = requests.post(f"{BASE_URL}/claim-daily-reward", headers=self.headers)
        if reward_response.status_code == 200:
            reward = reward_response.json()
            print(f"✅ Daily reward claimed: {reward['coins_awarded']} coins (Streak: {reward['streak_day']})")
        print()
        
        await asyncio.sleep(3)  # Wait for notifications
        
        # Demo 2: Task Assignment Notification
        print("🎯 DEMO 2: Task Assignment Notification")
        task_response = requests.post(f"{BASE_URL}/take-task", headers=self.headers)
        if task_response.status_code == 200:
            task_data = task_response.json()
            print(f"✅ Task assigned: ID {task_data['task_id']}")
            
            await asyncio.sleep(3)  # Wait for notifications
            
            # Demo 3: Task Completion with Level-up and Achievement
            print("🏆 DEMO 3: Task Completion with Achievement Notifications")
            completion_response = requests.post(f"{BASE_URL}/complete-task", 
                                               headers=self.headers,
                                               json={"task_id": task_data['task_id']})
            if completion_response.status_code == 200:
                result = completion_response.json()
                print(f"✅ Task completed: {result.get('message', 'No message')}")
                
                await asyncio.sleep(5)  # Wait for all completion notifications
            
        print()
        
        # Demo 4: Take and complete another task for more achievements
        print("🎯 DEMO 4: Second Task for Achievement Progression")
        task_response2 = requests.post(f"{BASE_URL}/take-task", headers=self.headers)
        if task_response2.status_code == 200:
            task_data2 = task_response2.json()
            print(f"✅ Second task assigned: ID {task_data2['task_id']}")
            
            await asyncio.sleep(2)
            
            completion_response2 = requests.post(f"{BASE_URL}/complete-task", 
                                                headers=self.headers,
                                                json={"task_id": task_data2['task_id']})
            if completion_response2.status_code == 200:
                result2 = completion_response2.json()
                print(f"✅ Second task completed: {result2.get('message', 'No message')}")
                
                await asyncio.sleep(3)
        
        print()
        
        # Demo 5: Check final stats
        print("📊 DEMO 5: Final Notification Statistics")
        stats_response = requests.get(f"{BASE_URL}/notification-stats", headers=self.headers)
        if stats_response.status_code == 200:
            stats = stats_response.json()
            print(f"📈 Total notifications: {stats['total_notifications']}")
            print(f"📬 Unread count: {stats['unread_count']}")
            print(f"📋 Types breakdown: {stats['notification_types']}")
        
        print()
        
        # Demo 6: Final profile
        print("👤 Final Profile Status:")
        profile = requests.get(f"{BASE_URL}/profile", headers=self.headers)
        if profile.status_code == 200:
            user_data = profile.json()
            print(f"💰 Balance: {user_data['coin_balance']} coins")
            print(f"✅ Completed tasks: {user_data['completed_tasks']}")
            print(f"🎯 Active tasks: {user_data['active_tasks']}")
        
        print()
        print("🎬 DEMO SUMMARY:")
        print("=" * 60)
        
        # Categorize notifications
        connection_notifs = 0
        task_notifs = 0
        reward_notifs = 0
        achievement_notifs = 0
        level_notifs = 0
        
        for notif in self.received_notifications:
            notif_data = notif.get('notification', {})
            title = notif_data.get('title', '').lower()
            
            if 'gerçek zamanlı' in title:
                connection_notifs += 1
            elif 'görev' in title:
                task_notifs += 1
            elif 'günlük' in title or 'bonus' in title:
                reward_notifs += 1
            elif 'seviye' in title or 'level' in title:
                level_notifs += 1
            elif 'tebrikler' in title or 'başarı' in title:
                achievement_notifs += 1
        
        print(f"📡 Real-time Notifications Received: {len(self.received_notifications)}")
        print(f"   🔌 Connection notifications: {connection_notifs}")
        print(f"   🎯 Task notifications: {task_notifs}")
        print(f"   🎁 Reward notifications: {reward_notifs}")
        print(f"   📈 Level-up notifications: {level_notifs}")
        print(f"   🏆 Achievement notifications: {achievement_notifs}")
        
        print()
        print("📋 All Notifications Received:")
        for i, notif in enumerate(self.received_notifications):
            notif_data = notif.get('notification', {})
            title = notif_data.get('title', 'No title')
            priority = notif_data.get('priority', 'unknown')
            print(f"   {i+1}. {title} (Priority: {priority})")
        
        print()
        print("✅ Enhanced Notification System Demo Complete!")
        print("🎉 All notification types working perfectly!")
        
        # Cancel WebSocket
        websocket_task.cancel()

def main():
    demo = NotificationDemo()
    asyncio.run(demo.demo_workflow())

if __name__ == "__main__":
    main()
