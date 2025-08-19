"""
Simple test for the Hybrid API endpoint
"""

import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'src'))

# Test the API directly
try:
    from fastapi.testclient import TestClient
    from main import app
    
    # Create test client
    client = TestClient(app)
    
    def test_hybrid_api():
        print("Testing Hybrid Recommendation API...")
        
        # Test health endpoint first
        print("\n1. Testing /health endpoint...")
        response = client.get("/health")
        print(f"   Status: {response.status_code}")
        print(f"   Response: {response.json()}")
        
        # Test system status endpoint
        print("\n2. Testing /system/status endpoint...")
        response = client.get("/system/status")
        print(f"   Status: {response.status_code}")
        if response.status_code == 200:
            data = response.json()
            print(f"   Hybrid initialized: {data.get('hybrid_system', {}).get('initialized', False)}")
        else:
            print(f"   Error: {response.text}")
        
        # Test hybrid recommendations endpoint
        print("\n3. Testing /recommend/hybrid/1 endpoint...")
        response = client.get("/recommend/hybrid/1?limit=5")
        print(f"   Status: {response.status_code}")
        if response.status_code == 200:
            data = response.json()
            print(f"   User ID: {data['user_id']}")
            print(f"   Recommendations: {data['total_recommendations']}")
            print(f"   Type: {data['recommendation_type']}")
            
            if data['recommendations']:
                print(f"   Sample recommendation:")
                rec = data['recommendations'][0]
                print(f"      • {rec['title']}")
                print(f"      • Sources: {rec.get('sources', [])}")
                print(f"      • Score: {rec.get('final_score', 0):.4f}")
        else:
            print(f"   Error: {response.text}")
    
    if __name__ == "__main__":
        test_hybrid_api()

except ImportError as e:
    print(f"Import error: {e}")
    print("Note: This test requires the API to be properly set up")
except Exception as e:
    print(f"Error: {e}")
    print("Testing basic hybrid functionality...")
    
    # Fallback to basic test
    print("Running basic component test...")
    
    import data_loader
    print("✅ DataLoader imported successfully")
    
    try:
        import recommendation_service
        print("✅ RecommendationService imported successfully")
    except Exception as e:
        print(f"❌ RecommendationService import failed: {e}")
    
    try:
        import item_similarity_service
        print("✅ ItemSimilarityService imported successfully")  
    except Exception as e:
        print(f"❌ ItemSimilarityService import failed: {e}")
    
    try:
        import content_based_model
        print("✅ ContentBasedModel imported successfully")
    except Exception as e:
        print(f"❌ ContentBasedModel import failed: {e}")
    
    try:
        import hybrid_recommendation_service
        print("✅ HybridRecommendationService imported successfully")
    except Exception as e:
        print(f"❌ HybridRecommendationService import failed: {e}")
    
    print("\n📋 Module imports completed. Fix any errors above to proceed.")
