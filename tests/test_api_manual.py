"""
Test script for the LatentLens API endpoints.
"""

import requests
import json

base_url = "http://127.0.0.1:8000"

def test_health():
    """Test the health endpoint."""
    print("Testing /health endpoint...")
    try:
        response = requests.get(f"{base_url}/health")
        print(f"Status: {response.status_code}")
        print(f"Response: {response.json()}")
        return response.status_code == 200
    except Exception as e:
        print(f"Error: {e}")
        return False

def test_user_recommendations():
    """Test the user recommendations endpoint."""
    print("\nTesting /recommend/123 endpoint...")
    try:
        response = requests.get(f"{base_url}/recommend/123?limit=5")
        print(f"Status: {response.status_code}")
        if response.status_code == 200:
            data = response.json()
            print(f"User ID: {data.get('user_id')}")
            print(f"Total recommendations: {data.get('total_recommendations')}")
            print(f"Recommendation type: {data.get('recommendation_type')}")
            print("First recommendation:")
            if data.get('recommendations'):
                print(f"  {data['recommendations'][0]}")
        else:
            print(f"Error response: {response.text}")
        return response.status_code == 200
    except Exception as e:
        print(f"Error: {e}")
        return False

def test_popular_movies():
    """Test the popular movies endpoint."""
    print("\nTesting /movies/popular endpoint...")
    try:
        response = requests.get(f"{base_url}/movies/popular?limit=3")
        print(f"Status: {response.status_code}")
        if response.status_code == 200:
            data = response.json()
            print(f"Total movies: {data.get('total_movies')}")
            print(f"Recommendation type: {data.get('recommendation_type')}")
            print("First movie:")
            if data.get('movies'):
                print(f"  {data['movies'][0]}")
        else:
            print(f"Error response: {response.text}")
        return response.status_code == 200
    except Exception as e:
        print(f"Error: {e}")
        return False

def test_similar_movies():
    """Test the similar movies endpoint."""
    print("\nTesting /movies/similar endpoint...")
    try:
        response = requests.get(f"{base_url}/movies/similar?movie_title=Toy Story (1995)&limit=3")
        print(f"Status: {response.status_code}")
        if response.status_code == 200:
            data = response.json()
            print(f"Query movie: {data.get('query_movie')}")
            print(f"Total similar movies: {data.get('total_movies')}")
            print(f"Recommendation type: {data.get('recommendation_type')}")
            print("First similar movie:")
            if data.get('similar_movies'):
                print(f"  {data['similar_movies'][0]}")
        else:
            print(f"Error response: {response.text}")
        return response.status_code == 200
    except Exception as e:
        print(f"Error: {e}")
        return False

if __name__ == "__main__":
    print("🎬 LatentLens API Test Suite")
    print("=" * 40)
    
    results = []
    results.append(("Health Check", test_health()))
    results.append(("User Recommendations", test_user_recommendations()))
    results.append(("Popular Movies", test_popular_movies()))
    results.append(("Similar Movies", test_similar_movies()))
    
    print("\n" + "=" * 40)
    print("Test Results Summary:")
    for test_name, passed in results:
        status = "✅ PASS" if passed else "❌ FAIL"
        print(f"{test_name}: {status}")
    
    total_passed = sum(passed for _, passed in results)
    print(f"\nTotal: {total_passed}/{len(results)} tests passed")
