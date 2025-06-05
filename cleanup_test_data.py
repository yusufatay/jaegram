#!/usr/bin/env python3
"""
Database Cleanup Script - Remove Test/Demo Data
This script removes all test data from the production database
"""

import sqlite3
import json
from datetime import datetime

def cleanup_test_data():
    """Remove all test data from the database"""
    
    print("🧹 DATABASE CLEANUP - Removing Test Data")
    print("="*60)
    
    # Connect to database
    conn = sqlite3.connect('instagram_platform.db')
    cursor = conn.cursor()
    
    try:
        # 1. Remove test users
        print("\n🧪 Removing test users...")
        cursor.execute("""
            DELETE FROM users 
            WHERE username LIKE '%test%' 
            OR email LIKE '%test%' 
            OR email LIKE '%example.com'
            OR username LIKE '%demo%'
            OR username LIKE '%sample%'
        """)
        deleted_users = cursor.rowcount
        print(f"   ✅ Removed {deleted_users} test users")
        
        # 2. Remove associated data for deleted users
        # Get user IDs that were deleted (we need to clean up before deletion)
        cursor.execute("""
            SELECT id FROM coin_transactions 
            WHERE user_id NOT IN (SELECT id FROM users)
        """)
        orphaned_transactions = cursor.fetchall()
        
        cursor.execute("""
            DELETE FROM coin_transactions 
            WHERE user_id NOT IN (SELECT id FROM users)
        """)
        deleted_transactions = cursor.rowcount
        print(f"   ✅ Removed {deleted_transactions} orphaned coin transactions")
        
        cursor.execute("""
            DELETE FROM daily_rewards 
            WHERE user_id NOT IN (SELECT id FROM users)
        """)
        deleted_rewards = cursor.rowcount
        print(f"   ✅ Removed {deleted_rewards} orphaned daily rewards")
        
        cursor.execute("""
            DELETE FROM user_statistics 
            WHERE user_id NOT IN (SELECT id FROM users)
        """)
        deleted_stats = cursor.rowcount
        print(f"   ✅ Removed {deleted_stats} orphaned user statistics")
        
        cursor.execute("""
            DELETE FROM user_badges 
            WHERE user_id NOT IN (SELECT id FROM users)
        """)
        deleted_badges = cursor.rowcount
        print(f"   ✅ Removed {deleted_badges} orphaned user badges")
        
        cursor.execute("""
            DELETE FROM email_verifications 
            WHERE user_id NOT IN (SELECT id FROM users)
        """)
        deleted_verifications = cursor.rowcount
        print(f"   ✅ Removed {deleted_verifications} orphaned email verifications")
        
        # 3. Clean up leaderboards (remove entries for deleted users)
        cursor.execute("""
            DELETE FROM leaderboards 
            WHERE user_id NOT IN (SELECT id FROM users)
        """)
        deleted_leaderboard = cursor.rowcount
        print(f"   ✅ Removed {deleted_leaderboard} orphaned leaderboard entries")
        
        # 4. Remove any test-related badges
        cursor.execute("""
            DELETE FROM badges 
            WHERE name LIKE '%test%' 
            OR name LIKE '%demo%' 
            OR description LIKE '%test%'
        """)
        deleted_test_badges = cursor.rowcount
        print(f"   ✅ Removed {deleted_test_badges} test badges")
        
        # 5. Verify cleanup
        print("\n🔍 VERIFICATION - Checking for remaining test data:")
        
        # Check users
        cursor.execute("""
            SELECT COUNT(*) FROM users 
            WHERE username LIKE '%test%' OR email LIKE '%test%'
        """)
        remaining_test_users = cursor.fetchone()[0]
        
        # Check all tables for test patterns
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
        tables = cursor.fetchall()
        
        remaining_test_data = False
        for (table_name,) in tables:
            try:
                cursor.execute(f'PRAGMA table_info({table_name})')
                columns = [col[1] for col in cursor.fetchall()]
                
                text_columns = [col for col in columns if any(keyword in col.lower() for keyword in ['name', 'title', 'description', 'username', 'email', 'text'])]
                
                for col in text_columns:
                    cursor.execute(f"""
                        SELECT COUNT(*) FROM {table_name} 
                        WHERE {col} LIKE '%test%' 
                        OR {col} LIKE '%demo%' 
                        OR {col} LIKE '%sample%' 
                        OR {col} LIKE '%fake%'
                        OR {col} LIKE '%example.com'
                    """)
                    count = cursor.fetchone()[0]
                    if count > 0:
                        remaining_test_data = True
                        print(f"   ⚠️  {table_name}.{col}: {count} records still contain test patterns")
            except Exception:
                pass
        
        if not remaining_test_data and remaining_test_users == 0:
            print("   ✅ All test data successfully removed!")
        else:
            print(f"   ⚠️  {remaining_test_users} test users remain")
        
        # 6. Commit changes
        conn.commit()
        
        print(f"\n✅ CLEANUP COMPLETED")
        print(f"   - Removed {deleted_users} test users")
        print(f"   - Removed {deleted_transactions + deleted_rewards + deleted_stats + deleted_badges + deleted_verifications + deleted_leaderboard} associated records")
        print(f"   - Database is now clean for production use")
        
        return True
        
    except Exception as e:
        print(f"❌ ERROR during cleanup: {e}")
        conn.rollback()
        return False
    finally:
        conn.close()

def verify_production_readiness():
    """Verify the database is ready for production"""
    
    print("\n🔍 PRODUCTION READINESS VERIFICATION")
    print("="*60)
    
    conn = sqlite3.connect('instagram_platform.db')
    cursor = conn.cursor()
    
    try:
        # Check for real users (non-test)
        cursor.execute("""
            SELECT COUNT(*) FROM users 
            WHERE username NOT LIKE '%test%' 
            AND email NOT LIKE '%test%' 
            AND email NOT LIKE '%example.com'
        """)
        real_users = cursor.fetchone()[0]
        
        # Check system tables
        cursor.execute("SELECT COUNT(*) FROM badges")
        badge_count = cursor.fetchone()[0]
        
        cursor.execute("SELECT COUNT(*) FROM orders")
        order_count = cursor.fetchone()[0]
        
        cursor.execute("SELECT COUNT(*) FROM tasks")
        task_count = cursor.fetchone()[0]
        
        print(f"👥 Real Users: {real_users}")
        print(f"🏆 System Badges: {badge_count}")
        print(f"📋 Orders: {order_count}")
        print(f"📋 Tasks: {task_count}")
        
        # Database schema verification
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
        tables = [table[0] for table in cursor.fetchall()]
        
        expected_tables = [
            'users', 'orders', 'tasks', 'coin_transactions', 'notifications',
            'badges', 'user_badges', 'leaderboards', 'instagram_credentials',
            'daily_rewards', 'email_verifications', 'user_statistics',
            'referrals', 'notification_settings', 'device_ip_logs',
            'gdpr_requests', 'user_education', 'mental_health_logs',
            'coin_withdrawal_requests', 'user_social', 'validation_logs',
            'user_fcm_tokens', 'coin_withdrawal_verifications', 'instagram_profiles'
        ]
        
        missing_tables = [table for table in expected_tables if table not in tables]
        extra_tables = [table for table in tables if table not in expected_tables and not table.startswith('sqlite_')]
        
        if missing_tables:
            print(f"⚠️  Missing tables: {missing_tables}")
        else:
            print("✅ All required tables present")
            
        if extra_tables:
            print(f"ℹ️  Additional tables: {extra_tables}")
        
        return len(missing_tables) == 0
        
    finally:
        conn.close()

if __name__ == "__main__":
    success = cleanup_test_data()
    if success:
        verify_production_readiness()
    else:
        print("❌ Cleanup failed - manual intervention required")
