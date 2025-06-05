#!/usr/bin/env python3
"""
Test script to debug complete-task endpoint issues
"""
import traceback
import requests
import json

def test_complete_task():
    base_url = "http://localhost:8080"
    
    # Login first to get token
    login_data = {
        "username": "testuser",
        "password": "testpassword"
    }
    
    print("=== Login ===")
    try:
        response = requests.post(f"{base_url}/login", data=login_data)
        print(f"Login Status: {response.status_code}")
        
        if response.status_code == 200:
            login_result = response.json()
            token = login_result.get("access_token")
            print(f"Token received: {token[:50]}...")
            
            # Headers for authenticated requests
            headers = {
                "Authorization": f"Bearer {token}",
                "Content-Type": "application/json"
            }
            
            # Check available tasks first
            print("\n=== Available Tasks ===")
            tasks_response = requests.get(f"{base_url}/tasks/available", headers=headers)
            print(f"Available tasks status: {tasks_response.status_code}")
            if tasks_response.status_code == 200:
                tasks_data = tasks_response.json()
                print(f"Available tasks: {json.dumps(tasks_data, indent=2)}")
                
                if 'tasks' in tasks_data and len(tasks_data['tasks']) > 0:
                    # Take first available task
                    first_task = tasks_data['tasks'][0]
                    task_id = first_task['id']
                    
                    print(f"\n=== Taking Task ID {task_id} ===")
                    take_task_data = {"task_id": task_id}
                    take_response = requests.post(f"{base_url}/take-task", json=take_task_data, headers=headers)
                    print(f"Take task status: {take_response.status_code}")
                    print(f"Take task response: {take_response.text}")
                    
                    if take_response.status_code == 200:
                        print(f"\n=== Completing Task ID {task_id} ===")
                        complete_task_data = {"task_id": task_id}
                        
                        try:
                            complete_response = requests.post(f"{base_url}/complete-task", json=complete_task_data, headers=headers)
                            print(f"Complete task status: {complete_response.status_code}")
                            print(f"Complete task response: {complete_response.text}")
                            
                            if complete_response.status_code != 200:
                                print("ERROR: Complete task failed")
                                try:
                                    error_detail = complete_response.json()
                                    print(f"Error detail: {json.dumps(error_detail, indent=2)}")
                                except:
                                    print("Could not parse error response as JSON")
                                    
                        except Exception as e:
                            print(f"Exception during complete-task: {e}")
                            traceback.print_exc()
                    else:
                        print("Could not take task, skipping complete task test")
                else:
                    print("No tasks available to test")
            else:
                print(f"Could not get available tasks: {tasks_response.text}")
                
        else:
            print(f"Login failed: {response.text}")
            
    except Exception as e:
        print(f"Error in test: {e}")
        traceback.print_exc()

if __name__ == "__main__":
    test_complete_task()
