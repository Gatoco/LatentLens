"""
Demo script for Item-to-Item Similarity Service

This script demonstrates the core functionality of the item-to-item
similarity system using the pre-trained model.
"""

import sys
import os
import time

# Add src directory to path
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'src'))

import data_loader
from item_similarity_service import ItemSimilarityService

def demo_item_similarity():
    """Demonstrate the item-to-item similarity functionality."""
    print("=" * 80)
    print("ITEM-TO-ITEM SIMILARITY DEMO")
    print("=" * 80)
    
    # Use the pre-trained model
    data_path = os.path.join(os.path.dirname(__file__), '..', 'data', 'ml-25m')
    
    print(f"Loading pre-trained model from: {data_path}")
    
    # Load the service (should use pre-trained model)
    service = ItemSimilarityService(data_path)
    service.initialize()
    
    # Get model info
    status = service.get_similarity_matrix_info()
    print(f"\n📊 Model Status:")
    print(f"   • Total movies in index: {status['total_movies']:,}")
    print(f"   • Matrix shape: {status['matrix_shape']}")
    print(f"   • Density: {status['matrix_density']:.6f}")
    
    # Demo with famous movies
    demo_movies = [
        (1, "Toy Story"),
        (260, "Star Wars Episode IV"),
        (2571, "The Matrix"),
        (1196, "Star Wars Episode V"),
        (1210, "Star Wars Episode VI")
    ]
    
    print(f"\n🎬 Similarity Demonstrations:")
    
    for movie_id, movie_name in demo_movies:
        try:
            print(f"\n--- Finding movies similar to {movie_name} (ID: {movie_id}) ---")
            
            # Get movie info
            movie_info = service.get_movie_info(movie_id)
            print(f"Title: {movie_info['title']}")
            print(f"Genres: {movie_info['genres']}")
            print(f"Rating: {movie_info['avg_rating']:.2f} ({movie_info['num_ratings']:,} ratings)")
            
            # Get similar movies
            start_time = time.time()
            similar = service.get_similar_items(movie_id, 5)
            query_time = time.time() - start_time
            
            print(f"Query time: {query_time:.4f} seconds")
            print(f"\nTop 5 similar movies:")
            
            for i, sim_movie in enumerate(similar, 1):
                print(f"   {i}. {sim_movie['title']}")
                print(f"      Similarity: {sim_movie['similarity_score']:.4f}")
                print(f"      Rating: {sim_movie['avg_rating']:.2f} ({sim_movie['num_ratings']:,} ratings)")
                print(f"      Genres: {sim_movie['genres']}")
                print()
                
        except Exception as e:
            print(f"   Error: {str(e)}")
    
    # Performance test
    print("\n⚡ Performance Test:")
    test_movie_ids = [1, 260, 2571, 1196, 1210]
    num_queries = 20
    
    start_time = time.time()
    for _ in range(num_queries):
        for movie_id in test_movie_ids:
            service.get_similar_items(movie_id, 10)
    
    total_time = time.time() - start_time
    total_queries = num_queries * len(test_movie_ids)
    
    print(f"   {total_queries} queries in {total_time:.2f} seconds")
    print(f"   Average: {total_time/total_queries:.4f} seconds per query")
    print(f"   Throughput: {total_queries/total_time:.1f} queries/second")
    
    print("\n" + "=" * 80)
    print("✅ DEMO COMPLETED - Item-to-Item Similarity System is operational!")
    print("=" * 80)

if __name__ == "__main__":
    demo_item_similarity()
