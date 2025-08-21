#!/usr/bin/env python3
"""
Test Refactored Recommender Class

This script tests the refactored Recommender class to ensure all strategies
work correctly and the API endpoints function as expected.

Author: LatentLens Team
License: MIT
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from src.recommender import get_recommender
import unittest
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class TestRecommenderRefactoring(unittest.TestCase):
    """Test cases for the refactored Recommender class"""
    
    @classmethod
    def setUpClass(cls):
        """Set up test fixtures before running tests"""
        print("🧪 Setting up Recommender tests...")
        cls.recommender = get_recommender()
        cls.test_user_id = 123
        cls.test_movie_id = 1
        
    def test_collaborative_filtering_strategy(self):
        """Test collaborative filtering strategy"""
        print("\n1️⃣ Testing Collaborative Filtering Strategy...")
        
        result = self.recommender.get_recommendations(
            user_id=self.test_user_id,
            strategy='collaborative',
            n_recommendations=5
        )
        
        self.assertIsInstance(result, dict)
        self.assertEqual(result['user_id'], self.test_user_id)
        self.assertEqual(result['strategy'], 'collaborative')
        self.assertIn('recommendations', result)
        self.assertIn('metadata', result)
        
        print(f"   ✅ Collaborative filtering returned {result['n_recommendations']} recommendations")
    
    def test_hybrid_strategy(self):
        """Test hybrid strategy with automatic cold start handling"""
        print("\n2️⃣ Testing Hybrid Strategy...")
        
        result = self.recommender.get_recommendations(
            user_id=self.test_user_id,
            strategy='hybrid',
            n_recommendations=10
        )
        
        self.assertIsInstance(result, dict)
        self.assertEqual(result['user_id'], self.test_user_id)
        self.assertIn(result['strategy'], ['hybrid', 'cold_start'])  # May switch to cold start
        self.assertIn('recommendations', result)
        self.assertIn('metadata', result)
        
        print(f"   ✅ Hybrid strategy returned {result['n_recommendations']} recommendations")
        print(f"   📊 Strategy used: {result['strategy']}")
        print(f"   🔍 Cold start detected: {result['metadata'].get('cold_start_detected', False)}")
    
    def test_popularity_strategy(self):
        """Test popularity-based strategy"""
        print("\n3️⃣ Testing Popularity Strategy...")
        
        result = self.recommender.get_popular_movies(n_recommendations=8)
        
        self.assertIsInstance(result, dict)
        self.assertEqual(result['strategy'], 'popularity')
        self.assertIn('recommendations', result)
        self.assertIn('metadata', result)
        
        print(f"   ✅ Popularity strategy returned {result['n_recommendations']} recommendations")
    
    def test_cold_start_strategies(self):
        """Test cold start strategies"""
        print("\n4️⃣ Testing Cold Start Strategies...")
        
        strategies = ['popular', 'trending', 'diverse']
        new_user_id = 999999999  # Non-existent user
        
        for strategy in strategies:
            result = self.recommender.get_recommendations(
                user_id=new_user_id,
                strategy='cold_start',
                n_recommendations=5,
                cold_start_strategy=strategy
            )
            
            self.assertIsInstance(result, dict)
            self.assertEqual(result['user_id'], new_user_id)
            self.assertEqual(result['strategy'], 'cold_start')
            self.assertIn('recommendations', result)
            
            print(f"   ✅ Cold start {strategy} strategy returned {result['n_recommendations']} recommendations")
    
    def test_movie_recommendations(self):
        """Test movie-to-movie recommendations"""
        print("\n5️⃣ Testing Movie-to-Movie Recommendations...")
        
        result = self.recommender.get_movie_recommendations(
            movie_id=self.test_movie_id,
            n_recommendations=6,
            strategy='item_similarity'
        )
        
        self.assertIsInstance(result, dict)
        self.assertEqual(result['movie_id'], self.test_movie_id)
        self.assertEqual(result['strategy'], 'item_similarity')
        self.assertIn('recommendations', result)
        self.assertIn('metadata', result)
        
        print(f"   ✅ Item similarity returned {result['n_recommendations']} recommendations")
    
    def test_new_movies_discovery(self):
        """Test new movies discovery functionality"""
        print("\n6️⃣ Testing New Movies Discovery...")
        
        result = self.recommender.get_new_movies(years_back=3, limit=15)
        
        self.assertIsInstance(result, dict)
        self.assertEqual(result['strategy'], 'new_movies')
        self.assertIn('movies', result)
        self.assertIn('metadata', result)
        self.assertEqual(result['years_back'], 3)
        
        print(f"   ✅ New movies discovery returned {result['n_movies']} movies")
        print(f"   📅 Year threshold: {result['threshold_year']}")
    
    def test_system_status(self):
        """Test system status functionality"""
        print("\n7️⃣ Testing System Status...")
        
        result = self.recommender.get_system_status()
        
        self.assertIsInstance(result, dict)
        self.assertIn('recommender_status', result)
        self.assertIn('available_strategies', result)
        self.assertIn('components', result)
        
        print(f"   ✅ System status: {result['recommender_status']}")
        print(f"   🛠️ Available strategies: {len(result['available_strategies'])}")
        print(f"   📦 Components loaded: {len(result['components'])}")
    
    def test_cold_start_detection(self):
        """Test cold start detection logic"""
        print("\n8️⃣ Testing Cold Start Detection...")
        
        # Test with a new user (high ID that likely doesn't exist)
        new_user_id = 999999999
        is_cold_start = self.recommender._is_cold_start_user(new_user_id)
        
        print(f"   🆔 User {new_user_id} is cold start: {is_cold_start}")
        self.assertTrue(is_cold_start)  # Should be True for non-existent user
        
        # Test with an existing user (low ID that likely exists)
        existing_user_id = 1
        is_cold_start_existing = self.recommender._is_cold_start_user(existing_user_id)
        
        print(f"   🆔 User {existing_user_id} is cold start: {is_cold_start_existing}")
        # This might be True or False depending on the user's rating history
    
    def test_strategy_fallback(self):
        """Test strategy fallback mechanism"""
        print("\n9️⃣ Testing Strategy Fallback...")
        
        # Test with an invalid strategy (should raise error)
        try:
            result = self.recommender.get_recommendations(
                user_id=self.test_user_id,
                strategy='invalid_strategy',
                n_recommendations=5
            )
            self.fail("Should have raised ValueError for invalid strategy")
        except ValueError as e:
            print(f"   ✅ Correctly caught invalid strategy error: {str(e)}")
    
    def test_recommender_singleton(self):
        """Test that recommender uses singleton pattern"""
        print("\n🔟 Testing Recommender Singleton...")
        
        recommender1 = get_recommender()
        recommender2 = get_recommender()
        
        self.assertIs(recommender1, recommender2)
        print("   ✅ Recommender correctly implements singleton pattern")


def run_recommender_tests():
    """Run all recommender tests"""
    print("🎯 Testing Refactored Recommender Class")
    print("=" * 50)
    
    # Create test suite
    test_suite = unittest.TestLoader().loadTestsFromTestCase(TestRecommenderRefactoring)
    
    # Run tests
    runner = unittest.TextTestRunner(verbosity=0)  # Set to 0 to reduce unittest output
    result = runner.run(test_suite)
    
    # Summary
    print("\n" + "=" * 50)
    print("📊 Test Results Summary:")
    print(f"   Tests run: {result.testsRun}")
    print(f"   Failures: {len(result.failures)}")
    print(f"   Errors: {len(result.errors)}")
    
    if result.failures:
        print("\n❌ Failures:")
        for test, traceback in result.failures:
            print(f"   - {test}: {traceback}")
    
    if result.errors:
        print("\n💥 Errors:")
        for test, traceback in result.errors:
            print(f"   - {test}: {traceback}")
    
    if result.wasSuccessful():
        print("\n🎉 All tests passed! Recommender refactoring successful!")
        return True
    else:
        print(f"\n❌ {len(result.failures + result.errors)} tests failed!")
        return False


if __name__ == "__main__":
    run_recommender_tests()
