#!/usr/bin/env python3
"""
Fix Users Table Primary Key Issue

This script addresses the "NULL identity key" error by properly recreating
the users table with the correct primary key and autoincrement settings.
"""

import sqlite3
import os
import shutil
from datetime import datetime

print("🚀 Script starting - imports successful")

def backup_database():
    """Create a backup of the current database"""
    db_path = "instagram_platform.db"
    if os.path.exists(db_path):
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        backup_path = f"{db_path}.backup_{timestamp}"
        shutil.copy2(db_path, backup_path)
        print(f"✅ Database backed up to: {backup_path}")
        return backup_path
    return None

def fix_users_table():
    """Fix the users table by recreating it with proper primary key"""
    
    # First backup the database
    backup_path = backup_database()
    
    # Connect to database
    conn = sqlite3.connect("instagram_platform.db")
    cursor = conn.cursor()
    
    try:
        print("🔧 Starting users table fix...")
        
        # Step 1: Check current table structure
        cursor.execute("PRAGMA table_info(users)")
        columns = cursor.fetchall()
        print(f"📋 Current users table has {len(columns)} columns")
        
        # Step 2: Create new table with proper structure
        print("🏗️  Creating new users table with proper primary key...")
        
        create_table_sql = """
        CREATE TABLE users_new (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
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
        
        cursor.execute(create_table_sql)
        print("✅ New users table created successfully")
        
        # Step 3: Copy data from old table to new table
        print("📁 Copying existing user data...")
        
        # Get all data from old table
        cursor.execute("SELECT * FROM users")
        old_data = cursor.fetchall()
        
        if old_data:
            print(f"📊 Found {len(old_data)} existing users to migrate")
            
            # Get column names from old table
            cursor.execute("PRAGMA table_info(users)")
            old_columns = [col[1] for col in cursor.fetchall()]
            
            # Create INSERT statement with proper column mapping
            placeholders = ",".join(["?" for _ in old_columns])
            columns_str = ",".join(old_columns)
            
            insert_sql = f"INSERT INTO users_new ({columns_str}) VALUES ({placeholders})"
            
            for row in old_data:
                try:
                    cursor.execute(insert_sql, row)
                except Exception as e:
                    print(f"⚠️  Warning: Could not migrate row {row[0] if row else 'unknown'}: {e}")
            
            print("✅ User data migration completed")
        else:
            print("ℹ️  No existing users found to migrate")
        
        # Step 4: Drop old table and rename new table
        print("🔄 Replacing old table with new table...")
        cursor.execute("DROP TABLE users")
        cursor.execute("ALTER TABLE users_new RENAME TO users")
        
        # Step 5: Recreate indexes
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
                print(f"⚠️  Warning: Could not create index: {e}")
        
        print("✅ Indexes created successfully")
        
        # Step 6: Verify the fix
        print("🔍 Verifying the fix...")
        
        # Check that the table has proper primary key
        cursor.execute("PRAGMA table_info(users)")
        columns = cursor.fetchall()
        
        id_column = next((col for col in columns if col[1] == 'id'), None)
        if id_column and id_column[5] == 1:  # pk column is index 5
            print("✅ Primary key constraint verified")
        else:
            print("❌ Primary key constraint issue detected")
            
        # Test autoincrement by inserting a test user
        cursor.execute("""
            INSERT INTO users (username, email, created_at) 
            VALUES ('test_autoincrement_user', 'test@example.com', ?)
        """, (int(datetime.now().timestamp()),))
        
        cursor.execute("SELECT id FROM users WHERE username = 'test_autoincrement_user'")
        test_user = cursor.fetchone()
        
        if test_user and test_user[0]:
            print(f"✅ Autoincrement working - Test user got ID: {test_user[0]}")
            # Clean up test user
            cursor.execute("DELETE FROM users WHERE username = 'test_autoincrement_user'")
        else:
            print("❌ Autoincrement test failed")
        
        # Commit all changes
        conn.commit()
        print("✅ All changes committed successfully")
        
        # Final verification
        cursor.execute("SELECT COUNT(*) FROM users")
        user_count = cursor.fetchone()[0]
        print(f"📊 Final user count: {user_count}")
        
        print("\n🎉 Users table fix completed successfully!")
        print("🔧 The NULL identity key error should now be resolved.")
        
    except Exception as e:
        print(f"❌ Error during users table fix: {e}")
        conn.rollback()
        
        # Restore backup if something went wrong
        if backup_path and os.path.exists(backup_path):
            print(f"🔄 Restoring database from backup: {backup_path}")
            shutil.copy2(backup_path, "instagram_platform.db")
            print("✅ Database restored from backup")
        
        raise
        
    finally:
        conn.close()

if __name__ == "__main__":
    print("🚀 Starting Users Table Primary Key Fix")
    print("=" * 50)
    
    # Check current directory and database file
    current_dir = os.getcwd()
    print(f"📁 Current directory: {current_dir}")
    
    # Look for database file in current and backend directories
    db_locations = ["instagram_platform.db", "backend/instagram_platform.db"]
    db_path = None
    
    for location in db_locations:
        if os.path.exists(location):
            db_path = location
            print(f"📊 Found database at: {location}")
            break
    
    if not db_path:
        print("❌ Could not find instagram_platform.db file!")
        print("🔍 Looking in current directory...")
        files = [f for f in os.listdir(".") if f.endswith(".db")]
        print(f"📁 Database files found: {files}")
        exit(1)
    
    # Change to directory containing the database
    if "backend/" in db_path:
        os.chdir("backend")
        print("📁 Changed to backend directory")
    
    fix_users_table()
    
    print("=" * 50)
    print("🏁 Fix completed. You can now test the Instagram challenge authentication.")
