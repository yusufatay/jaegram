#!/usr/bin/env python3
"""
Debug script to examine challenge data structure in detail
"""

import sys
import os
import json

# Add backend to path
sys.path.append(os.path.join(os.path.dirname(__file__), 'backend'))

from instagram_service import InstagramAPIService
import logging

# Set up detailed logging
logging.basicConfig(level=logging.DEBUG, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def analyze_challenge_data():
    """Analyze stored challenge data to understand the structure"""
    print("🔍 Challenge Data Structure Analyzer")
    print("=" * 50)
    
    service = InstagramAPIService()
    
    # Check if we have any pending challenges
    if not service.pending_challenges:
        print("❌ No pending challenges found")
        print("💡 First trigger a challenge by attempting to login")
        return
    
    for username, challenge_info in service.pending_challenges.items():
        print(f"\n👤 Challenge for user: {username}")
        print("-" * 30)
        
        challenge_data = challenge_info.get("challenge_data", {})
        
        print(f"📋 Challenge Info:")
        print(f"   Attempts: {challenge_info.get('attempts', 0)}")
        print(f"   Challenge URL: {challenge_info.get('challenge_url')}")
        print(f"   Timestamp: {challenge_info.get('timestamp')}")
        
        print(f"\n📦 Challenge Data Structure:")
        print(f"   Keys: {list(challenge_data.keys())}")
        
        # Analyze the structure
        if "challenge" in challenge_data:
            print(f"   📁 Legacy challenge format detected")
            challenge_obj = challenge_data["challenge"]
            print(f"   Challenge object keys: {list(challenge_obj.keys())}")
            
            if "api_path" in challenge_obj:
                print(f"   API Path: {challenge_obj['api_path']}")
            
            if "challengeType" in challenge_obj:
                print(f"   Challenge Type: {challenge_obj['challengeType']}")
            
        # Check for Bloks format
        bloks_indicators = ["step_name", "nonce_code", "challenge_context", "step_data"]
        found_bloks = [key for key in bloks_indicators if key in challenge_data]
        
        if found_bloks:
            print(f"   📁 Bloks challenge format detected")
            print(f"   Bloks indicators: {found_bloks}")
            
            if "step_name" in challenge_data:
                print(f"   Step Name: {challenge_data['step_name']}")
            
            if "step_data" in challenge_data:
                step_data = challenge_data["step_data"]
                print(f"   Step Data: {step_data}")
                
                if isinstance(step_data, dict):
                    if "contact_point" in step_data:
                        print(f"   📧 Contact Point: {step_data['contact_point']}")
                    if "form_type" in step_data:
                        print(f"   📝 Form Type: {step_data['form_type']}")
        
        print(f"\n📄 Full Challenge Data (JSON):")
        print(json.dumps(challenge_data, indent=2, default=str))

if __name__ == "__main__":
    analyze_challenge_data()
