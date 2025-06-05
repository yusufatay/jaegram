#!/usr/bin/env python3
"""
Debug script for daily reward system issues
"""

import requests
import json
import sqlite3
from datetime import datetime, timedelta

BASE_URL = "http://localhost:8000"
DB_PATH = "/home/mirza/Desktop/instagram_puan_iskelet/instagram_platform.db"

def reset_daily_reward_for_user(user_id=10):
    """Reset daily reward to allow testing"""
    try:
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        
        # Delete today's reward record
        today = datetime.now().date()
        cursor.execute("DELETE FROM daily_rewards WHERE user_id = ? AND claimed_date = ?", (user_id, today))
        
        # Set last_daily_reward to yesterday
        yesterday = datetime.now() - timedelta(days=1)
        cursor.execute("UPDATE users SET last_daily_reward = ? WHERE id = ?", (yesterday, user_id))
        
        conn.commit()
        conn.close()
        print(f"✅ Reset daily reward for user {user_id}")
        return True
    except Exception as e:
        print(f"❌ Failed to reset daily reward: {e}")
        return False

def get_user_balance(user_id=10):
    """Get current user balance from database"""
    try:
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        
        cursor.execute("SELECT coin_balance FROM users WHERE id = ?", (user_id,))
        result = cursor.fetchone()
        conn.close()
        
        if result:
            return result[0] or 0
        return 0
    except Exception as e:
        print(f"❌ Failed to get user balance: {e}")
        return 0

def get_token():
    """Get authentication token"""
    try:
        # Try to login with test user
        login_data = {"username": "test_user", "password": "test123"}
        response = requests.post(f"{BASE_URL}/login", data=login_data)
        
        if response.status_code == 200:
            token_data = response.json()
            return token_data["access_token"]
        else:
            print(f"❌ Login failed: {response.text}")
            return None
    except Exception as e:
        print(f"❌ Login error: {e}")
        return None

def test_daily_reward_status(token):
    """Test daily reward status endpoint"""
    print("\n🔍 Testing daily reward status...")
    
    headers = {"Authorization": f"Bearer {token}"}
    response = requests.get(f"{BASE_URL}/daily-reward-status", headers=headers)
    
    if response.status_code == 200:
        data = response.json()
        print("✅ Daily reward status response:")
        print(json.dumps(data, indent=2))
        return data
    else:
        print(f"❌ Status check failed: {response.status_code} - {response.text}")
        return None

def test_daily_reward_claim(token):
    """Test daily reward claim endpoint"""
    print("\n🎁 Testing daily reward claim...")
    
    # Get balance before claim
    balance_before = get_user_balance()
    print(f"💰 Balance before claim: {balance_before}")
    
    headers = {"Authorization": f"Bearer {token}"}
    response = requests.post(f"{BASE_URL}/claim-daily-reward", headers=headers)
    
    print(f"📡 Response status: {response.status_code}")
    
    if response.status_code == 200:
        data = response.json()
        print("✅ Daily reward claim response:")
        print(json.dumps(data, indent=2))
        
        # Check balance after claim
        balance_after = get_user_balance()
        print(f"💰 Balance after claim: {balance_after}")
        print(f"💰 Balance difference: {balance_after - balance_before}")
        
        return data
    else:
        print(f"❌ Claim failed: {response.status_code} - {response.text}")
        return None

def check_database_records():
    """Check daily_rewards table records"""
    print("\n🗄️ Checking database records...")
    
    try:
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        
        # Check daily_rewards table
        cursor.execute("SELECT * FROM daily_rewards ORDER BY claimed_date DESC LIMIT 5")
        daily_rewards = cursor.fetchall()
        
        print("📊 Recent daily_rewards records:")
        for reward in daily_rewards:
            print(f"   User: {reward[1]}, Amount: {reward[2]}, Days: {reward[3]}, Date: {reward[4]}")
        
        # Check coin_transactions table
        cursor.execute("SELECT * FROM coin_transactions WHERE type = 'earn' ORDER BY created_at DESC LIMIT 5")
        transactions = cursor.fetchall()
        
        print("📊 Recent coin transactions (earn):")
        for tx in transactions:
            print(f"   User: {tx[1]}, Amount: {tx[2]}, Note: {tx[4]}, Date: {tx[5]}")
        
        conn.close()
        
    except Exception as e:
        print(f"❌ Database check failed: {e}")

def main():
    print("🚀 Daily Reward System Debug Tool")
    print("=" * 50)
    
    # Reset daily reward first
    reset_daily_reward_for_user()
    
    # Get authentication token
    token = get_token()
    if not token:
        print("❌ Cannot proceed without authentication token")
        return
    
    print(f"✅ Got authentication token: {token[:20]}...")
    
    # Test status endpoint
    status_data = test_daily_reward_status(token)
    
    # Test claim endpoint
    claim_data = test_daily_reward_claim(token)
    
    # Check database records
    check_database_records()
    
    print("\n" + "=" * 50)
    print("🔍 Debug Summary:")
    if status_data:
        print(f"   ✅ Status endpoint working")
    else:
        print(f"   ❌ Status endpoint failed")
    
    if claim_data:
        print(f"   ✅ Claim endpoint working")
        expected_fields = ["success", "coins_earned", "total_balance", "streak"]
        missing_fields = [field for field in expected_fields if field not in claim_data]
        if missing_fields:
            print(f"   ⚠️ Missing response fields: {missing_fields}")
        else:
            print(f"   ✅ All expected fields present")
    else:
        print(f"   ❌ Claim endpoint failed")

if __name__ == "__main__":
    main()
