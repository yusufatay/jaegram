#!/usr/bin/env python3
"""
Test the task system with API calls
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
        response = requests.post(f"{BASE_URL}/login", data={
            "username": username,
            "password": password
        })
        
        print(f"Login response status: {response.status_code}")
        print(f"Login response: {response.text}")
        
        if response.status_code == 200:
            token_data = response.json()
            logger.info(f"Login successful for {username}")
            return token_data["access_token"]
        else:
            logger.error(f"Login failed: {response.status_code} - {response.text}")
            return None
            
    except Exception as e:
        logger.error(f"Login error: {e}")
        return None

def take_task(token):
    """Try to take a task"""
    try:
        headers = {"Authorization": f"Bearer {token}"}
        response = requests.post(f"{BASE_URL}/take-task", headers=headers)
        
        logger.info(f"Take task response: {response.status_code}")
        logger.info(f"Response body: {response.text}")
        
        if response.status_code == 200:
            task_data = response.json()
            logger.info(f"Task taken successfully: {task_data}")
            return task_data
        else:
            logger.error(f"Failed to take task: {response.status_code} - {response.text}")
            return None
            
    except Exception as e:
        logger.error(f"Take task error: {e}")
        return None

def get_user_profile(token):
    """Get user profile to check current state"""
    try:
        headers = {"Authorization": f"Bearer {token}"}
        response = requests.get(f"{BASE_URL}/profile", headers=headers)
        
        if response.status_code == 200:
            profile = response.json()
            logger.info(f"User profile: {profile.get('username')} - {profile.get('coin_balance')} coins")
            return profile
        else:
            logger.error(f"Failed to get profile: {response.status_code} - {response.text}")
            return None
            
    except Exception as e:
        logger.error(f"Profile error: {e}")
        return None

def main():
    """Main test function"""
    logger.info("=== TESTING TASK SYSTEM ===")
    
    # Test credentials
    username = "williamjohnson12935"
    password = "mmmmmmmm2008"
    
    # Step 1: Login
    logger.info("Step 1: Logging in...")
    token = login_user(username, password)
    if not token:
        logger.error("Login failed, stopping test")
        return
    
    # Step 2: Get profile
    logger.info("Step 2: Getting user profile...")
    profile = get_user_profile(token)
    
    # Step 3: Try to take a task
    logger.info("Step 3: Trying to take a task...")
    task = take_task(token)
    
    if task:
        logger.info("🎉 SUCCESS: Task system is working!")
        logger.info(f"Task details: {task}")
    else:
        logger.warning("❌ Task system needs investigation")

if __name__ == "__main__":
    main()
