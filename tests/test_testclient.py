"""
Quick test using FastAPI TestClient (no network required)
"""

from fastapi.testclient import TestClient
import sys
import os

# Add src to path
sys.path.append(os.path.join(os.path.dirname(__file__), 'src'))

try:
    from main import app
    
    # Create test client
    client = TestClient(app)
    
    print("🧪 Testing LatentLens Hybrid API with TestClient...")
    
    # Test health endpoint (should be instant)
    print("\n1. Testing /health endpoint...")
    response = client.get("/health")
    print(f"   Status: {response.status_code}")
    print(f"   Response: {response.json()}")
    
    # Test readiness (this will trigger initialization)
    print("\n2. Testing /ready endpoint...")
    print("   (This may take a while as it initializes all services...)")
    response = client.get("/ready", timeout=None)
    print(f"   Status: {response.status_code}")
    
    if response.status_code == 200:
        print(f"   Response: {response.json()}")
        print("   ✅ All services are ready!")
        
        # Test system status
        print("\n3. Testing /system/status endpoint...")
        response = client.get("/system/status")
        print(f"   Status: {response.status_code}")
        data = response.json()
        
        if 'data_stats' in data:
            stats = data['data_stats']
            print(f"   📊 Dataset: {stats['num_users']} users, {stats['num_movies']} movies, {stats['num_ratings']} ratings")
        
        # Test hybrid recommendations
        print("\n4. Testing hybrid recommendations for user 1...")
        response = client.get("/recommend/hybrid/1", params={
            "n_recommendations": 3,
            "collaborative_weight": 0.4,
            "item_similarity_weight": 0.3, 
            "content_based_weight": 0.3
        })
        
        print(f"   Status: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            recommendations = data.get('recommendations', [])
            print(f"   Got {len(recommendations)} recommendations:")
            
            for i, rec in enumerate(recommendations):
                title = rec.get('title', 'Unknown')
                score = rec.get('hybrid_score', 0)
                print(f"     {i+1}. {title} (score: {score:.3f})")
            
            print("   ✅ Hybrid system working perfectly!")
        else:
            error = response.json()
            print(f"   ❌ Error: {error}")
    
    else:
        error = response.json()
        print(f"   ❌ Services not ready: {error}")
    
    print("\n🎉 Test completed!")
    
except Exception as e:
    print(f"❌ Test failed: {e}")
    import traceback
    traceback.print_exc()
