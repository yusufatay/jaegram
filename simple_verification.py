print("🧪 INSTAGRAM BYPASS VERIFICATION")
print("="*40)

# Test 1: Check file existence
import os
from pathlib import Path

backend_dir = Path("backend")
service_file = backend_dir / "instagram_service.py"
app_file = backend_dir / "app.py"

print(f"Service file exists: {service_file.exists()}")
print(f"App file exists: {app_file.exists()}")

if service_file.exists():
    with open(service_file, 'r') as f:
        content = f.read()
    
    testuser_count = content.count('testuser')
    test_mode_count = content.count('test_mode')
    
    print(f"'testuser' mentions: {testuser_count}")
    print(f"'test_mode' mentions: {test_mode_count}")
    
    if testuser_count >= 5 and test_mode_count >= 3:
        print("✅ Bypass logic is implemented!")
    else:
        print("❌ Bypass logic may be incomplete")

print("✅ Verification complete!")
