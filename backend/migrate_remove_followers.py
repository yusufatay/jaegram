#!/usr/bin/env python3
"""
Database Migration Script: Remove Follower/Following Columns
This script removes all follower and following related columns from the database tables.
"""

import sqlite3
import os
import logging
from datetime import datetime

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def backup_database(db_path):
    """Create a backup of the database before migration"""
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    backup_path = f"{db_path}.backup_{timestamp}"
    
    try:
        # Connect to original database
        source_conn = sqlite3.connect(db_path)
        source_conn.execute("BEGIN IMMEDIATE;")
        
        # Create backup
        backup_conn = sqlite3.connect(backup_path)
        source_conn.backup(backup_conn)
        
        # Close connections
        backup_conn.close()
        source_conn.close()
        
        logger.info(f"Database backup created: {backup_path}")
        return backup_path
    except Exception as e:
        logger.error(f"Failed to create backup: {e}")
        raise

def remove_follower_following_columns(db_path):
    """Remove follower and following columns from users table"""
    
    try:
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        logger.info("Starting migration to remove follower/following columns...")
        
        # Check if columns exist first
        cursor.execute("PRAGMA table_info(users);")
        columns = cursor.fetchall()
        column_names = [col[1] for col in columns]
        
        columns_to_remove = []
        if 'followers' in column_names:
            columns_to_remove.append('followers')
        if 'following' in column_names:
            columns_to_remove.append('following')
        if 'instagram_followers' in column_names:
            columns_to_remove.append('instagram_followers')
        if 'instagram_following' in column_names:
            columns_to_remove.append('instagram_following')
            
        if not columns_to_remove:
            logger.info("No follower/following columns found to remove.")
            return True
            
        logger.info(f"Found columns to remove: {columns_to_remove}")
        
        # Start transaction
        cursor.execute("BEGIN TRANSACTION;")
        
        # Create new table without follower/following columns
        # Get current table schema
        cursor.execute("SELECT sql FROM sqlite_master WHERE type='table' AND name='users';")
        create_sql = cursor.fetchone()[0]
        
        # Remove follower/following columns from the CREATE statement
        lines = create_sql.split('\n')
        filtered_lines = []
        
        for line in lines:
            line_lower = line.lower().strip()
            should_skip = False
            
            for col in columns_to_remove:
                if f'{col.lower()} ' in line_lower or f'{col.lower()}\t' in line_lower:
                    should_skip = True
                    break
                    
            if not should_skip:
                filtered_lines.append(line)
        
        # Create the new table SQL
        new_create_sql = '\n'.join(filtered_lines)
        new_create_sql = new_create_sql.replace('CREATE TABLE "users"', 'CREATE TABLE "users_new"')
        
        logger.info("Creating new users table without follower/following columns...")
        cursor.execute(new_create_sql)
        
        # Copy data from old table to new table (excluding removed columns)
        remaining_columns = [col for col in column_names if col not in columns_to_remove]
        columns_str = ', '.join([f'"{col}"' for col in remaining_columns])
        
        copy_sql = f'INSERT INTO "users_new" ({columns_str}) SELECT {columns_str} FROM "users";'
        logger.info(f"Copying data to new table...")
        cursor.execute(copy_sql)
        
        # Drop old table and rename new table
        logger.info("Replacing old table with new table...")
        cursor.execute('DROP TABLE "users";')
        cursor.execute('ALTER TABLE "users_new" RENAME TO "users";')
        
        # Recreate indexes that might have been lost
        logger.info("Recreating indexes...")
        cursor.execute('CREATE UNIQUE INDEX IF NOT EXISTS "ix_users_username" ON "users" ("username");')
        cursor.execute('CREATE UNIQUE INDEX IF NOT EXISTS "ix_users_email" ON "users" ("email");')
        cursor.execute('CREATE INDEX IF NOT EXISTS "ix_users_id" ON "users" ("id");')
        cursor.execute('CREATE UNIQUE INDEX IF NOT EXISTS "ix_users_instagram_pk" ON "users" ("instagram_pk");')
        cursor.execute('CREATE INDEX IF NOT EXISTS "ix_users_instagram_username" ON "users" ("instagram_username");')
        
        # Commit transaction
        cursor.execute("COMMIT;")
        
        logger.info(f"Successfully removed columns: {columns_to_remove}")
        
        # Verify the migration
        cursor.execute("PRAGMA table_info(users);")
        new_columns = cursor.fetchall()
        new_column_names = [col[1] for col in new_columns]
        
        logger.info(f"Remaining columns in users table: {len(new_column_names)}")
        
        # Check that removed columns are gone
        still_present = [col for col in columns_to_remove if col in new_column_names]
        if still_present:
            logger.error(f"Migration failed - columns still present: {still_present}")
            return False
        
        conn.close()
        logger.info("Migration completed successfully!")
        return True
        
    except Exception as e:
        logger.error(f"Migration failed: {e}")
        try:
            cursor.execute("ROLLBACK;")
            conn.close()
        except:
            pass
        raise

def main():
    """Main migration function"""
    db_path = "./instagram_platform.db"
    
    if not os.path.exists(db_path):
        logger.error(f"Database file not found: {db_path}")
        return False
    
    try:
        # Create backup
        backup_path = backup_database(db_path)
        
        # Run migration
        success = remove_follower_following_columns(db_path)
        
        if success:
            logger.info("=" * 60)
            logger.info("MIGRATION COMPLETED SUCCESSFULLY!")
            logger.info("=" * 60)
            logger.info(f"Database: {db_path}")
            logger.info(f"Backup: {backup_path}")
            logger.info("Removed columns: followers, following, instagram_followers, instagram_following")
            logger.info("=" * 60)
        else:
            logger.error("Migration failed!")
            
        return success
        
    except Exception as e:
        logger.error(f"Migration error: {e}")
        return False

if __name__ == "__main__":
    main()
