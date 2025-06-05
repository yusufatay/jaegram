#!/usr/bin/env python3
"""
Migration script to add missing fields to tasks and validation_logs tables
"""

import sqlite3
import logging
from datetime import datetime

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def migrate_database():
    """Add missing fields to existing database"""
    db_path = "/home/mirza/Desktop/instagram_puan_iskelet/backend/instagram_platform.db"
    
    try:
        logger.info(f"Connecting to database: {db_path}")
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        # Check if we need to add fields to tasks table
        cursor.execute("PRAGMA table_info(tasks)")
        tasks_columns = [column[1] for column in cursor.fetchall()]
        
        if 'url' not in tasks_columns:
            logger.info("Adding url column to tasks table")
            cursor.execute("ALTER TABLE tasks ADD COLUMN url TEXT")
            
        if 'task_type' not in tasks_columns:
            logger.info("Adding task_type column to tasks table")
            cursor.execute("ALTER TABLE tasks ADD COLUMN task_type TEXT")
            
        if 'comment_text' not in tasks_columns:
            logger.info("Adding comment_text column to tasks table")
            cursor.execute("ALTER TABLE tasks ADD COLUMN comment_text TEXT")
            
        if 'validation_log_id' not in tasks_columns:
            logger.info("Adding validation_log_id column to tasks table")
            cursor.execute("ALTER TABLE tasks ADD COLUMN validation_log_id INTEGER")
        
        # Check if we need to add fields to validation_logs table
        cursor.execute("PRAGMA table_info(validation_logs)")
        validation_columns = [column[1] for column in cursor.fetchall()]
        
        if 'validation_type' not in validation_columns:
            logger.info("Adding validation_type column to validation_logs table")
            cursor.execute("ALTER TABLE validation_logs ADD COLUMN validation_type TEXT")
            
        if 'url' not in validation_columns:
            logger.info("Adding url column to validation_logs table")
            cursor.execute("ALTER TABLE validation_logs ADD COLUMN url TEXT")
            
        if 'success' not in validation_columns:
            logger.info("Adding success column to validation_logs table")
            cursor.execute("ALTER TABLE validation_logs ADD COLUMN success BOOLEAN DEFAULT 0")
        
        # Update existing tasks with data from their orders
        logger.info("Updating existing tasks with order data")
        cursor.execute("""
            UPDATE tasks 
            SET url = (SELECT post_url FROM orders WHERE orders.id = tasks.order_id),
                task_type = (SELECT order_type FROM orders WHERE orders.id = tasks.order_id),
                comment_text = (SELECT comment_text FROM orders WHERE orders.id = tasks.order_id)
            WHERE url IS NULL OR task_type IS NULL
        """)
        
        conn.commit()
        logger.info("Database migration completed successfully")
        
    except Exception as e:
        logger.error(f"Migration failed: {e}")
        if conn:
            conn.rollback()
        raise
    finally:
        if conn:
            conn.close()

if __name__ == "__main__":
    migrate_database()
