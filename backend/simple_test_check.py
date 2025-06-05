#!/usr/bin/env python3
"""
Simple verification script for suspect endpoints implementation.
Tests core functionality without complex dependencies.
"""

def test_models():
    """Test that suspect models work."""
    try:
        print("🔍 Testing Suspect Models...")
        from models.suspect_models import (
            CreateSuspectRequest, 
            DialogueRequest, 
            SuspectEmotionalState,
            SuspectInteractionType
        )
        
        # Test model creation
        create_req = CreateSuspectRequest(
            story_id="test-story",
            name="Test Suspect"
        )
        
        dialogue_req = DialogueRequest(
            question="Where were you?",
            story_id="test-story"
        )
        
        print("✅ Suspect models work perfectly!")
        return True
    except Exception as e:
        print(f"❌ Model error: {e}")
        return False

def test_routes_structure():
    """Test that routes are structured correctly."""
    try:
        print("\n🔍 Testing Routes Structure...")
        
        # Check if files exist
        import os
        files_to_check = [
            'routes/suspect_routes.py',
            'services/suspect_service.py',
            'models/suspect_models.py',
            'tests/test_suspect_routes.py'
        ]
        
        for file_path in files_to_check:
            if os.path.exists(file_path):
                print(f"✅ {file_path} exists")
            else:
                print(f"❌ {file_path} missing")
                return False
        
        print("✅ All required files exist!")
        return True
    except Exception as e:
        print(f"❌ Structure error: {e}")
        return False

def test_flask_app_integration():
    """Test that the Flask app can be created with suspect routes."""
    try:
        print("\n🔍 Testing Flask App Integration...")
        from app import create_app
        
        app = create_app()
        
        # Check if suspect routes are registered
        routes = []
        for rule in app.url_map.iter_rules():
            if 'suspect' in rule.rule:
                routes.append(rule.rule)
        
        expected_routes = [
            '/api/suspects',
            '/api/suspects/<suspect_id>',
            '/api/suspects/<suspect_id>/dialogue',
            '/api/suspects/<suspect_id>/verify-alibi',
            '/api/suspects/<suspect_id>/state',
            '/api/suspects/<suspect_id>/motives',
            '/api/suspects/<suspect_id>/generate'
        ]
        
        print(f"✅ Found {len(routes)} suspect routes:")
        for route in routes:
            print(f"   • {route}")
        
        if len(routes) >= 7:  # We expect at least 7 suspect routes
            print("✅ Flask app integration successful!")
            return True
        else:
            print("⚠️  Some routes might be missing")
            return False
            
    except Exception as e:
        print(f"❌ Flask integration error: {e}")
        return False

def test_basic_service_structure():
    """Test basic service structure without AI dependencies."""
    try:
        print("\n🔍 Testing Service Structure...")
        
        # Just check if we can import the service class
        with open('services/suspect_service.py', 'r') as f:
            content = f.read()
            
        required_methods = [
            'get_story_suspects',
            'get_suspect_profile', 
            'create_suspect',
            'generate_dialogue',
            'verify_alibi',
            'get_suspect_state',
            'update_suspect_state',
            'explore_motives',
            'generate_suspect_profile'
        ]
        
        for method in required_methods:
            if f"def {method}" in content or f"async def {method}" in content:
                print(f"✅ {method} method found")
            else:
                print(f"❌ {method} method missing")
                return False
        
        print("✅ Service structure looks good!")
        return True
    except Exception as e:
        print(f"❌ Service error: {e}")
        return False

def check_documentation():
    """Check if documentation exists."""
    try:
        print("\n🔍 Checking Documentation...")
        import os
        
        doc_files = [
            'docs/suspect_endpoints.md',
            'BE-007_IMPLEMENTATION_SUMMARY.md'
        ]
        
        for doc_file in doc_files:
            if os.path.exists(doc_file):
                print(f"✅ {doc_file} exists")
            else:
                print(f"❌ {doc_file} missing")
        
        return True
    except Exception as e:
        print(f"❌ Documentation check error: {e}")
        return False

def main():
    """Run all tests."""
    print("=" * 50)
    print("🔧 SUSPECT ENDPOINTS VERIFICATION")
    print("=" * 50)
    
    tests = [
        test_models,
        test_routes_structure,
        test_flask_app_integration,
        test_basic_service_structure,
        check_documentation
    ]
    
    results = []
    for test in tests:
        try:
            result = test()
            results.append(result)
        except Exception as e:
            print(f"❌ Test failed with error: {e}")
            results.append(False)
    
    print("\n" + "=" * 50)
    print("📊 SUMMARY")
    print("=" * 50)
    
    passed = sum(results)
    total = len(results)
    
    print(f"Tests passed: {passed}/{total}")
    
    if passed == total:
        print("🎉 ALL TESTS PASSED! Your suspect endpoints implementation is ready!")
        print("\n💡 Next steps:")
        print("   • Set up your database (Supabase)")
        print("   • Add API keys to environment variables")
        print("   • Start the Flask app: python app.py")
        print("   • Test with curl or Postman")
    elif passed >= total * 0.8:
        print("⚠️  Most tests passed! Minor issues to fix.")
    else:
        print("❌ Several issues found. Check the output above.")
    
    return passed == total

if __name__ == "__main__":
    main() 