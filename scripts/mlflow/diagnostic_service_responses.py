#!/usr/bin/env python3
"""
Service Response Diagnostic Script

This script tests each recommendation service individually to identify
why movie IDs are not being extracted properly in the evaluation.

Author: LatentLens Team
"""

import os
import sys
import json
from pprint import pprint

# Add src to path for imports
sys.path.append(os.path.join(os.path.dirname(__file__), '..', '..'))
sys.path.append(os.path.join(os.path.dirname(__file__), '..', '..', 'src'))

from src.recommender import get_recommender

def test_service_responses():
    """Test each recommendation service and examine response structure"""
    print("🔍 DIAGNOSTIC: Testing Service Response Structures")
    print("=" * 60)
    
    recommender = get_recommender()
    test_user_id = 1
    
    # Test 1: Popularity Model
    print("\n📊 TESTING POPULARITY MODEL:")
    print("-" * 40)
    try:
        popularity_result = recommender.get_popular_movies(n_recommendations=3)
        print(f"Type: {type(popularity_result)}")
        print(f"Keys: {list(popularity_result.keys()) if isinstance(popularity_result, dict) else 'Not a dict'}")
        
        if isinstance(popularity_result, dict) and 'recommendations' in popularity_result:
            recs = popularity_result['recommendations']
            print(f"Recommendations count: {len(recs)}")
            if recs:
                print("First recommendation structure:")
                pprint(recs[0])
                print("All keys in first rec:", list(recs[0].keys()) if isinstance(recs[0], dict) else "Not a dict")
        else:
            print("Full response:")
            pprint(popularity_result)
            
    except Exception as e:
        print(f"ERROR in Popularity: {e}")
    
    # Test 2: Collaborative Model
    print("\n🤝 TESTING COLLABORATIVE MODEL:")
    print("-" * 40)
    try:
        collaborative_result = recommender.get_recommendations(
            user_id=test_user_id,
            strategy="collaborative",
            n_recommendations=3
        )
        print(f"Type: {type(collaborative_result)}")
        print(f"Keys: {list(collaborative_result.keys()) if isinstance(collaborative_result, dict) else 'Not a dict'}")
        
        if isinstance(collaborative_result, dict) and 'recommendations' in collaborative_result:
            recs = collaborative_result['recommendations']
            print(f"Recommendations count: {len(recs)}")
            if recs:
                print("First recommendation structure:")
                pprint(recs[0])
                print("All keys in first rec:", list(recs[0].keys()) if isinstance(recs[0], dict) else "Not a dict")
        else:
            print("Full response:")
            pprint(collaborative_result)
            
    except Exception as e:
        print(f"ERROR in Collaborative: {e}")
    
    # Test 3: Hybrid Model
    print("\n🔄 TESTING HYBRID MODEL:")
    print("-" * 40)
    try:
        hybrid_result = recommender.get_recommendations(
            user_id=test_user_id,
            strategy="hybrid",
            n_recommendations=3
        )
        print(f"Type: {type(hybrid_result)}")
        print(f"Keys: {list(hybrid_result.keys()) if isinstance(hybrid_result, dict) else 'Not a dict'}")
        
        if isinstance(hybrid_result, dict) and 'recommendations' in hybrid_result:
            recs = hybrid_result['recommendations']
            print(f"Recommendations count: {len(recs)}")
            if recs:
                print("First recommendation structure:")
                pprint(recs[0])
                print("All keys in first rec:", list(recs[0].keys()) if isinstance(recs[0], dict) else "Not a dict")
        else:
            print("Full response:")
            pprint(hybrid_result)
            
    except Exception as e:
        print(f"ERROR in Hybrid: {e}")
    
    # Test 4: Check if services return movie_id vs movieId
    print("\n🔑 TESTING MOVIE ID FIELD NAMES:")
    print("-" * 40)
    
    services = [
        ("Popularity", lambda: recommender.get_popular_movies(n_recommendations=1)),
        ("Collaborative", lambda: recommender.get_recommendations(user_id=test_user_id, strategy="collaborative", n_recommendations=1)),
        ("Hybrid", lambda: recommender.get_recommendations(user_id=test_user_id, strategy="hybrid", n_recommendations=1))
    ]
    
    for service_name, service_func in services:
        try:
            result = service_func()
            if isinstance(result, dict) and 'recommendations' in result and result['recommendations']:
                rec = result['recommendations'][0]
                if isinstance(rec, dict):
                    has_movie_id = 'movie_id' in rec
                    has_movieId = 'movieId' in rec
                    movie_id_value = rec.get('movie_id', 'NOT_FOUND')
                    movieId_value = rec.get('movieId', 'NOT_FOUND')
                    
                    print(f"{service_name}:")
                    print(f"  has 'movie_id': {has_movie_id} (value: {movie_id_value})")
                    print(f"  has 'movieId': {has_movieId} (value: {movieId_value})")
                else:
                    print(f"{service_name}: Recommendation is not a dict")
            else:
                print(f"{service_name}: No recommendations found")
        except Exception as e:
            print(f"{service_name}: ERROR - {e}")
    
    print("\n✅ DIAGNOSTIC COMPLETED")
    print("=" * 60)

if __name__ == "__main__":
    test_service_responses()
