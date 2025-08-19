"""
Simple test for the API endpoints
"""

import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'src'))

from fastapi.testclient import TestClient
from main import app

# Create test client
client = TestClient(app)

def test_endpoints():
    print("Testing API endpoints...")
    
    # Test health endpoint
    print("\n1. Testing /health endpoint...")
    response = client.get("/health")
    print(f"   Status: {response.status_code}")
    print(f"   Response: {response.json()}")
    
    # Test model status endpoint
    print("\n2. Testing /model/status endpoint...")
    response = client.get("/model/status")
    print(f"   Status: {response.status_code}")
    if response.status_code == 200:
        print(f"   Response: {response.json()}")
    else:
        print(f"   Error: {response.text}")
    
    # Test similar movies endpoint (will trigger model initialization)
    print("\n3. Testing /similar/1 endpoint...")
    response = client.get("/similar/1?limit=3")
    print(f"   Status: {response.status_code}")
    if response.status_code == 200:
        data = response.json()
        print(f"   Query movie: {data['query_movie']['title']}")
        print(f"   Similar movies: {len(data['similar_movies'])}")
        for movie in data['similar_movies']:
            print(f"      • {movie['title']} (similarity: {movie['similarity_score']:.4f})")
    else:
        print(f"   Error: {response.text}")

if __name__ == "__main__":
    test_endpoints()
