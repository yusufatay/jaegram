#!/usr/bin/env python3
"""
Simple test to check available tasks
"""

import sqlite3
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def check_available_tasks():
    """Check available tasks using direct SQL"""
    db_path = "/home/mirza/Desktop/instagram_puan_iskelet/instagram_platform.db"
    
    try:
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        # Check tasks table structure
        logger.info("Checking tasks table structure:")
        cursor.execute("PRAGMA table_info(tasks)")
        columns = cursor.fetchall()
        for col in columns:
            logger.info(f"  {col[1]} ({col[2]})")
        
        # Check available tasks
        logger.info("\nChecking available tasks:")
        cursor.execute("""
            SELECT t.id, t.order_id, t.status, t.url, t.task_type, o.status as order_status
            FROM tasks t
            JOIN orders o ON o.id = t.order_id
            WHERE t.status = 'pending' AND o.status = 'active'
        """)
        
        tasks = cursor.fetchall()
        logger.info(f"Found {len(tasks)} available tasks:")
        
        for task in tasks:
            logger.info(f"  Task {task[0]}: {task[4]} - {task[3]} (Order: {task[1]}, Order Status: {task[5]})")
        
        # Check all tasks
        logger.info("\nAll tasks:")
        cursor.execute("SELECT id, order_id, status, url, task_type FROM tasks")
        all_tasks = cursor.fetchall()
        
        for task in all_tasks:
            logger.info(f"  Task {task[0]}: {task[4]} - {task[3]} (Order: {task[1]}, Status: {task[2]})")
        
        return len(tasks)
        
    except Exception as e:
        logger.error(f"Error: {e}")
        return 0
    finally:
        if conn:
            conn.close()

def check_users():
    """Check available users"""
    db_path = "/home/mirza/Desktop/instagram_puan_iskelet/instagram_platform.db"
    
    try:
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        cursor.execute("SELECT id, username, coin_balance FROM users LIMIT 10")
        users = cursor.fetchall()
        
        logger.info(f"Found {len(users)} users:")
        for user in users:
            logger.info(f"  User {user[0]}: {user[1]} ({user[2]} coins)")
        
    except Exception as e:
        logger.error(f"Error checking users: {e}")
    finally:
        if conn:
            conn.close()

if __name__ == "__main__":
    logger.info("Checking users...")
    check_users()
    
    logger.info("\nChecking available tasks...")
    task_count = check_available_tasks()
    
    logger.info(f"\nSummary: {task_count} available tasks found")
