#!/usr/bin/env python3
"""
Enhanced Challenge Detection Test
Tests the improved Bloks vs Legacy challenge detection and analysis
"""

import sys
import os
import json
import asyncio

# Add backend to path
sys.path.append(os.path.join(os.path.dirname(__file__), 'backend'))

from instagram_service import InstagramAPIService
import logging

# Set up logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def test_challenge_analysis():
    """Test the challenge data analysis functionality"""
    
    print("🔍 Enhanced Challenge Detection Test")
    print("=" * 60)
    
    service = InstagramAPIService()
    
    # Test case 1: Modern Bloks challenge with complete data
    print("\n📱 Test Case 1: Modern Bloks Challenge (Complete)")
    print("-" * 50)
    
    bloks_challenge_complete = {
        "step_name": "verify_email",
        "step_data": {
            "contact_point": "n******f@w*****.com",
            "form_type": "email"
        },
        "nonce_code": "abc123def456",
        "challenge_context": "eyJ0ZXN0IjoiZGF0YSJ9",
        "user_id": 74918532103,
        "flow_render_type": "email_verification"
    }
    
    analysis1 = service._analyze_challenge_data(bloks_challenge_complete)
    print(f"📊 Analysis Result:")
    print(f"   Format: {analysis1['format']}")
    print(f"   Step Name: {analysis1['step_name']}")
    print(f"   Contact Point: {analysis1.get('contact_point', 'Not found')}")
    print(f"   Form Type: {analysis1.get('form_type', 'Not found')}")
    print(f"   Contact Hint: {analysis1.get('contact_hint', 'Not found')}")
    print(f"   Has Nonce: {analysis1['has_nonce']}")
    print(f"   Has Context: {analysis1['has_context']}")
    
    # Test case 2: Bloks challenge with minimal data
    print("\n📱 Test Case 2: Bloks Challenge (Minimal)")
    print("-" * 50)
    
    bloks_challenge_minimal = {
        "step_name": "verify_email",
        "nonce_code": "xyz789"
    }
    
    analysis2 = service._analyze_challenge_data(bloks_challenge_minimal)
    print(f"📊 Analysis Result:")
    print(f"   Format: {analysis2['format']}")
    print(f"   Step Name: {analysis2['step_name']}")
    print(f"   Has Nonce: {analysis2['has_nonce']}")
    print(f"   Has Context: {analysis2['has_context']}")
    
    # Test case 3: Legacy challenge format
    print("\n🏛️ Test Case 3: Legacy Challenge")
    print("-" * 50)
    
    legacy_challenge = {
        "message": "challenge_required",
        "challenge": {
            "api_path": "/challenge/8530598273/PlWAX2OMVk/",
            "challengeType": "VerifyEmailCodeForm",
            "hide_webview_header": True,
            "lock": True,
            "navigation": {
                "forward": "/challenge/8530598273/PlWAX2OMVk/"
            }
        },
        "status": "fail"
    }
    
    analysis3 = service._analyze_challenge_data(legacy_challenge)
    print(f"📊 Analysis Result:")
    print(f"   Format: {analysis3['format']}")
    print(f"   Challenge Type: {analysis3.get('challenge_type', 'Not found')}")
    print(f"   API Path: {analysis3.get('api_path', 'Not found')}")
    print(f"   Has Legacy: {analysis3['has_legacy']}")
    
    # Test case 4: Mixed format (both Bloks and Legacy elements)
    print("\n🔄 Test Case 4: Mixed Format Challenge")
    print("-" * 50)
    
    mixed_challenge = {
        "step_name": "verify_email",
        "step_data": {
            "contact_point": "+1***-***-**45",
            "form_type": "sms"
        },
        "challenge": {
            "api_path": "/challenge/1234567890/AbCdEfGhIj/",
            "challengeType": "VerifySMSCodeForm"
        },
        "nonce_code": "mixed123"
    }
    
    analysis4 = service._analyze_challenge_data(mixed_challenge)
    print(f"📊 Analysis Result:")
    print(f"   Format: {analysis4['format']}")
    print(f"   Step Name: {analysis4['step_name']}")
    print(f"   Contact Point: {analysis4.get('contact_point', 'Not found')}")
    print(f"   Form Type: {analysis4.get('form_type', 'Not found')}")
    print(f"   Contact Hint: {analysis4.get('contact_hint', 'Not found')}")
    print(f"   Has Legacy: {analysis4['has_legacy']}")
    
    # Test case 5: Empty/invalid data
    print("\n❌ Test Case 5: Invalid/Empty Data")
    print("-" * 50)
    
    analysis5 = service._analyze_challenge_data({})
    print(f"📊 Analysis Result:")
    print(f"   Format: {analysis5['format']}")
    print(f"   Error: {analysis5.get('error', 'None')}")
    
    return True

async def test_challenge_resolution_flow():
    """Test the complete challenge resolution flow with enhanced detection"""
    
    print("\n🔄 Enhanced Challenge Resolution Flow Test")
    print("=" * 60)
    
    service = InstagramAPIService()
    
    # Simulate a challenge scenario
    test_username = "test_bloks_user"
    test_code = "123456"
    
    # Create mock challenge data
    mock_challenge_data = {
        "step_name": "verify_email", 
        "step_data": {
            "contact_point": "test@example.com",
            "form_type": "email"
        },
        "nonce_code": "test_nonce_123",
        "challenge_context": "eyJ0ZXN0IjoiZGF0YSJ9",
        "user_id": 12345
    }
    
    # Simulate stored challenge
    service.pending_challenges[test_username] = {
        "challenge_data": mock_challenge_data,
        "attempts": 0,
        "timestamp": "2024-01-01T00:00:00"
    }
    
    print(f"📱 Testing challenge resolution for: {test_username}")
    print(f"📊 Mock challenge data: Bloks format with email verification")
    
    try:
        # This will test our enhanced detection logic
        result = await service.resolve_challenge(test_username, test_code)
        
        print(f"📋 Resolution Result:")
        print(f"   Success: {result.get('success', False)}")
        print(f"   Error: {result.get('error', 'No error')}")
        
        # The result should show that it detected Bloks format
        # Even though it will fail (no actual client), the logs should show correct detection
        
    except Exception as e:
        print(f"⚠️ Expected error (no challenge client): {e}")
    
    print("\n✅ Enhanced detection logic test completed")
    print("   Check the logs above to verify Bloks format detection")
    
    return True

async def main():
    """Run all enhanced challenge detection tests"""
    
    print("🚀 Enhanced Instagram Challenge Detection Test Suite")
    print("=" * 70)
    
    try:
        # Test challenge analysis
        test_challenge_analysis()
        
        # Test challenge resolution flow
        await test_challenge_resolution_flow()
        
        print(f"\n🎉 All Enhanced Challenge Detection Tests Completed!")
        print("=" * 70)
        
        print("\n📝 Key Improvements:")
        print("✅ Enhanced Bloks vs Legacy detection")
        print("✅ Better contact point extraction")
        print("✅ User-friendly challenge messages")
        print("✅ Comprehensive challenge analysis")
        print("✅ Improved logging for debugging")
        
        print("\n🎯 Next Steps:")
        print("1. Test with real Instagram challenges")
        print("2. Verify frontend integration")
        print("3. Monitor production behavior")
        
    except Exception as e:
        print(f"❌ Test suite failed: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(main())
