#!/usr/bin/env python3
"""
Test script to test the task system via API
"""

import requests
import json
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

BASE_URL = "http://localhost:8000"

def login_user(username, password):
    """Login and get access token"""
    try:
        response = requests.post(f"{BASE_URL}/token", data={
            "username": username,
            "password": password
        })
        
        if response.status_code == 200:
            data = response.json()
            logger.info(f"Login successful for {username}")
            return data.get("access_token")
        else:
            logger.error(f"Login failed: {response.status_code} - {response.text}")
            return None
            
    except Exception as e:
        logger.error(f"Login error: {e}")
        return None

def take_task(token):
    """Take a task"""
    try:
        headers = {
            "Authorization": f"Bearer {token}",
            "Content-Type": "application/json"
        }
        
        response = requests.post(f"{BASE_URL}/take-task", headers=headers)
        
        logger.info(f"Take task response: {response.status_code}")
        logger.info(f"Response: {response.text}")
        
        if response.status_code == 200:
            return response.json()
        else:
            return None
            
    except Exception as e:
        logger.error(f"Take task error: {e}")
        return None

def get_user_info(token):
    """Get current user info"""
    try:
        headers = {
            "Authorization": f"Bearer {token}",
            "Content-Type": "application/json"
        }
        
        response = requests.get(f"{BASE_URL}/users/me", headers=headers)
        
        if response.status_code == 200:
            return response.json()
        else:
            logger.error(f"Get user info failed: {response.status_code} - {response.text}")
            return None
            
    except Exception as e:
        logger.error(f"Get user info error: {e}")
        return None

def test_task_system():
    """Test the complete task system"""
    # Test with williamjohnson12935 user
    username = "williamjohnson12935"
    password = "password123"  # Default test password
    
    logger.info(f"Testing task system with user: {username}")
    
    # Step 1: Login
    token = login_user(username, password)
    if not token:
        logger.error("Could not get access token")
        return
    
    # Step 2: Get user info
    user_info = get_user_info(token)
    if user_info:
        logger.info(f"User info: {user_info.get('username')} - Coins: {user_info.get('coin_balance')}")
    
    # Step 3: Try to take a task
    task_result = take_task(token)
    if task_result:
        logger.info(f"Task taken successfully: {task_result}")
    else:
        logger.error("Could not take task")

if __name__ == "__main__":
    test_task_system()
