"""
Unit tests for ranking metrics module.

This test suite validates the implementation of ranking-based evaluation metrics
for recommendation systems including Precision@k, Recall@k, MAP@k, and NDCG@k.

Author: LatentLens Team
"""

import unittest
import numpy as np
import pandas as pd
import sys
import os

# Add src to path
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'src'))

from ranking_metrics import RankingMetrics, create_test_dataset_for_ranking_evaluation, format_ranking_metrics_report


class TestRankingMetrics(unittest.TestCase):
    """Test cases for the RankingMetrics class."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.metrics = RankingMetrics(relevance_threshold=4.0)
        
        # Sample predictions (item_id, predicted_rating) sorted by predicted rating desc
        self.predictions = [
            ("item1", 4.8),  # Relevant
            ("item2", 4.5),  # Relevant  
            ("item3", 3.2),  # Not relevant
            ("item4", 4.1),  # Relevant
            ("item5", 2.8),  # Not relevant
            ("item6", 4.7),  # Relevant
            ("item7", 3.5),  # Not relevant
            ("item8", 4.3),  # Relevant
        ]
        
        # Ground truth ratings
        self.ground_truth = {
            "item1": 4.8,  # Relevant
            "item2": 4.5,  # Relevant
            "item3": 3.2,  # Not relevant
            "item4": 4.1,  # Relevant
            "item5": 2.8,  # Not relevant
            "item6": 4.7,  # Relevant
            "item7": 3.5,  # Not relevant
            "item8": 4.3,  # Relevant
        }
    
    def test_is_relevant(self):
        """Test relevance threshold function."""
        self.assertTrue(self.metrics._is_relevant(4.0))
        self.assertTrue(self.metrics._is_relevant(4.5))
        self.assertTrue(self.metrics._is_relevant(5.0))
        self.assertFalse(self.metrics._is_relevant(3.9))
        self.assertFalse(self.metrics._is_relevant(2.0))
    
    def test_precision_at_k(self):
        """Test Precision@k calculation."""
        # At k=5: items 1,2,3,4,5 -> relevant: 1,2,4 -> 3/5 = 0.6
        precision_5 = self.metrics.precision_at_k(self.predictions, self.ground_truth, 5)
        self.assertAlmostEqual(precision_5, 3/5, places=4)
        
        # At k=2: items 1,2 -> relevant: 1,2 -> 2/2 = 1.0
        precision_2 = self.metrics.precision_at_k(self.predictions, self.ground_truth, 2)
        self.assertAlmostEqual(precision_2, 1.0, places=4)
        
        # At k=0: should return 0
        precision_0 = self.metrics.precision_at_k(self.predictions, self.ground_truth, 0)
        self.assertEqual(precision_0, 0.0)
    
    def test_recall_at_k(self):
        """Test Recall@k calculation."""
        # Total relevant items: 1,2,4,6,8 = 5 items
        # At k=5: items 1,2,3,4,5 -> relevant found: 1,2,4 = 3 items -> 3/5 = 0.6
        recall_5 = self.metrics.recall_at_k(self.predictions, self.ground_truth, 5)
        self.assertAlmostEqual(recall_5, 3/5, places=4)
        
        # At k=8: all items -> relevant found: 1,2,4,6,8 = 5 items -> 5/5 = 1.0
        recall_8 = self.metrics.recall_at_k(self.predictions, self.ground_truth, 8)
        self.assertAlmostEqual(recall_8, 1.0, places=4)
        
        # At k=0: should return 0
        recall_0 = self.metrics.recall_at_k(self.predictions, self.ground_truth, 0)
        self.assertEqual(recall_0, 0.0)
    
    def test_average_precision_at_k(self):
        """Test Average Precision@k calculation."""
        # At k=5: 
        # Position 1: item1 (relevant) -> P@1 = 1/1 = 1.0
        # Position 2: item2 (relevant) -> P@2 = 2/2 = 1.0  
        # Position 3: item3 (not relevant) -> skip
        # Position 4: item4 (relevant) -> P@4 = 3/4 = 0.75
        # Position 5: item5 (not relevant) -> skip
        # AP@5 = (1.0 + 1.0 + 0.75) / min(5, 5) = 2.75 / 5 = 0.55
        ap_5 = self.metrics.average_precision_at_k(self.predictions, self.ground_truth, 5)
        expected_ap = (1.0 + 1.0 + 0.75) / 5  # 5 total relevant items
        self.assertAlmostEqual(ap_5, expected_ap, places=4)
    
    def test_ndcg_at_k(self):
        """Test NDCG@k calculation."""
        # This is a more complex metric, test basic functionality
        ndcg_5 = self.metrics.ndcg_at_k(self.predictions, self.ground_truth, 5)
        self.assertGreaterEqual(ndcg_5, 0.0)
        self.assertLessEqual(ndcg_5, 1.0)
        
        # NDCG should be higher for better rankings
        # Create worse predictions (reverse order)
        worse_predictions = list(reversed(self.predictions))
        ndcg_worse = self.metrics.ndcg_at_k(worse_predictions, self.ground_truth, 5)
        self.assertGreater(ndcg_5, ndcg_worse)
    
    def test_evaluate_user_recommendations(self):
        """Test comprehensive user evaluation."""
        results = self.metrics.evaluate_user_recommendations(
            self.predictions, 
            self.ground_truth, 
            k_values=[5, 10]
        )
        
        # Check structure
        self.assertIn('precision', results)
        self.assertIn('recall', results)
        self.assertIn('average_precision', results)
        self.assertIn('ndcg', results)
        
        # Check k values
        for metric in results.values():
            self.assertIn(5, metric)
            self.assertIn(10, metric)
        
        # Check value ranges
        for metric_name, k_results in results.items():
            for k, value in k_results.items():
                self.assertGreaterEqual(value, 0.0)
                self.assertLessEqual(value, 1.0)
    
    def test_evaluate_model_performance(self):
        """Test model-level evaluation across multiple users."""
        # Create data for multiple users
        all_predictions = {
            "user1": self.predictions,
            "user2": self.predictions[:4],  # Different length
        }
        
        all_ground_truth = {
            "user1": self.ground_truth,
            "user2": {k: v for k, v in list(self.ground_truth.items())[:4]},
        }
        
        results = self.metrics.evaluate_model_performance(
            all_predictions,
            all_ground_truth,
            k_values=[3, 5]
        )
        
        # Check structure
        self.assertIn('precision', results)
        self.assertIn('recall', results)
        
        # Check that we get averages
        for metric_name, k_results in results.items():
            for k, value in k_results.items():
                self.assertIsInstance(value, (int, float))
                self.assertGreaterEqual(value, 0.0)
                self.assertLessEqual(value, 1.0)
    
    def test_empty_ground_truth(self):
        """Test behavior with empty ground truth."""
        empty_gt = {}
        
        precision = self.metrics.precision_at_k(self.predictions, empty_gt, 5)
        recall = self.metrics.recall_at_k(self.predictions, empty_gt, 5)
        ap = self.metrics.average_precision_at_k(self.predictions, empty_gt, 5)
        
        self.assertEqual(precision, 0.0)
        self.assertEqual(recall, 0.0)
        self.assertEqual(ap, 0.0)
    
    def test_no_relevant_items(self):
        """Test behavior when no items are relevant."""
        # All ratings below threshold
        low_ratings = {k: 3.0 for k in self.ground_truth.keys()}
        
        precision = self.metrics.precision_at_k(self.predictions, low_ratings, 5)
        recall = self.metrics.recall_at_k(self.predictions, low_ratings, 5)
        ap = self.metrics.average_precision_at_k(self.predictions, low_ratings, 5)
        
        self.assertEqual(precision, 0.0)
        self.assertEqual(recall, 0.0)
        self.assertEqual(ap, 0.0)


class TestDatasetCreation(unittest.TestCase):
    """Test cases for ranking evaluation dataset creation."""
    
    def setUp(self):
        """Set up test data."""
        # Create sample ratings dataframe
        np.random.seed(42)
        n_users = 100
        n_movies = 50
        n_ratings = 1000
        
        user_ids = np.random.choice(range(1, n_users + 1), n_ratings)
        movie_ids = np.random.choice(range(1, n_movies + 1), n_ratings)
        ratings = np.random.choice([1, 2, 3, 4, 5], n_ratings)
        
        self.ratings_df = pd.DataFrame({
            'userId': user_ids,
            'movieId': movie_ids,
            'rating': ratings
        })
    
    def test_create_test_dataset_for_ranking_evaluation(self):
        """Test creation of train/test split for ranking evaluation."""
        train_df, test_df = create_test_dataset_for_ranking_evaluation(
            self.ratings_df,
            test_size=0.2,
            min_ratings_per_user=5,
            random_state=42
        )
        
        # Check that we have data
        self.assertGreater(len(train_df), 0)
        self.assertGreater(len(test_df), 0)
        
        # Check that train + test <= original (due to filtering)
        self.assertLessEqual(len(train_df) + len(test_df), len(self.ratings_df))
        
        # Check that each user appears in both sets
        train_users = set(train_df['userId'].unique())
        test_users = set(test_df['userId'].unique())
        self.assertEqual(train_users, test_users)
        
        # Check columns are preserved
        expected_cols = ['userId', 'movieId', 'rating']
        self.assertEqual(list(train_df.columns), expected_cols)
        self.assertEqual(list(test_df.columns), expected_cols)


class TestReportFormatting(unittest.TestCase):
    """Test cases for metrics report formatting."""
    
    def test_format_ranking_metrics_report(self):
        """Test metrics report formatting."""
        sample_metrics = {
            'precision': {5: 0.6, 10: 0.5},
            'recall': {5: 0.3, 10: 0.6},
            'average_precision': {5: 0.4, 10: 0.45},
            'ndcg': {5: 0.7, 10: 0.75}
        }
        
        report = format_ranking_metrics_report(sample_metrics, "TestModel")
        
        # Check that report contains expected elements
        self.assertIn("TestModel", report)
        self.assertIn("Precision", report)
        self.assertIn("Recall", report)
        self.assertIn("NDCG", report)
        self.assertIn("@5", report)
        self.assertIn("@10", report)
        self.assertIn("Key Insights", report)
        
        # Check that values are present
        self.assertIn("0.6", report)
        self.assertIn("0.3", report)
        self.assertIn("0.7", report)


if __name__ == '__main__':
    # Run tests
    unittest.main(verbosity=2)
