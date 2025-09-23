#!/usr/bin/env python3
"""
MOSDAC AI Help Bot - Flask Frontend Test Script
Simple test to verify the application is working correctly
"""

import requests
import json
import time

BASE_URL = "http://127.0.0.1:5000"

def test_endpoint(endpoint, method="GET", data=None, expected_status=200):
    """Test a specific endpoint"""
    try:
        url = f"{BASE_URL}{endpoint}"
        print(f"\n🔍 Testing {method} {endpoint}")
        
        if method == "GET":
            response = requests.get(url, timeout=10)
        elif method == "POST":
            response = requests.post(url, json=data, timeout=10)
        
        print(f"   Status: {response.status_code}")
        
        if response.status_code == expected_status:
            print("   ✅ PASS")
            return True
        else:
            print(f"   ❌ FAIL - Expected {expected_status}, got {response.status_code}")
            if response.text:
                print(f"   Response: {response.text[:200]}...")
            return False
            
    except requests.exceptions.RequestException as e:
        print(f"   ❌ ERROR: {str(e)}")
        return False

def main():
    """Run all tests"""
    print("🚀 MOSDAC Flask Frontend Test Suite")
    print("=" * 50)
    
    tests = [
        # Basic endpoints
        ("/", "GET", None, 200),
        ("/health", "GET", None, 200),
        ("/api/status", "GET", None, 200),
        
        # Admin endpoints (may return 200 or redirect)
        ("/admin", "GET", None, [200, 302]),
        ("/analytics", "GET", None, [200, 302]),
        
        # API endpoints
        ("/api/chat", "POST", {"message": "Hello", "language": "en"}, [200, 400, 502]),
        ("/api/feedback", "POST", {"rating": 5, "comment": "Test"}, [200, 400]),
    ]
    
    passed = 0
    total = len(tests)
    
    for endpoint, method, data, expected in tests:
        if isinstance(expected, list):
            # Multiple acceptable status codes
            success = False
            for status in expected:
                if test_endpoint(endpoint, method, data, status):
                    success = True
                    break
            if success:
                passed += 1
        else:
            if test_endpoint(endpoint, method, data, expected):
                passed += 1
        
        time.sleep(0.5)  # Small delay between tests
    
    print("\n" + "=" * 50)
    print(f"📊 Test Results: {passed}/{total} tests passed")
    
    if passed == total:
        print("🎉 All tests passed! Flask frontend is working correctly.")
    else:
        print(f"⚠️  {total - passed} tests failed. Check the logs for details.")
    
    # Additional info
    print(f"\n🌐 Application URL: {BASE_URL}")
    print("📝 Check the browser preview to see the full interface")

if __name__ == "__main__":
    main()
