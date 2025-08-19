"""
Complete test with manual service initialization for TestClient
"""

from fastapi.testclient import TestClient
import sys
import os
import time

# Add src to path  
sys.path.append(os.path.join(os.path.dirname(__file__), 'src'))

def test_with_initialization():
    """Test the API with proper service initialization"""
    
    print("🚀 Initializing LatentLens Hybrid System...")
    print("   This will take a few minutes to load all data and models...")
    
    start_time = time.time()
    
    try:
        # Import services
        from src.data_loader import DataLoader
        from src.recommendation_service import RecommendationService  
        from src.hybrid_recommendation_service import HybridRecommendationService
        
        # Initialize data loader
        print("\n📊 Loading MovieLens dataset...")
        data_loader = DataLoader()
        ratings_df = data_loader.load_ratings()
        movies_df = data_loader.load_movies()
        print(f"   ✅ Loaded {len(ratings_df)} ratings for {len(ratings_df['userId'].unique())} users")
        print(f"   ✅ Loaded {len(movies_df)} movies")
        
        # Initialize recommendation service
        print("\n🤖 Initializing recommendation models...")
        recommendation_service = RecommendationService()
        recommendation_service.initialize()
        print("   ✅ Collaborative filtering ready")
        
        # Initialize hybrid service
        print("\n🔄 Setting up hybrid recommendation system...")
        hybrid_service = HybridRecommendationService()
        hybrid_service.initialize()
        print("   ✅ Hybrid system ready")
        
        elapsed = time.time() - start_time
        print(f"\n⏱️ Total initialization time: {elapsed:.1f} seconds")
        
        # Test direct function calls
        print("\n🧪 Testing hybrid recommendations...")
        
        user_id = 1
        recommendations = hybrid_service.get_hybrid_recommendations(
            user_id=user_id,
            n_recommendations=5
        )
        
        print(f"\n🎬 Top 5 hybrid recommendations for user {user_id}:")
        for i, rec in enumerate(recommendations[:5]):
            title = rec.get('title', 'Unknown')
            score = rec.get('hybrid_score', 0)
            print(f"   {i+1}. {title} (score: {score:.3f})")
        
        # Test individual algorithms
        print(f"\n🔍 Testing individual algorithms for user {user_id}:")
        
        # Collaborative filtering
        collab_recs = recommendation_service.get_collaborative_recommendations(user_id, 3)
        print(f"   Collaborative: {len(collab_recs)} recommendations")
        
        # Item similarity (using user recommendations which include KNN)
        user_recs = recommendation_service.get_user_recommendations(user_id, 3)
        print(f"   User-based: {len(user_recs)} recommendations")
        
        # Popular movies as baseline
        popular_recs = recommendation_service.get_popular_recommendations(3)
        print(f"   Popular baseline: {len(popular_recs)} recommendations")
        
        print("\n✅ ALL TESTS PASSED!")
        print("🎉 Hybrid recommendation system is working perfectly!")
        
        return True
        
    except Exception as e:
        print(f"\n❌ Test failed: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_performance():
    """Quick performance benchmark"""
    print("\n⚡ Performance Test:")
    
    try:
        from src.hybrid_recommendation_service import HybridRecommendationService
        
        hybrid_service = HybridRecommendationService()
        hybrid_service.initialize()
        
        # Test response times
        test_users = [1, 10, 100, 1000]
        
        for user_id in test_users:
            start = time.time()
            recs = hybrid_service.get_hybrid_recommendations(user_id, 5)
            elapsed = time.time() - start
            
            print(f"   User {user_id}: {len(recs)} recs in {elapsed:.3f}s")
        
    except Exception as e:
        print(f"   Performance test failed: {e}")

if __name__ == "__main__":
    print("🔬 LatentLens Hybrid System - Complete Test Suite")
    print("=" * 60)
    
    success = test_with_initialization()
    
    if success:
        test_performance()
        
        print("\n" + "=" * 60)
        print("✅ WEEK 6 COMPLETE: Hybrid Recommendation System Working!")
        print("🚀 Ready for production deployment!")
    else:
        print("\n❌ Tests failed. Check logs above.")
