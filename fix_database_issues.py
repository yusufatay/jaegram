#!/usr/bin/env python3
"""
Comprehensive fix for database schema and daily reward issues
"""

import sqlite3
import os
from datetime import datetime, date

DB_PATH = "instagram_platform.db"

def main():
    print("🔧 Comprehensive Database Fixes")
    print("=" * 50)
    
    if not os.path.exists(DB_PATH):
        print(f"❌ Database {DB_PATH} not found!")
        return
    
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    try:
        # Fix 1: Verify order_id column exists in coin_transactions
        print("1. Checking coin_transactions.order_id column...")
        cursor.execute("PRAGMA table_info(coin_transactions)")
        columns = [col[1] for col in cursor.fetchall()]
        if 'order_id' in columns:
            print("✅ order_id column exists")
        else:
            print("❌ order_id column missing - this should have been fixed already")
        
        # Fix 2: Clean up daily_rewards date format issue
        print("\n2. Fixing daily_rewards date format...")
        
        # First, check current data
        cursor.execute("SELECT COUNT(*) FROM daily_rewards")
        count = cursor.fetchone()[0]
        print(f"   Found {count} daily reward records")
        
        if count > 0:
            # Update any datetime entries to date format
            cursor.execute("""
                UPDATE daily_rewards 
                SET claimed_date = date(claimed_date)
                WHERE claimed_date LIKE '%:%'
            """)
            affected = cursor.rowcount
            print(f"   Updated {affected} records to date format")
        
        # Fix 3: Add a unique constraint to prevent duplicate daily rewards
        print("\n3. Adding unique constraint for daily rewards...")
        try:
            # Check if index already exists
            cursor.execute("PRAGMA index_list(daily_rewards)")
            indexes = cursor.fetchall()
            has_unique_constraint = any('unique' in str(idx).lower() for idx in indexes)
            
            if not has_unique_constraint:
                cursor.execute("""
                    CREATE UNIQUE INDEX IF NOT EXISTS idx_daily_rewards_user_date 
                    ON daily_rewards(user_id, claimed_date)
                """)
                print("✅ Added unique constraint to prevent duplicate daily rewards")
            else:
                print("✅ Unique constraint already exists")
        except sqlite3.OperationalError as e:
            print(f"⚠️  Unique constraint creation: {e}")
        
        # Fix 4: Clean up any duplicate daily rewards for today
        print("\n4. Cleaning up duplicate daily rewards...")
        today = date.today().isoformat()
        
        # Find duplicates for today
        cursor.execute("""
            SELECT user_id, COUNT(*) as count 
            FROM daily_rewards 
            WHERE date(claimed_date) = ? 
            GROUP BY user_id 
            HAVING COUNT(*) > 1
        """, (today,))
        
        duplicates = cursor.fetchall()
        if duplicates:
            print(f"   Found {len(duplicates)} users with duplicate rewards today")
            for user_id, count in duplicates:
                # Keep only the latest one
                cursor.execute("""
                    DELETE FROM daily_rewards 
                    WHERE user_id = ? AND date(claimed_date) = ? 
                    AND id NOT IN (
                        SELECT id FROM daily_rewards 
                        WHERE user_id = ? AND date(claimed_date) = ? 
                        ORDER BY created_at DESC LIMIT 1
                    )
                """, (user_id, today, user_id, today))
                print(f"   Removed {cursor.rowcount} duplicate rewards for user {user_id}")
        else:
            print("✅ No duplicate daily rewards found")
        
        # Commit all changes
        conn.commit()
        print("\n✅ All database fixes completed successfully!")
        
        # Verification
        print("\n📊 Verification:")
        cursor.execute("SELECT COUNT(*) FROM daily_rewards WHERE date(claimed_date) = ?", (today,))
        today_count = cursor.fetchone()[0]
        print(f"   Daily rewards claimed today: {today_count}")
        
        cursor.execute("PRAGMA table_info(coin_transactions)")
        ct_columns = [col[1] for col in cursor.fetchall()]
        print(f"   CoinTransaction columns: {ct_columns}")
        
    except Exception as e:
        print(f"❌ Error during database fixes: {e}")
        conn.rollback()
    finally:
        conn.close()

if __name__ == "__main__":
    main()
