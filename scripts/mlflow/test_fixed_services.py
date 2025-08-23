#!/usr/bin/env python3
"""
Quick Fix Verification Script

Test the corrected recommendation services to verify movieId inclusion.
"""

import os
import sys
from pprint import pprint

# Add src to path for imports
sys.path.append(os.path.join(os.path.dirname(__file__), '..', '..'))
sys.path.append(os.path.join(os.path.dirname(__file__), '..', '..', 'src'))

from recommender import get_recommender

def test_fixed_services():
    """Test the fixed recommendation services"""
    print("🔧 TESTING FIXED SERVICES:")
    print("=" * 50)
    
    recommender = get_recommender()
    
    # Test 1: Popularity Model
    print("\n📊 POPULARITY MODEL (FIXED):")
    print("-" * 30)
    try:
        result = recommender.get_popular_movies(n_recommendations=2)
        if result and 'recommendations' in result:
            for i, rec in enumerate(result['recommendations'][:2]):
                print(f"Rec {i+1}:")
                print(f"  movieId: {rec.get('movieId', 'MISSING')}")
                print(f"  title: {rec.get('title', 'MISSING')}")
                print(f"  rating: {rec.get('average_rating', 'MISSING')}")
                
    except Exception as e:
        print(f"ERROR: {e}")
    
    # Test 2: Collaborative Model
    print("\n🤝 COLLABORATIVE MODEL (FIXED):")
    print("-" * 30)
    try:
        result = recommender.get_recommendations(
            user_id=1,
            strategy="collaborative",
            n_recommendations=2
        )
        if result and 'recommendations' in result:
            for i, rec in enumerate(result['recommendations'][:2]):
                print(f"Rec {i+1}:")
                print(f"  movieId: {rec.get('movieId', 'MISSING')}")
                print(f"  title: {rec.get('title', 'MISSING')}")
                print(f"  rating: {rec.get('average_rating', 'MISSING')}")
                
    except Exception as e:
        print(f"ERROR: {e}")
    
    print("\n✅ FIX VERIFICATION COMPLETED")

if __name__ == "__main__":
    test_fixed_services()
