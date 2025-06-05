#!/usr/bin/env python3
import sys
import os

print("🔧 Simple Test Starting...")

# Add backend to path
sys.path.append(os.path.join(os.path.dirname(__file__), 'backend'))

try:
    from instagram_service import InstagramAPIService
    print("✅ Successfully imported InstagramAPIService")
    
    service = InstagramAPIService()
    print("✅ Successfully created service instance")
    
    # Test the analyze method exists
    if hasattr(service, '_analyze_challenge_data'):
        print("✅ _analyze_challenge_data method exists")
    else:
        print("❌ _analyze_challenge_data method missing")
        
    # Simple test
    test_data = {
        "step_name": "verify_email",
        "nonce_code": "test123"
    }
    
    result = service._analyze_challenge_data(test_data)
    print(f"✅ Analysis result: {result}")
    
    print("🎉 Simple test completed successfully!")
    
except Exception as e:
    print(f"❌ Error: {e}")
    import traceback
    traceback.print_exc()
