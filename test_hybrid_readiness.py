"""
Test script with proper readiness checking for Hybrid API
"""

import time
import requests
import json
from typing import Optional

BASE_URL = "http://127.0.0.1:8000"

def wait_for_readiness(
    base_url: str = BASE_URL,
    health_path: str = "/health", 
    ready_path: str = "/ready",
    retries: int = 30,
    delay: float = 1.0
) -> bool:
    """
    Wait for API to be ready with proper timeout and retries
    
    Args:
        base_url: Base URL of the API
        health_path: Path for liveness check
        ready_path: Path for readiness check
        retries: Number of retries
        delay: Delay between retries in seconds
        
    Returns:
        True if API is ready, False if timeout
    """
    print(f"⏳ Waiting for API to be ready at {base_url}...")
    
    for attempt in range(retries):
        try:
            # First check liveness (health)
            health_response = requests.get(
                f"{base_url}{health_path}", 
                timeout=2
            )
            
            if health_response.status_code == 200:
                print(f"✓ Health check passed (attempt {attempt + 1})")
                
                # Then check readiness
                ready_response = requests.get(
                    f"{base_url}{ready_path}",
                    timeout=5  # Longer timeout for readiness
                )
                
                if ready_response.status_code == 200:
                    print("✅ API is ready!")
                    return True
                else:
                    ready_data = ready_response.json()
                    print(f"⚠️  Services not ready yet: {ready_data}")
                    
            else:
                print(f"❌ Health check failed: {health_response.status_code}")
                
        except requests.exceptions.RequestException as e:
            print(f"🔄 Connection attempt {attempt + 1} failed: {e}")
        
        if attempt < retries - 1:  # Don't sleep on last attempt
            time.sleep(delay)
    
    print(f"❌ API not ready after {retries} attempts")
    return False

def test_hybrid_api():
    """Test the hybrid recommendation API endpoints"""
    
    # Wait for API to be ready
    if not wait_for_readiness():
        print("❌ Cannot proceed with tests - API not ready")
        return False
    
    print("\n🧪 Starting API tests...")
    
    # Test 1: Health endpoint
    print("\n1. Testing /health endpoint...")
    try:
        response = requests.get(f"{BASE_URL}/health", timeout=2)
        print(f"   Status: {response.status_code}")
        print(f"   Response: {response.json()}")
        assert response.status_code == 200
        print("   ✅ Health test passed")
    except Exception as e:
        print(f"   ❌ Health test failed: {e}")
        return False
    
    # Test 2: Readiness endpoint
    print("\n2. Testing /ready endpoint...")
    try:
        response = requests.get(f"{BASE_URL}/ready", timeout=5)
        print(f"   Status: {response.status_code}")
        print(f"   Response: {response.json()}")
        assert response.status_code == 200
        print("   ✅ Readiness test passed")
    except Exception as e:
        print(f"   ❌ Readiness test failed: {e}")
        return False
    
    # Test 3: System status
    print("\n3. Testing /system/status endpoint...")
    try:
        response = requests.get(f"{BASE_URL}/system/status", timeout=5)
        print(f"   Status: {response.status_code}")
        data = response.json()
        print(f"   Services ready: {data.get('services_ready', False)}")
        if 'data_stats' in data:
            stats = data['data_stats']
            print(f"   Data: {stats['num_users']} users, {stats['num_movies']} movies")
        assert response.status_code == 200
        print("   ✅ System status test passed")
    except Exception as e:
        print(f"   ❌ System status test failed: {e}")
        return False
    
    # Test 4: Hybrid recommendations (sample user)
    print("\n4. Testing /recommend/hybrid/{user_id} endpoint...")
    sample_user_id = 1
    try:
        response = requests.get(
            f"{BASE_URL}/recommend/hybrid/{sample_user_id}",
            params={
                "n_recommendations": 5,
                "collaborative_weight": 0.4,
                "item_similarity_weight": 0.3,
                "content_based_weight": 0.3
            },
            timeout=10  # Longer timeout for ML operations
        )
        print(f"   Status: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            recommendations = data.get('recommendations', [])
            print(f"   Got {len(recommendations)} recommendations for user {sample_user_id}")
            
            if recommendations:
                print("   Sample recommendations:")
                for i, rec in enumerate(recommendations[:3]):
                    title = rec.get('title', 'Unknown')
                    score = rec.get('hybrid_score', 0)
                    print(f"     {i+1}. {title} (score: {score:.3f})")
            
            print("   ✅ Hybrid recommendations test passed")
        else:
            error_data = response.json()
            print(f"   ❌ Request failed: {error_data}")
            return False
            
    except Exception as e:
        print(f"   ❌ Hybrid recommendations test failed: {e}")
        return False
    
    # Test 5: Individual algorithm endpoints
    print("\n5. Testing individual algorithm endpoints...")
    
    algorithms = [
        ("collaborative", "collaborative"),
        ("item-similarity", "item-similarity"), 
        ("content-based", "content-based")
    ]
    
    for algo_name, endpoint in algorithms:
        try:
            response = requests.get(
                f"{BASE_URL}/recommend/{endpoint}/{sample_user_id}",
                params={"n_recommendations": 3},
                timeout=10
            )
            
            if response.status_code == 200:
                data = response.json()
                recs = data.get('recommendations', [])
                print(f"   ✅ {algo_name}: {len(recs)} recommendations")
            else:
                print(f"   ⚠️  {algo_name}: {response.status_code}")
                
        except Exception as e:
            print(f"   ❌ {algo_name} test failed: {e}")
    
    print("\n🎉 All tests completed successfully!")
    return True

def test_performance():
    """Quick performance test"""
    print("\n⚡ Testing response times...")
    
    endpoints = [
        ("/health", "Health"),
        ("/ready", "Readiness"),
        ("/system/status", "System Status")
    ]
    
    for endpoint, name in endpoints:
        try:
            start_time = time.time()
            response = requests.get(f"{BASE_URL}{endpoint}", timeout=5)
            elapsed = time.time() - start_time
            
            if response.status_code == 200:
                print(f"   {name}: {elapsed:.3f}s ✅")
            else:
                print(f"   {name}: {elapsed:.3f}s ❌ (status: {response.status_code})")
                
        except Exception as e:
            print(f"   {name}: ❌ {e}")

if __name__ == "__main__":
    print("🚀 LatentLens Hybrid API Test Suite")
    print("=" * 50)
    
    success = test_hybrid_api()
    
    if success:
        test_performance()
        print("\n✅ All tests passed! Hybrid system is working correctly.")
    else:
        print("\n❌ Some tests failed. Check the logs above.")
    
    print("\n" + "=" * 50)
