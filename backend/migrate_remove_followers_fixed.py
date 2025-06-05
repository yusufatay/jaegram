#!/usr/bin/env python3
"""
Database Migration Script: Remove Follower/Following Columns
This script removes all follower and following related columns from the database tables.
"""

import sqlite3
import os
import sys
import logging
from datetime import datetime

# Setup logging with immediate output
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    stream=sys.stdout
)
logger = logging.getLogger(__name__)

def main():
    print("=" * 60)
    print("DATABASE MIGRATION: Remove Follower/Following Columns")
    print("=" * 60)
    
    # Database path
    db_path = "instagram_platform.db"
    
    if not os.path.exists(db_path):
        print(f"ERROR: Database file not found: {db_path}")
        print("Current directory:", os.getcwd())
        print("Files in current directory:")
        for f in os.listdir("."):
            if f.endswith(".db"):
                print(f"  - {f}")
        return False
    
    print(f"Found database: {db_path}")
    
    try:
        # Create backup first
        print("\n1. Creating database backup...")
        backup_path = backup_database(db_path)
        print(f"✓ Backup created: {backup_path}")
        
        # Connect to database
        print("\n2. Connecting to database...")
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        print("✓ Connected to database")
        
        # Check current table structure
        print("\n3. Checking current table structure...")
        cursor.execute("PRAGMA table_info(users);")
        columns = cursor.fetchall()
        
        print("Current columns in 'users' table:")
        columns_to_remove = []
        for col in columns:
            col_name = col[1]
            print(f"  - {col_name}")
            if col_name in ['followers', 'following', 'instagram_followers', 'instagram_following']:
                columns_to_remove.append(col_name)
        
        if not columns_to_remove:
            print("\n✓ No follower/following columns found. Migration not needed.")
            conn.close()
            return True
        
        print(f"\nColumns to remove: {columns_to_remove}")
        
        # Start transaction
        print("\n4. Starting migration transaction...")
        cursor.execute("BEGIN TRANSACTION;")
        
        # For SQLite, we need to recreate the table without the unwanted columns
        print("\n5. Creating new table structure...")
        
        # Get all columns except the ones we want to remove
        keep_columns = [col for col in columns if col[1] not in columns_to_remove]
        
        # Create column definitions for new table
        column_defs = []
        for col in keep_columns:
            col_name = col[1]
            col_type = col[2]
            not_null = "NOT NULL" if col[3] else ""
            default = f"DEFAULT {col[4]}" if col[4] is not None else ""
            pk = "PRIMARY KEY" if col[5] else ""
            
            col_def = f"{col_name} {col_type} {not_null} {default} {pk}".strip()
            column_defs.append(col_def)
        
        new_table_sql = f"""
        CREATE TABLE users_new (
            {', '.join(column_defs)}
        );
        """
        
        print("New table SQL:")
        print(new_table_sql)
        
        cursor.execute(new_table_sql)
        print("✓ New table created")
        
        # Copy data from old table to new table
        print("\n6. Copying data to new table...")
        keep_column_names = [col[1] for col in keep_columns]
        copy_sql = f"""
        INSERT INTO users_new ({', '.join(keep_column_names)})
        SELECT {', '.join(keep_column_names)} FROM users;
        """
        
        cursor.execute(copy_sql)
        rows_copied = cursor.rowcount
        print(f"✓ Copied {rows_copied} rows to new table")
        
        # Drop old table and rename new table
        print("\n7. Replacing old table...")
        cursor.execute("DROP TABLE users;")
        cursor.execute("ALTER TABLE users_new RENAME TO users;")
        print("✓ Table replaced successfully")
        
        # Commit transaction
        print("\n8. Committing changes...")
        cursor.execute("COMMIT;")
        print("✓ Changes committed")
        
        # Verify final structure
        print("\n9. Verifying final table structure...")
        cursor.execute("PRAGMA table_info(users);")
        final_columns = cursor.fetchall()
        
        print("Final columns in 'users' table:")
        for col in final_columns:
            print(f"  - {col[1]}")
        
        # Check if any follower/following columns remain
        remaining_bad_columns = [col[1] for col in final_columns if col[1] in ['followers', 'following', 'instagram_followers', 'instagram_following']]
        
        if remaining_bad_columns:
            print(f"\n❌ ERROR: Some columns still exist: {remaining_bad_columns}")
            conn.close()
            return False
        
        print("\n✓ Migration completed successfully!")
        print("✓ All follower/following columns removed")
        
        conn.close()
        return True
        
    except Exception as e:
        print(f"\n❌ ERROR during migration: {e}")
        print(f"Exception type: {type(e)}")
        
        try:
            cursor.execute("ROLLBACK;")
            print("✓ Transaction rolled back")
        except:
            pass
        
        try:
            conn.close()
        except:
            pass
        
        return False

def backup_database(db_path):
    """Create a backup of the database before migration"""
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    backup_path = f"{db_path}.backup_{timestamp}"
    
    try:
        # Connect to original database
        source_conn = sqlite3.connect(db_path)
        
        # Create backup
        backup_conn = sqlite3.connect(backup_path)
        source_conn.backup(backup_conn)
        
        # Close connections
        backup_conn.close()
        source_conn.close()
        
        return backup_path
    except Exception as e:
        print(f"Failed to create backup: {e}")
        raise

if __name__ == "__main__":
    print("Starting migration script...")
    success = main()
    
    if success:
        print("\n" + "=" * 60)
        print("MIGRATION COMPLETED SUCCESSFULLY!")
        print("=" * 60)
        sys.exit(0)
    else:
        print("\n" + "=" * 60)
        print("MIGRATION FAILED!")
        print("=" * 60)
        sys.exit(1)
