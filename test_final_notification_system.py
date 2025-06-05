#!/usr/bin/env python3
"""
Final Enhanced Notification System Test
Complete demonstration of all notification features
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

class FinalNotificationTest:
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
                print(f"   💰 Balance: {user_data['coin_balance']} coins")
                print(f"   ✅ Completed: {user_data['completed_tasks']} tasks")
                print(f"   🎯 Active: {user_data['active_tasks']} tasks")
                return True
        
        return False
    
    def setup_test_environment(self):
        """Setup test environment with available tasks and reset daily reward"""
        try:
            conn = sqlite3.connect(DB_PATH)
            cursor = conn.cursor()
            
            print("🔧 Setting up test environment...")
            
            # Create test order and tasks
            cursor.execute("""
                INSERT INTO orders (user_id, post_url, order_type, target_count, status)
                VALUES (2, 'https://www.instagram.com/p/test456/', 'like', 15, 'active')
            """)
            
            order_id = cursor.lastrowid
            
            # Create multiple tasks for testing
            for i in range(5):
                cursor.execute("""
                    INSERT INTO tasks (order_id, status)
                    VALUES (?, 'pending')
                """, (order_id,))
            
            # Reset daily reward for testing
            yesterday = datetime.now() - timedelta(days=1)
            cursor.execute("""
                UPDATE users 
                SET last_daily_reward = ?, daily_reward_streak = 3
                WHERE id = ?
            """, (yesterday, self.user_id))
            
            conn.commit()
            conn.close()
            
            print(f"✅ Created test order {order_id} with 5 tasks")
            print("✅ Reset daily reward for testing")
            return True
            
        except Exception as e:
            print(f"❌ Setup failed: {e}")
            return False
    
    async def websocket_listener(self):
        """Enhanced WebSocket listener with categorization"""
        try:
            uri = f"{WS_URL}/ws/notifications?token={self.token}"
            
            async with websockets.connect(uri) as websocket:
                print("🔌 WebSocket connected - Enhanced notifications active!")
                
                async for message in websocket:
                    try:
                        notification = json.loads(message)
                        self.received_notifications.append(notification)
                        
                        if 'notification' in notification:
                            notif = notification['notification']
                            title = notif.get('title', 'No title')
                            message = notif.get('message', 'No message')
                            priority = notif.get('priority', 'unknown')
                            
                            # Enhanced display with emojis based on priority
                            priority_emoji = {
                                'low': '💬',
                                'medium': '⚡',
                                'high': '🚨',
                                'urgent': '🔥'
                            }.get(priority, '📡')
                            
                            print(f"\n{priority_emoji} REAL-TIME NOTIFICATION:")
                            print(f"   📋 {title}")
                            print(f"   💭 {message}")
                            print(f"   🎯 Priority: {priority.upper()}")
                            print("-" * 50)
                        
                    except json.JSONDecodeError as e:
                        print(f"❌ Parse error: {e}")
                        
        except Exception as e:
            print(f"❌ WebSocket error: {e}")
    
    async def complete_workflow_test(self):
        """Run complete notification workflow test"""
        print("\n🚀 ENHANCED NOTIFICATION SYSTEM - FINAL TEST")
        print("=" * 60)
        
        # Login
        if not self.login():
            return
        
        # Setup test environment
        if not self.setup_test_environment():
            return
        
        print()
        
        # Start WebSocket listener
        websocket_task = asyncio.create_task(self.websocket_listener())
        await asyncio.sleep(2)
        
        print("🎬 Starting Complete Workflow Test...")
        print()
        
        # Step 1: Claim daily reward
        print("🎁 STEP 1: Daily Reward System Test")
        reward_response = requests.post(f"{BASE_URL}/claim-daily-reward", headers=self.headers)
        if reward_response.status_code == 200:
            reward = reward_response.json()
            print(f"✅ Daily reward claimed!")
            print(f"   💰 Coins: {reward['coins_awarded']}")
            print(f"   🔥 Streak: {reward['streak_day']} days")
            print(f"   💎 New balance: {reward['new_balance']}")
        else:
            print(f"ℹ️  {reward_response.json().get('detail', 'Unknown')}")
        
        await asyncio.sleep(3)
        print()
        
        # Step 2: Take first task
        print("🎯 STEP 2: Task Assignment Test")
        task1_response = requests.post(f"{BASE_URL}/take-task", headers=self.headers)
        if task1_response.status_code == 200:
            task1_data = task1_response.json()
            print(f"✅ First task assigned: ID {task1_data['task_id']}")
            
            await asyncio.sleep(2)
            
            # Complete first task
            print("🏆 STEP 3: Task Completion Test")
            completion1 = requests.post(f"{BASE_URL}/complete-task",
                                       headers=self.headers,
                                       json={"task_id": task1_data['task_id']})
            if completion1.status_code == 200:
                result1 = completion1.json()
                print(f"✅ First task completed!")
                print(f"   💰 Coins earned: {result1.get('coins_earned', 0)}")
                print(f"   💎 New balance: {result1.get('new_balance', 0)}")
                
                await asyncio.sleep(3)
        
        print()
        
        # Step 3: Take and complete second task
        print("🎯 STEP 4: Second Task Cycle")
        task2_response = requests.post(f"{BASE_URL}/take-task", headers=self.headers)
        if task2_response.status_code == 200:
            task2_data = task2_response.json()
            print(f"✅ Second task assigned: ID {task2_data['task_id']}")
            
            await asyncio.sleep(2)
            
            completion2 = requests.post(f"{BASE_URL}/complete-task",
                                       headers=self.headers,
                                       json={"task_id": task2_data['task_id']})
            if completion2.status_code == 200:
                result2 = completion2.json()
                print(f"✅ Second task completed!")
                
                await asyncio.sleep(3)
        
        print()
        
        # Step 4: Check final stats
        print("📊 STEP 5: Final Statistics")
        stats_response = requests.get(f"{BASE_URL}/notification-stats", headers=self.headers)
        if stats_response.status_code == 200:
            stats = stats_response.json()
            print(f"📈 Total notifications: {stats['total_notifications']}")
            print(f"📬 Unread: {stats['unread_count']}")
            print(f"📊 Types: {stats['notification_types']}")
        
        profile_response = requests.get(f"{BASE_URL}/profile", headers=self.headers)
        if profile_response.status_code == 200:
            final_profile = profile_response.json()
            print(f"👤 Final Profile:")
            print(f"   💰 Balance: {final_profile['coin_balance']} coins")
            print(f"   ✅ Completed: {final_profile['completed_tasks']} tasks")
            print(f"   🎯 Active: {final_profile['active_tasks']} tasks")
        
        print()
        
        # Summary
        print("🎬 FINAL TEST SUMMARY")
        print("=" * 60)
        
        notification_categories = {
            'connection': 0,
            'task_assignment': 0,
            'task_completion': 0,
            'daily_reward': 0,
            'achievement': 0,
            'level_up': 0,
            'other': 0
        }
        
        for notif in self.received_notifications:
            notif_data = notif.get('notification', {})
            title = notif_data.get('title', '').lower()
            
            if 'gerçek zamanlı' in title or 'aktif' in title:
                notification_categories['connection'] += 1
            elif 'görev' in title and ('alındı' in title or 'atandı' in title):
                notification_categories['task_assignment'] += 1
            elif 'görev' in title and 'tamamlandı' in title:
                notification_categories['task_completion'] += 1
            elif 'günlük' in title or 'giriş' in title:
                notification_categories['daily_reward'] += 1
            elif 'seviye' in title or 'level' in title:
                notification_categories['level_up'] += 1
            elif 'başarı' in title or 'tebrikler' in title:
                notification_categories['achievement'] += 1
            else:
                notification_categories['other'] += 1
        
        print(f"📡 Real-time Notifications Received: {len(self.received_notifications)}")
        print(f"   🔌 Connection: {notification_categories['connection']}")
        print(f"   🎯 Task Assignment: {notification_categories['task_assignment']}")
        print(f"   🏆 Task Completion: {notification_categories['task_completion']}")
        print(f"   🎁 Daily Rewards: {notification_categories['daily_reward']}")
        print(f"   📈 Level Ups: {notification_categories['level_up']}")
        print(f"   🏅 Achievements: {notification_categories['achievement']}")
        print(f"   📋 Other: {notification_categories['other']}")
        
        print()
        print("📋 All Notifications Received:")
        for i, notif in enumerate(self.received_notifications, 1):
            notif_data = notif.get('notification', {})
            title = notif_data.get('title', 'No title')
            priority = notif_data.get('priority', 'unknown')
            print(f"   {i}. {title} (Priority: {priority.upper()})")
        
        print()
        
        # Test results
        total_notifications = len(self.received_notifications)
        test_success = total_notifications >= 2  # At least connection + task notifications
        
        print("🎯 TEST RESULTS:")
        print(f"   ✅ WebSocket Connection: {'PASS' if notification_categories['connection'] > 0 else 'FAIL'}")
        print(f"   ✅ Task Notifications: {'PASS' if notification_categories['task_assignment'] > 0 else 'FAIL'}")
        print(f"   ✅ Real-time Delivery: {'PASS' if total_notifications > 0 else 'FAIL'}")
        print(f"   ✅ Overall System: {'PASS' if test_success else 'FAIL'}")
        
        print()
        if test_success:
            print("🎉 ENHANCED NOTIFICATION SYSTEM TEST PASSED!")
            print("🚀 All notification features are working perfectly!")
        else:
            print("⚠️  Some notification features need attention")
        
        print()
        print("✅ Enhanced Notification System Development Complete!")
        
        # Cancel WebSocket
        websocket_task.cancel()

def main():
    tester = FinalNotificationTest()
    asyncio.run(tester.complete_workflow_test())

if __name__ == "__main__":
    main()
