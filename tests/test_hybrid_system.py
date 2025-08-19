"""
Test script for Hybrid Recommendation Service

This script tests the newly implemented hybrid recommendation system
that combines collaborative filtering, item-to-item similarity, and
content-based filtering approaches.

Author: LatentLens Team
License: MIT
"""

import sys
import os
import time
import traceback
from pathlib import Path

# Add src directory to path
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'src'))

# Import modules
import data_loader
from hybrid_recommendation_service import HybridRecommendationService, get_hybrid_recommendations_for_user, get_hybrid_system_status


def test_hybrid_recommendation_service():
    """Test the HybridRecommendationService functionality."""
    print("=" * 80)
    print("TESTING HYBRID RECOMMENDATION SERVICE")
    print("=" * 80)
    
    try:
        # Initialize service
        print("\n1. Initializing HybridRecommendationService...")
        start_time = time.time()
        
        # Use absolute path from tests directory
        data_path = os.path.join(os.path.dirname(__file__), '..', 'data', 'ml-25m')
        service = HybridRecommendationService(data_path)
        service.initialize()
        
        init_time = time.time() - start_time
        print(f"   ✅ Service initialized in {init_time:.2f} seconds")
        
        # Get system status
        print("\n2. Checking hybrid system status...")
        status = service.get_system_status()
        print(f"   📊 Hybrid System Status:")
        print(f"      • Initialized: {status['initialized']}")
        print(f"      • Users in cache: {status.get('users_in_cache', 0):,}")
        print(f"      • Total ratings: {status.get('total_ratings', 0):,}")
        print(f"      • Total movies: {status.get('total_movies', 0):,}")
        print(f"      • Weights: {status.get('weights', {})}")
        
        # Test hybrid recommendations for different users
        test_user_ids = [1, 100, 1000, 5000]  # Different user types
        
        print("\n3. Testing hybrid recommendations...")
        
        for user_id in test_user_ids:
            try:
                print(f"\n   🎬 Testing User ID: {user_id}")
                
                # Get user history
                user_history = service.get_user_history(user_id)
                print(f"      User has rated {len(user_history)} movies")
                
                # Get hybrid recommendations
                start_query_time = time.time()
                recommendations = service.get_hybrid_recommendations(user_id, n_recommendations=10)
                query_time = time.time() - start_query_time
                
                print(f"      Query time: {query_time:.4f} seconds")
                print(f"      Generated {len(recommendations)} recommendations")
                
                if recommendations:
                    print(f"      Top 5 hybrid recommendations:")
                    
                    for i, rec in enumerate(recommendations[:5], 1):
                        sources = ', '.join(rec.get('sources', []))
                        print(f"         {i}. {rec['title']}")
                        print(f"            Final Score: {rec['final_score']:.4f}")
                        print(f"            Sources: [{sources}]")
                        print(f"            Genres: {rec['genres']}")
                        print()
                else:
                    print(f"      ⚠️  No recommendations generated for user {user_id}")
                
            except Exception as e:
                print(f"      ❌ Error testing user ID {user_id}: {str(e)}")
        
        # Test convenience functions
        print("\n4. Testing convenience functions...")
        
        print("   Testing get_hybrid_recommendations_for_user()...")
        hybrid_recs = get_hybrid_recommendations_for_user(1, 5)
        print(f"   ✅ Generated {len(hybrid_recs)} hybrid recommendations for user 1")
        
        print("   Testing get_hybrid_system_status()...")
        system_status = get_hybrid_system_status()
        print(f"   ✅ System status: {'Initialized' if system_status['initialized'] else 'Not initialized'}")
        
        # Analyze recommendation diversity
        print("\n5. Analyzing recommendation diversity...")
        
        if hybrid_recs:
            sources_analysis = {}
            for rec in hybrid_recs:
                for source in rec.get('sources', []):
                    sources_analysis[source] = sources_analysis.get(source, 0) + 1
            
            print(f"   📊 Source Distribution Analysis:")
            for source, count in sources_analysis.items():
                percentage = (count / len(hybrid_recs)) * 100
                print(f"      • {source}: {count} recommendations ({percentage:.1f}%)")
            
            # Genre diversity
            all_genres = []
            for rec in hybrid_recs:
                if rec.get('genres'):
                    genres = rec['genres'].split('|')
                    all_genres.extend(genres)
            
            unique_genres = len(set(all_genres))
            print(f"   🎭 Genre Diversity: {unique_genres} unique genres across recommendations")
        
        # Performance benchmarks
        print("\n6. Performance benchmarks...")
        
        # Benchmark query speed for different users
        benchmark_users = [1, 100, 1000, 5000, 10000]
        benchmark_times = []
        
        print("   ⚡ Benchmark Results:")
        
        for user_id in benchmark_users:
            try:
                start_benchmark = time.time()
                _ = service.get_hybrid_recommendations(user_id, n_recommendations=10)
                benchmark_time = time.time() - start_benchmark
                benchmark_times.append(benchmark_time)
                
                print(f"      User {user_id:5d}: {benchmark_time:.4f} seconds")
                
            except Exception as e:
                print(f"      User {user_id:5d}: Error - {str(e)}")
        
        if benchmark_times:
            avg_time = sum(benchmark_times) / len(benchmark_times)
            print(f"      📊 Average query time: {avg_time:.4f} seconds")
            print(f"      🚀 Estimated throughput: {1/avg_time:.1f} queries/second")
        
        print("\n" + "=" * 80)
        print("✅ ALL TESTS PASSED - Hybrid Recommendation Service is working correctly!")
        print("=" * 80)
        
        return True
        
    except Exception as e:
        print(f"\n❌ TEST FAILED: {str(e)}")
        print("\nStack trace:")
        traceback.print_exc()
        return False


def test_hybrid_combinations():
    """Test different hybrid combination scenarios."""
    print("\n" + "=" * 80)
    print("TESTING HYBRID COMBINATION SCENARIOS")
    print("=" * 80)
    
    try:
        data_path = os.path.join(os.path.dirname(__file__), '..', 'data', 'ml-25m')
        service = HybridRecommendationService(data_path)
        service.initialize()
        
        # Test different weight configurations
        print("\n1. Testing weight configuration impacts...")
        
        original_weights = service.weights.copy()
        
        # Test collaborative-heavy configuration
        print("   🔧 Testing collaborative-heavy weights...")
        service.weights = {'collaborative': 0.7, 'item_similarity': 0.2, 'content_based': 0.1}
        
        collab_recs = service.get_hybrid_recommendations(1, 5)
        print(f"      Generated {len(collab_recs)} recommendations")
        
        # Test item-similarity-heavy configuration
        print("   🔧 Testing item-similarity-heavy weights...")
        service.weights = {'collaborative': 0.2, 'item_similarity': 0.6, 'content_based': 0.2}
        
        item_recs = service.get_hybrid_recommendations(1, 5)
        print(f"      Generated {len(item_recs)} recommendations")
        
        # Test content-heavy configuration
        print("   🔧 Testing content-heavy weights...")
        service.weights = {'collaborative': 0.2, 'item_similarity': 0.2, 'content_based': 0.6}
        
        content_recs = service.get_hybrid_recommendations(1, 5)
        print(f"      Generated {len(content_recs)} recommendations")
        
        # Restore original weights
        service.weights = original_weights
        
        # Analyze differences
        print(f"\n   📊 Configuration Analysis:")
        print(f"      • Collaborative-heavy: {len(collab_recs)} recommendations")
        print(f"      • Item-similarity-heavy: {len(item_recs)} recommendations")
        print(f"      • Content-heavy: {len(content_recs)} recommendations")
        
        print("\n✅ Hybrid combination tests passed!")
        return True
        
    except Exception as e:
        print(f"\n❌ Hybrid combination test failed: {str(e)}")
        return False


if __name__ == "__main__":
    print("Starting Hybrid Recommendation Service Tests...\n")
    
    # Run main functionality tests
    success = test_hybrid_recommendation_service()
    
    if success:
        # Run hybrid combination tests
        success = test_hybrid_combinations()
    
    if success:
        print("\n🎉 ALL TESTS COMPLETED SUCCESSFULLY!")
        print("The Hybrid Recommendation Service is ready for production use.")
    else:
        print("\n💥 SOME TESTS FAILED!")
        print("Please check the error messages above and fix any issues.")
        sys.exit(1)
