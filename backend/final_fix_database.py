#!/usr/bin/env python3
"""
FINAL DATABASE FIX - NULL Identity Key Error Resolution

This script will DEFINITELY fix the users table primary key issue once and for all.
"""

import sqlite3
import os
import shutil
from datetime import datetime

def final_fix_database():
    """Final fix for the users table primary key issue"""
    
    db_path = "instagram_platform.db"
    
    if not os.path.exists(db_path):
        print(f"❌ Database file not found: {db_path}")
        return False
    
    # Backup first
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    backup_path = f"{db_path}.final_backup_{timestamp}"
    shutil.copy2(db_path, backup_path)
    print(f"✅ Database backed up to: {backup_path}")
    
    try:
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        print("🔧 Starting FINAL database fix...")
        
        # Check current users table
        cursor.execute("SELECT COUNT(*) FROM users")
        user_count = cursor.fetchone()[0]
        print(f"📊 Current users: {user_count}")
        
        # Get all user data first
        cursor.execute("SELECT * FROM users")
        all_users = cursor.fetchall()
        
        # Get column info
        cursor.execute("PRAGMA table_info(users)")
        columns_info = cursor.fetchall()
        column_names = [col[1] for col in columns_info]
        
        print(f"📋 Columns: {len(column_names)}")
        
        # Drop the problematic table completely
        print("🗑️  Dropping old users table...")
        cursor.execute("DROP TABLE IF EXISTS users")
        
        # Create the new table with PROPER primary key
        print("🏗️  Creating NEW users table with PROPER primary key...")
        
        create_sql = """
        CREATE TABLE users (
            id INTEGER PRIMARY KEY AUTOINCREMENT NOT NULL,
            username TEXT UNIQUE NOT NULL,
            password_hash TEXT,
            email TEXT UNIQUE,
            email_verified INTEGER DEFAULT 0,
            email_verification_code TEXT,
            email_verification_expires INTEGER,
            two_factor_enabled INTEGER DEFAULT 0,
            two_factor_secret TEXT,
            full_name TEXT,
            profile_pic_url TEXT,
            coin_balance INTEGER DEFAULT 0,
            is_admin INTEGER DEFAULT 0,
            is_active INTEGER DEFAULT 1,
            is_admin_platform INTEGER DEFAULT 0,
            created_at INTEGER,
            updated_at INTEGER,
            last_daily_reward INTEGER,
            daily_reward_streak INTEGER DEFAULT 0,
            instagram_pk TEXT UNIQUE,
            instagram_username TEXT,
            instagram_session_data TEXT,
            first_name TEXT,
            last_name TEXT,
            phone_number TEXT,
            birth_date INTEGER,
            gender TEXT,
            country TEXT,
            city TEXT,
            timezone TEXT,
            language TEXT DEFAULT 'tr',
            last_login_at INTEGER,
            last_seen_at INTEGER,
            login_count INTEGER DEFAULT 0,
            registration_ip TEXT,
            last_login_ip TEXT,
            account_status TEXT DEFAULT 'active',
            suspension_reason TEXT,
            bio TEXT,
            website_url TEXT,
            privacy_public_profile INTEGER DEFAULT 1,
            privacy_show_email INTEGER DEFAULT 0,
            privacy_show_phone INTEGER DEFAULT 0,
            privacy_show_stats INTEGER DEFAULT 1,
            theme_preference TEXT DEFAULT 'system',
            notification_email INTEGER DEFAULT 1,
            notification_push INTEGER DEFAULT 1,
            notification_sms INTEGER DEFAULT 0,
            instagram_posts_count INTEGER DEFAULT 0,
            instagram_profile_pic_url TEXT,
            instagram_bio TEXT,
            instagram_is_private INTEGER,
            instagram_is_verified INTEGER,
            instagram_external_url TEXT,
            instagram_category TEXT,
            instagram_contact_phone TEXT,
            instagram_contact_email TEXT,
            instagram_business_category TEXT,
            instagram_connected_at INTEGER,
            instagram_last_sync INTEGER,
            instagram_sync_enabled INTEGER
        )
        """
        
        cursor.execute(create_sql)
        print("✅ NEW users table created with proper PRIMARY KEY AUTOINCREMENT")
        
        # Insert all the old data back (without the id column, let it auto-generate)
        if all_users:
            print(f"📁 Restoring {len(all_users)} users...")
            
            # Prepare insert statement (skip id column, let it auto-increment)
            insert_columns = column_names[1:]  # Skip 'id' column
            placeholders = ",".join(["?" for _ in insert_columns])
            columns_str = ",".join(insert_columns)
            
            insert_sql = f"INSERT INTO users ({columns_str}) VALUES ({placeholders})"
            
            for user_row in all_users:
                user_data = user_row[1:]  # Skip the old id value
                cursor.execute(insert_sql, user_data)
            
            print("✅ All user data restored with NEW auto-generated IDs")
        
        # Create indexes
        print("📇 Creating indexes...")
        indexes = [
            "CREATE INDEX ix_users_id ON users (id)",
            "CREATE UNIQUE INDEX ix_users_username ON users (username)",
            "CREATE UNIQUE INDEX ix_users_email ON users (email)",
            "CREATE UNIQUE INDEX ix_users_instagram_pk ON users (instagram_pk)",
            "CREATE INDEX ix_users_instagram_username ON users (instagram_username)"
        ]
        
        for index_sql in indexes:
            try:
                cursor.execute(index_sql)
            except Exception as e:
                print(f"⚠️  Index warning: {e}")
        
        # FINAL TEST - Test autoincrement
        print("🧪 Testing autoincrement...")
        cursor.execute("""
            INSERT INTO users (username, email, created_at) 
            VALUES ('test_final_user', 'final_test@example.com', ?)
        """, (int(datetime.now().timestamp()),))
        
        cursor.execute("SELECT id FROM users WHERE username = 'test_final_user'")
        test_user = cursor.fetchone()
        
        if test_user and test_user[0]:
            print(f"✅ AUTOINCREMENT WORKING! Test user ID: {test_user[0]}")
            cursor.execute("DELETE FROM users WHERE username = 'test_final_user'")
        else:
            print("❌ AUTOINCREMENT FAILED!")
            return False
        
        # Commit everything
        conn.commit()
        
        # Final verification
        cursor.execute("SELECT COUNT(*) FROM users")
        final_count = cursor.fetchone()[0]
        print(f"📊 Final user count: {final_count}")
        
        # Check table structure
        cursor.execute("PRAGMA table_info(users)")
        new_columns = cursor.fetchall()
        id_column = next((col for col in new_columns if col[1] == 'id'), None)
        
        if id_column and id_column[5] == 1:  # Primary key flag
            print("✅ PRIMARY KEY VERIFIED!")
        else:
            print("❌ PRIMARY KEY VERIFICATION FAILED!")
            return False
            
        print("\n🎉 DATABASE FIXED SUCCESSFULLY!")
        print("🔧 The NULL identity key error is NOW RESOLVED!")
        
        return True
        
    except Exception as e:
        print(f"❌ Error during final fix: {e}")
        conn.rollback()
        return False
    finally:
        conn.close()

if __name__ == "__main__":
    print("🚀 FINAL DATABASE FIX - Starting...")
    print("=" * 60)
    
    if final_fix_database():
        print("=" * 60)
        print("🎉 SUCCESS! Database is now fixed!")
        print("🔧 You can now restart the server and test the Instagram challenge.")
        print("=" * 60)
    else:
        print("=" * 60)
        print("❌ FAILED! Please check the error messages above.")
        print("=" * 60)
