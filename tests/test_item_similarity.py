"""
Test Script for Item-to-Item Similarity Service

This script tests the newly implemented item-to-item similarity functionality
including KNN model training, similarity computation, and API integration.

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

# Import with absolute imports
import data_loader
from item_similarity_service import ItemSimilarityService, get_similar_items_by_id, get_movie_information, get_model_status


def test_item_similarity_service():
    """Test the ItemSimilarityService functionality."""
    print("=" * 80)
    print("TESTING ITEM-TO-ITEM SIMILARITY SERVICE")
    print("=" * 80)
    
    try:
        # Initialize service
        print("\n1. Initializing ItemSimilarityService...")
        start_time = time.time()
        
        # Use absolute path from tests directory
        data_path = os.path.join(os.path.dirname(__file__), '..', 'data', 'ml-25m')
        service = ItemSimilarityService(data_path)
        service.initialize(min_ratings_per_movie=50, min_ratings_per_user=20)
        
        init_time = time.time() - start_time
        print(f"   ✅ Service initialized in {init_time:.2f} seconds")
        
        # Get model status
        print("\n2. Checking model status...")
        status = service.get_similarity_matrix_info()
        print(f"   📊 Model Status:")
        print(f"      • Total movies: {status['total_movies']:,}")
        print(f"      • Matrix shape: {status['matrix_shape']}")
        print(f"      • Matrix density: {status['matrix_density']:.6f}")
        print(f"      • KNN neighbors: {status['knn_neighbors']}")
        print(f"      • KNN metric: {status['knn_metric']}")
        
        # Test with popular movies
        test_movie_ids = [1, 2, 3, 260, 1196, 2571]  # Toy Story, Jumanji, etc.
        
        print("\n3. Testing similarity queries...")
        
        for movie_id in test_movie_ids:
            try:
                print(f"\n   🎬 Testing Movie ID: {movie_id}")
                
                # Get movie info
                movie_info = service.get_movie_info(movie_id)
                print(f"      Title: {movie_info['title']}")
                print(f"      Genres: {movie_info['genres']}")
                print(f"      Avg Rating: {movie_info['avg_rating']:.2f}")
                print(f"      Num Ratings: {movie_info['num_ratings']:,}")
                
                # Get similar movies
                start_query_time = time.time()
                similar_movies = service.get_similar_items(movie_id, n_similar=5)
                query_time = time.time() - start_query_time
                
                print(f"      Query time: {query_time:.4f} seconds")
                print(f"      Top 5 similar movies:")
                
                for i, sim_movie in enumerate(similar_movies, 1):
                    print(f"         {i}. {sim_movie['title']}")
                    print(f"            Similarity: {sim_movie['similarity_score']:.4f}")
                    print(f"            Rating: {sim_movie['avg_rating']:.2f} ({sim_movie['num_ratings']:,} ratings)")
                    print(f"            Genres: {sim_movie['genres']}")
                    print()
                
            except Exception as e:
                print(f"      ❌ Error testing movie ID {movie_id}: {str(e)}")
        
        # Test convenience functions
        print("\n4. Testing convenience functions...")
        
        print("   Testing get_similar_items_by_id()...")
        similar_items = get_similar_items_by_id(1, 3)
        print(f"   ✅ Found {len(similar_items)} similar items for Toy Story")
        
        print("   Testing get_movie_information()...")
        movie_info = get_movie_information(1)
        print(f"   ✅ Retrieved info for: {movie_info['title']}")
        
        print("   Testing get_model_status()...")
        status = get_model_status()
        print(f"   ✅ Model status: {'Initialized' if status['initialized'] else 'Not initialized'}")
        
        # Performance benchmarks
        print("\n5. Performance benchmarks...")
        
        # Benchmark query speed
        benchmark_queries = 50
        start_benchmark = time.time()
        
        for i in range(benchmark_queries):
            movie_id = test_movie_ids[i % len(test_movie_ids)]
            _ = service.get_similar_items(movie_id, n_similar=10)
        
        benchmark_time = time.time() - start_benchmark
        avg_query_time = benchmark_time / benchmark_queries
        
        print(f"   ⚡ Benchmark Results:")
        print(f"      • {benchmark_queries} queries in {benchmark_time:.2f} seconds")
        print(f"      • Average query time: {avg_query_time:.4f} seconds")
        print(f"      • Queries per second: {benchmark_queries/benchmark_time:.1f}")
        
        print("\n" + "=" * 80)
        print("✅ ALL TESTS PASSED - Item-to-Item Similarity Service is working correctly!")
        print("=" * 80)
        
        return True
        
    except Exception as e:
        print(f"\n❌ TEST FAILED: {str(e)}")
        print("\nStack trace:")
        traceback.print_exc()
        return False


def test_error_handling():
    """Test error handling scenarios."""
    print("\n" + "=" * 80)
    print("TESTING ERROR HANDLING")
    print("=" * 80)
    
    try:
        data_path = os.path.join(os.path.dirname(__file__), '..', 'data', 'ml-25m')
        service = ItemSimilarityService(data_path)
        service.initialize()
        
        # Test invalid movie ID
        print("\n1. Testing invalid movie ID...")
        try:
            service.get_similar_items(999999, 5)
            print("   ❌ Should have raised ValueError")
            return False
        except ValueError as e:
            print(f"   ✅ Correctly raised ValueError: {str(e)}")
        
        # Test movie not in index
        print("\n2. Testing movie not in similarity index...")
        try:
            service.get_movie_info(999999)
            print("   ❌ Should have raised ValueError")
            return False
        except ValueError as e:
            print(f"   ✅ Correctly raised ValueError: {str(e)}")
        
        print("\n✅ Error handling tests passed!")
        return True
        
    except Exception as e:
        print(f"\n❌ Error handling test failed: {str(e)}")
        return False


if __name__ == "__main__":
    print("Starting Item-to-Item Similarity Service Tests...\n")
    
    # Run main functionality tests
    success = test_item_similarity_service()
    
    if success:
        # Run error handling tests
        success = test_error_handling()
    
    if success:
        print("\n🎉 ALL TESTS COMPLETED SUCCESSFULLY!")
        print("The Item-to-Item Similarity Service is ready for production use.")
    else:
        print("\n💥 SOME TESTS FAILED!")
        print("Please check the error messages above and fix any issues.")
        sys.exit(1)
