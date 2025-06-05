#!/usr/bin/env python3
"""
Test script to create an order and test the task system
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from models import SessionLocal, User, Order, Task, OrderType, TaskStatus
from datetime import datetime
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def create_test_order():
    """Create a test order for testing the task system"""
    db = SessionLocal()
    
    try:
        # Find a test user
        test_user = db.query(User).filter(User.username == "williamjohnson12935").first()
        if not test_user:
            logger.error("Test user not found")
            return
        
        # Check current coin balance
        logger.info(f"User {test_user.username} has {test_user.coin_balance} coins")
        
        # Create a test order
        test_order = Order(
            user_id=test_user.id,
            post_url="https://www.instagram.com/p/test123/",
            order_type=OrderType.like,
            target_count=3,
            status="active"
        )
        db.add(test_order)
        db.flush()  # Get the order ID
        
        # Deduct coins
        cost = 3 * 10  # 3 tasks * 10 coins each
        test_user.coin_balance -= cost
        
        # Create tasks with proper fields
        tasks_to_create = []
        for i in range(3):
            task = Task(
                order_id=test_order.id,
                status=TaskStatus.pending,
                url=test_order.post_url,
                task_type=test_order.order_type.value,
                comment_text=None
            )
            tasks_to_create.append(task)
        
        db.add_all(tasks_to_create)
        db.commit()
        
        logger.info(f"Created test order {test_order.id} with 3 tasks")
        logger.info(f"User {test_user.username} now has {test_user.coin_balance} coins")
        
        # Verify tasks were created
        task_count = db.query(Task).filter(Task.order_id == test_order.id).count()
        logger.info(f"Verified: {task_count} tasks created for order {test_order.id}")
        
        return test_order.id
        
    except Exception as e:
        logger.error(f"Error creating test order: {e}")
        db.rollback()
        raise
    finally:
        db.close()

def check_available_tasks():
    """Check if there are any available tasks"""
    db = SessionLocal()
    
    try:
        available_tasks = db.query(Task).join(Order).filter(
            Task.status == TaskStatus.pending,
            Order.status == "active"
        ).all()
        
        logger.info(f"Found {len(available_tasks)} available tasks")
        
        for task in available_tasks:
            logger.info(f"Task {task.id}: {task.task_type} - {task.url} (Order: {task.order_id})")
        
        return len(available_tasks)
        
    finally:
        db.close()

if __name__ == "__main__":
    logger.info("Creating test order...")
    order_id = create_test_order()
    
    logger.info("Checking available tasks...")
    task_count = check_available_tasks()
    
    logger.info(f"Test completed. Order {order_id} created with {task_count} available tasks.")
