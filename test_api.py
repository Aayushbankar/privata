#!/usr/bin/env python3
"""
Test script for MOSDAC AI Help Bot API.

This script tests all API endpoints to ensure they are working correctly.
Run this script after starting the API server.
"""

import requests
import json
import time
import sys
from typing import Dict, Any, List

# API base URL
BASE_URL = "http://localhost:8000/api/v1"

def test_health_check():
    """Test health check endpoint."""
    print("🧪 Testing health check endpoint...")
    try:
        response = requests.get(f"{BASE_URL}/health")
        if response.status_code == 200:
            print("✅ Health check passed")
            return True
        else:
            print(f"❌ Health check failed: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ Health check error: {e}")
        return False

def test_chat_endpoint():
    """Test chat endpoint."""
    print("🧪 Testing chat endpoint...")
    try:
        payload = {
            "message": "What is MOSDAC?",
            "session_id": "test_session_123"
        }
        response = requests.post(f"{BASE_URL}/chat", json=payload)
        
        if response.status_code == 200:
            data = response.json()
            print(f"✅ Chat response: {data.get('response', 'No response')}")
            return True
        else:
            print(f"❌ Chat failed: {response.status_code} - {response.text}")
            return False
    except Exception as e:
        print(f"❌ Chat error: {e}")
        return False

def test_data_endpoints():
    """Test data management endpoints."""
    print("🧪 Testing data endpoints...")
    
    # Test scraping job creation
    print("  Testing scraping job creation...")
    try:
        payload = {
            "urls": ["https://www.mosdac.gov.in"],
            "max_pages": 10,
            "force_rescrape": False
        }
        response = requests.post(f"{BASE_URL}/data/scrape", json=payload)
        
        if response.status_code == 200:
            data = response.json()
            job_id = data.get("job_id")
            print(f"✅ Scraping job created: {job_id}")
            
            # Test getting job status
            time.sleep(2)  # Wait a bit for job to start
            status_response = requests.get(f"{BASE_URL}/data/scrape/{job_id}")
            if status_response.status_code == 200:
                status_data = status_response.json()
                print(f"✅ Job status: {status_data.get('status')}")
                return True
            else:
                print(f"❌ Job status check failed: {status_response.status_code}")
                return False
        else:
            print(f"❌ Scraping job creation failed: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ Data endpoint error: {e}")
        return False

def test_status_endpoint():
    """Test status endpoint."""
    print("🧪 Testing status endpoint...")
    try:
        response = requests.get(f"{BASE_URL}/status")
        if response.status_code == 200:
            data = response.json()
            print(f"✅ Status: {data.get('status')}")
            print(f"✅ Components: {json.dumps(data.get('components', {}), indent=2)}")
            return True
        else:
            print(f"❌ Status check failed: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ Status error: {e}")
        return False

def test_admin_endpoints():
    """Test admin endpoints."""
    print("🧪 Testing admin endpoints...")
    
    # Test config endpoint
    print("  Testing config endpoint...")
    try:
        response = requests.get(f"{BASE_URL}/admin/config")
        if response.status_code == 200:
            data = response.json()
            print("✅ Config endpoint working")
            
            # Test updating config
            update_payload = {
                "scraping_interval_hours": 24,
                "max_scraping_pages": 500
            }
            update_response = requests.put(f"{BASE_URL}/admin/config", json=update_payload)
            if update_response.status_code == 200:
                print("✅ Config update working")
                return True
            else:
                print(f"❌ Config update failed: {update_response.status_code}")
                return False
        else:
            print(f"❌ Config check failed: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ Admin endpoint error: {e}")
        return False

def test_all_endpoints():
    """Test all API endpoints."""
    print("🚀 Starting comprehensive API tests...")
    print("=" * 50)
    
    tests = [
        ("Health Check", test_health_check),
        ("Status Endpoint", test_status_endpoint),
        ("Chat Endpoint", test_chat_endpoint),
        ("Data Endpoints", test_data_endpoints),
        ("Admin Endpoints", test_admin_endpoints)
    ]
    
    results = []
    for test_name, test_func in tests:
        print(f"\n{test_name}")
        print("-" * len(test_name))
        success = test_func()
        results.append((test_name, success))
        time.sleep(1)  # Brief pause between tests
    
    print("\n" + "=" * 50)
    print("📊 Test Results Summary:")
    print("=" * 50)
    
    all_passed = True
    for test_name, success in results:
        status = "✅ PASS" if success else "❌ FAIL"
        print(f"{status} - {test_name}")
        if not success:
            all_passed = False
    
    print("=" * 50)
    if all_passed:
        print("🎉 All tests passed! API is working correctly.")
    else:
        print("⚠️  Some tests failed. Check the logs above for details.")
    
    return all_passed

def quick_test():
    """Quick test to verify API is running."""
    print("🔍 Quick API availability test...")
    try:
        response = requests.get("http://localhost:8000/", timeout=5)
        if response.status_code == 200:
            print("✅ API server is running")
            return True
        else:
            print(f"❌ API returned status: {response.status_code}")
            return False
    except requests.exceptions.ConnectionError:
        print("❌ API server is not running. Please start the server first.")
        print("   Run: python -m src.api.main")
        return False
    except Exception as e:
        print(f"❌ Error: {e}")
        return False

if __name__ == "__main__":
    # Check if API server is running
    if not quick_test():
        sys.exit(1)
    
    # Run comprehensive tests
    success = test_all_endpoints()
    
    if not success:
        print("\n💡 Troubleshooting tips:")
        print("1. Make sure the API server is running: python -m src.api.main")
        print("2. Check if all dependencies are installed: pip install -r requirements.txt")
        print("3. Verify that ChromaDB and embedding models are properly configured")
        print("4. Check the server logs for any error messages")
    
    sys.exit(0 if success else 1)
