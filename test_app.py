"""
Quick diagnostic script to test the application
"""
import sys
from pathlib import Path

print("=" * 60)
print("Diagnostic Test for Document Analysis System")
print("=" * 60)

# Test 1: Check imports
print("\n1. Testing imports...")
try:
    from main import DocumentAnalyzer
    print("   ✓ DocumentAnalyzer imported successfully")
except Exception as e:
    print(f"   ✗ Failed to import DocumentAnalyzer: {e}")
    sys.exit(1)

# Test 2: Check Flask app
print("\n2. Testing Flask app...")
try:
    from web_app import app, analyzer, processed_documents
    print("   ✓ Flask app imported successfully")
    print(f"   ✓ Analyzer initialized: {analyzer is not None}")
except Exception as e:
    print(f"   ✗ Failed to import Flask app: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)

# Test 3: Check directories
print("\n3. Testing directories...")
upload_dir = Path('data/uploads')
if upload_dir.exists():
    print(f"   ✓ Upload directory exists: {upload_dir}")
else:
    print(f"   ⚠ Upload directory missing, will be created: {upload_dir}")
    upload_dir.mkdir(parents=True, exist_ok=True)
    print(f"   ✓ Created upload directory")

# Test 4: Check analyzer initialization
print("\n4. Testing analyzer...")
if analyzer is None:
    print("   ✗ Analyzer is not initialized!")
    sys.exit(1)
else:
    print("   ✓ Analyzer is initialized")
    print(f"   ✓ Current document ID: {analyzer.current_document_id}")

# Test 5: Test health endpoint
print("\n5. Testing health endpoint...")
try:
    with app.test_client() as client:
        response = client.get('/health')
        if response.status_code == 200:
            print("   ✓ Health endpoint working")
            print(f"   Response: {response.get_json()}")
        else:
            print(f"   ✗ Health endpoint returned status {response.status_code}")
except Exception as e:
    print(f"   ✗ Health endpoint test failed: {e}")
    import traceback
    traceback.print_exc()

print("\n" + "=" * 60)
print("Diagnostic test completed!")
print("=" * 60)
print("\nIf all tests passed, try running: python web_app.py")
print("Then open http://localhost:5000 in your browser")

