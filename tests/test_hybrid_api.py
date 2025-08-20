"""
Test script for the Hybrid Recommendation API
"""

import requests
import json

def test_hybrid_api():
    """Test the hybrid recommendation endpoint"""
    base_url = "http://localhost:8000"
    
    print("🔍 Testing Hybrid Recommendation API...")
    
    # Test 1: Health check
    print("\n1. Testing health endpoint...")
    try:
        response = requests.get(f"{base_url}/health")
        print(f"   Status: {response.status_code}")
        print(f"   Response: {response.json()}")
    except Exception as e:
        print(f"   Error: {e}")
    
    # Test 2: System status
    print("\n2. Testing system status...")
    try:
        response = requests.get(f"{base_url}/system/status")
        print(f"   Status: {response.status_code}")
        print(f"   Response: {json.dumps(response.json(), indent=2)}")
    except Exception as e:
        print(f"   Error: {e}")
    
    # Test 3: Hybrid recommendations
    print("\n3. Testing hybrid recommendations...")
    user_id = 1
    try:
        response = requests.get(f"{base_url}/recommend/hybrid/{user_id}")
        print(f"   Status: {response.status_code}")
        data = response.json()
        print(f"   User ID: {data.get('user_id')}")
        print(f"   Total recommendations: {data.get('total_recommendations')}")
        print(f"   Algorithm weights: {data.get('algorithm_weights')}")
        print(f"   First 3 recommendations:")
        for i, rec in enumerate(data.get('recommendations', [])[:3]):
            print(f"     {i+1}. {rec.get('title')} (Score: {rec.get('hybrid_score', 'N/A'):.3f})")
    except Exception as e:
        print(f"   Error: {e}")
    
    # Test 4: Individual algorithm comparison
    print("\n4. Testing individual algorithms...")
    
    # Collaborative filtering
    try:
        response = requests.get(f"{base_url}/recommend/collaborative/{user_id}")
        data = response.json()
        print(f"   Collaborative: {data.get('total_recommendations')} recommendations")
    except Exception as e:
        print(f"   Collaborative error: {e}")
    
    # Item similarity
    try:
        response = requests.get(f"{base_url}/recommend/item-similarity/{user_id}")
        data = response.json()
        print(f"   Item similarity: {data.get('total_recommendations')} recommendations")
    except Exception as e:
        print(f"   Item similarity error: {e}")
    
    # Content-based
    try:
        response = requests.get(f"{base_url}/recommend/content-based/{user_id}")
        data = response.json()
        print(f"   Content-based: {data.get('total_recommendations')} recommendations")
    except Exception as e:
        print(f"   Content-based error: {e}")
    
    print("\n✅ Hybrid API test completed!")

if __name__ == "__main__":
    test_hybrid_api()
