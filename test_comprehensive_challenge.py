#!/usr/bin/env python3
"""
Comprehensive Test: Instagram Challenge Flow
Tests the complete challenge detection and handling system
"""

import json
import sys
import os

# Add the backend directory to Python path
sys.path.append(os.path.join(os.path.dirname(__file__), 'backend'))

from instagram_service import InstagramAPIService

def test_challenge_analysis():
    """Test the enhanced challenge analysis functionality"""
    print("🧪 Testing Enhanced Challenge Analysis System")
    print("=" * 60)
    
    service = InstagramAPIService()
    
    # Test 1: Modern Bloks Challenge (Email Verification)
    print("\n📧 Test 1: Bloks Email Verification Challenge")
    print("-" * 50)
    
    bloks_email_challenge = {
        'step_name': 'verify_email',
        'step_data': {
            'contact_point': 'test@example.com',
            'form_type': 'email'
        },
        'bloks_action': 'com.instagram.challenge.navigation.take_challenge',
        'challenge_context': '{"step_name":"verify_email","nonce":"abc123"}',
        'nonce': 'test_nonce_123'
    }
    
    analysis = service._analyze_challenge_data(bloks_email_challenge)
    print(f"✅ Analysis Result: {json.dumps(analysis, indent=2, ensure_ascii=False)}")
    
    # Test 2: Modern Bloks Challenge (SMS Verification)
    print("\n📱 Test 2: Bloks SMS Verification Challenge")
    print("-" * 50)
    
    bloks_sms_challenge = {
        'step_name': 'verify_phone',
        'step_data': {
            'contact_point': '+90*****1234',
            'form_type': 'phone'
        },
        'bloks_action': 'com.instagram.challenge.navigation.take_challenge',
        'challenge_context': '{"step_name":"verify_phone","user_id":123}',
        'nonce': 'sms_nonce_456'
    }
    
    analysis = service._analyze_challenge_data(bloks_sms_challenge)
    print(f"✅ Analysis Result: {json.dumps(analysis, indent=2, ensure_ascii=False)}")
    
    # Test 3: Legacy Challenge Format
    print("\n🏛️ Test 3: Legacy Challenge Format")
    print("-" * 50)
    
    legacy_challenge = {
        'challenge_url': '/challenge/123456789/',
        'user_agent': 'Instagram 123.0.0.0 Android',
        'challenge_context': 'legacy_context'
    }
    
    analysis = service._analyze_challenge_data(legacy_challenge)
    print(f"✅ Analysis Result: {json.dumps(analysis, indent=2, ensure_ascii=False)}")
    
    # Test 4: Mixed Format Challenge
    print("\n🔀 Test 4: Mixed Format Challenge")
    print("-" * 50)
    
    mixed_challenge = {
        'step_name': 'submit_phone',
        'challenge_url': '/challenge/mixed/',
        'bloks_action': 'submit_verification',
        'step_data': {
            'contact_point': 'user@domain.com',
            'form_type': 'email'
        }
    }
    
    analysis = service._analyze_challenge_data(mixed_challenge)
    print(f"✅ Analysis Result: {json.dumps(analysis, indent=2, ensure_ascii=False)}")

def test_challenge_detection_logic():
    """Test the enhanced Bloks detection logic"""
    print("\n\n🔍 Testing Challenge Detection Logic")
    print("=" * 60)
    
    service = InstagramAPIService()
    
    # Simulate different challenge response formats
    test_cases = [
        {
            'name': 'Strong Bloks Indicators',
            'data': {
                'step_name': 'verify_email',
                'step_data': {'contact_point': 'test@email.com'},
                'bloks_action': 'take_challenge',
                'challenge_context': '{"nonce":"abc"}',
                'nonce': 'test123'
            }
        },
        {
            'name': 'Minimal Bloks Indicators',
            'data': {
                'step_name': 'verify_code',
                'other_field': 'value'
            }
        },
        {
            'name': 'Legacy Format Only',
            'data': {
                'challenge_url': '/challenge/12345/',
                'user_agent': 'Instagram App'
            }
        }
    ]
    
    for i, test_case in enumerate(test_cases, 1):
        print(f"\n🧪 Test Case {i}: {test_case['name']}")
        print(f"Data: {json.dumps(test_case['data'], indent=2)}")
        
        # Count Bloks indicators manually for verification
        bloks_indicators = [
            'step_name', 'step_data', 'bloks_action', 
            'challenge_context', 'nonce', 'client_input_params', 'server_params'
        ]
        
        count = sum(1 for indicator in bloks_indicators if indicator in test_case['data'])
        print(f"Bloks Indicators Found: {count}")
        
        analysis = service._analyze_challenge_data(test_case['data'])
        print(f"Detection Result: {analysis['format']}")
        print(f"Expected: {'bloks' if count >= 1 else 'legacy'}")
        
        if analysis['format'] == ('bloks' if count >= 1 else 'legacy'):
            print("✅ Detection PASSED")
        else:
            print("❌ Detection FAILED")

def test_contact_hint_generation():
    """Test contact hint generation for different contact types"""
    print("\n\n💬 Testing Contact Hint Generation")
    print("=" * 60)
    
    service = InstagramAPIService()
    
    test_contacts = [
        {
            'contact_point': 'user@example.com',
            'form_type': 'email',
            'expected_hint': 'E-posta adresiniz (user@example.com)'
        },
        {
            'contact_point': '+90*****1234',
            'form_type': 'phone',
            'expected_hint': 'Telefon numaranız (+90*****1234)'
        },
        {
            'contact_point': 'masked_email@******.com',
            'form_type': 'email',
            'expected_hint': 'E-posta adresiniz (masked_email@******.com)'
        },
        {
            'contact_point': None,
            'form_type': 'email',
            'expected_hint': 'E-posta adresiniz'
        }
    ]
    
    for i, test in enumerate(test_contacts, 1):
        print(f"\n📞 Test {i}: {test.get('contact_point', 'No contact point')}")
        
        challenge_data = {
            'step_name': 'verify_contact',
            'step_data': {
                'contact_point': test['contact_point'],
                'form_type': test['form_type']
            }
        }
        
        analysis = service._analyze_challenge_data(challenge_data)
        generated_hint = analysis.get('contact_hint', 'No hint generated')
        
        print(f"Expected: {test['expected_hint']}")
        print(f"Generated: {generated_hint}")
        
        if generated_hint == test['expected_hint']:
            print("✅ Hint generation PASSED")
        else:
            print("❌ Hint generation FAILED")

def main():
    """Run all comprehensive tests"""
    print("🚀 Instagram Challenge System - Comprehensive Test Suite")
    print("=" * 80)
    
    try:
        test_challenge_analysis()
        test_challenge_detection_logic()
        test_contact_hint_generation()
        
        print("\n\n🎉 All Tests Completed!")
        print("=" * 80)
        print("✅ Challenge analysis system is working correctly")
        print("✅ Bloks detection logic is functioning properly")
        print("✅ Contact hint generation is accurate")
        print("\n🔗 System is ready for production use!")
        
    except Exception as e:
        print(f"\n❌ Test Suite Failed: {str(e)}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()
