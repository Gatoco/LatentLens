"""
Unit tests for evaluation module.

This test suite validates the comprehensive evaluation framework
that orchestrates traditional accuracy metrics and ranking-based evaluation.

Author: LatentLens Team
"""

import unittest
import numpy as np
import pandas as pd
import sys
import os
from unittest.mock import Mock, patch, MagicMock

# Add src to path
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'src'))

from evaluation import (
    ModelEvaluator, 
    EvaluationPipeline, 
    create_evaluation_dataset,
    quick_rmse_evaluation,
    quick_ranking_evaluation,
    precision_recall_at_k
)


class TestModelEvaluator(unittest.TestCase):
    """Test cases for the ModelEvaluator class."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.evaluator = ModelEvaluator(
            relevance_threshold=4.0,
            k_values=[5, 10],
            cv_folds=3,
            random_state=42
        )
        
        # Create mock model
        self.mock_model = Mock()
        
        # Create sample test data
        self.test_df = pd.DataFrame({
            'userId': [1, 1, 2, 2, 3, 3] * 2,
            'movieId': [101, 102, 103, 104, 105, 106] * 2,
            'rating': [4.5, 3.0, 4.8, 2.5, 5.0, 3.5] * 2
        })
        
        # Create mock testset
        self.mock_testset = [
            (1, 101, 4.5),
            (1, 102, 3.0),
            (2, 103, 4.8)
        ]
    
    def test_initialization(self):
        """Test ModelEvaluator initialization."""
        self.assertEqual(self.evaluator.relevance_threshold, 4.0)
        self.assertEqual(self.evaluator.k_values, [5, 10])
        self.assertEqual(self.evaluator.cv_folds, 3)
        self.assertEqual(self.evaluator.random_state, 42)
        self.assertIsNotNone(self.evaluator.ranking_evaluator)
    
    @patch('evaluation.accuracy')
    def test_evaluate_traditional_metrics(self, mock_accuracy):
        """Test traditional metrics evaluation."""
        # Mock accuracy functions
        mock_accuracy.rmse.return_value = 0.85
        mock_accuracy.mae.return_value = 0.65
        
        # Mock model predictions
        mock_predictions = Mock()
        self.mock_model.test.return_value = mock_predictions
        
        # Test evaluation
        results = self.evaluator.evaluate_traditional_metrics(
            self.mock_model, 
            self.mock_testset,
            metrics=['rmse', 'mae']
        )
        
        # Verify results
        self.assertIn('rmse', results)
        self.assertIn('mae', results)
        self.assertEqual(results['rmse'], 0.85)
        self.assertEqual(results['mae'], 0.65)
        
        # Verify method calls
        self.mock_model.test.assert_called_once_with(self.mock_testset)
        mock_accuracy.rmse.assert_called_once_with(mock_predictions, verbose=False)
        mock_accuracy.mae.assert_called_once_with(mock_predictions, verbose=False)
    
    def test_evaluate_ranking_metrics_structure(self):
        """Test ranking metrics evaluation structure."""
        # Mock model predict method
        def mock_predict(user_id, movie_id):
            prediction = Mock()
            prediction.est = 4.0 + np.random.random()  # Random rating between 4.0-5.0
            return prediction
        
        self.mock_model.predict = mock_predict
        
        # Test ranking evaluation
        ranking_results = self.evaluator.evaluate_ranking_metrics(
            self.mock_model, 
            self.test_df,
            sample_users=2
        )
        
        # Verify structure
        self.assertIsInstance(ranking_results, dict)
        expected_metrics = ['precision', 'recall', 'average_precision', 'ndcg']
        for metric in expected_metrics:
            self.assertIn(metric, ranking_results)
            self.assertIsInstance(ranking_results[metric], dict)
            for k in self.evaluator.k_values:
                self.assertIn(k, ranking_results[metric])
                self.assertIsInstance(ranking_results[metric][k], (int, float))
    
    @patch('evaluation.cross_validate')
    def test_cross_validate_model(self, mock_cross_validate):
        """Test cross-validation functionality."""
        # Mock cross_validate results
        mock_cross_validate.return_value = {
            'test_rmse': [0.8, 0.85, 0.9],
            'test_mae': [0.6, 0.65, 0.7]
        }
        
        # Mock model class and data
        mock_model_class = Mock()
        mock_data = Mock()
        
        # Test cross-validation
        cv_results = self.evaluator.cross_validate_model(
            mock_model_class,
            mock_data,
            model_params={'n_factors': 50},
            metrics=['rmse', 'mae']
        )
        
        # Verify results
        self.assertIn('rmse', cv_results)
        self.assertIn('mae', cv_results)
        self.assertEqual(cv_results['rmse'], [0.8, 0.85, 0.9])
        self.assertEqual(cv_results['mae'], [0.6, 0.65, 0.7])
        
        # Verify cross_validate was called correctly
        mock_cross_validate.assert_called_once()
    
    @patch.object(ModelEvaluator, 'evaluate_ranking_metrics')
    @patch.object(ModelEvaluator, 'evaluate_traditional_metrics')
    def test_comprehensive_evaluation(self, mock_traditional, mock_ranking):
        """Test comprehensive evaluation functionality."""
        # Mock method returns
        mock_traditional.return_value = {'rmse': 0.85, 'mae': 0.65}
        mock_ranking.return_value = {
            'precision': {10: 0.75},
            'recall': {10: 0.80},
            'ndcg': {10: 0.85}
        }
        
        # Test comprehensive evaluation
        results = self.evaluator.comprehensive_evaluation(
            self.mock_model,
            self.mock_testset,
            self.test_df,
            model_name="TestModel",
            include_ranking=True,
            sample_users=50
        )
        
        # Verify structure
        self.assertIn('model_name', results)
        self.assertIn('evaluation_timestamp', results)
        self.assertIn('traditional_metrics', results)
        self.assertIn('ranking_metrics', results)
        self.assertIn('summary', results)
        
        # Verify content
        self.assertEqual(results['model_name'], "TestModel")
        self.assertEqual(results['traditional_metrics'], {'rmse': 0.85, 'mae': 0.65})
        self.assertIn('rmse', results['summary'])
        self.assertIn('precision_at_10', results['summary'])
        
        # Verify method calls
        mock_traditional.assert_called_once()
        mock_ranking.assert_called_once()
    
    def test_compare_models(self):
        """Test model comparison functionality."""
        # Create sample evaluation results
        evaluation_results = [
            {
                'model_name': 'Model_A',
                'evaluation_timestamp': '2025-08-17T10:00:00',
                'traditional_metrics': {'rmse': 0.85, 'mae': 0.65},
                'ranking_metrics': {
                    'precision': {10: 0.75},
                    'recall': {10: 0.80}
                }
            },
            {
                'model_name': 'Model_B',
                'evaluation_timestamp': '2025-08-17T11:00:00',
                'traditional_metrics': {'rmse': 0.90, 'mae': 0.70},
                'ranking_metrics': {
                    'precision': {10: 0.70},
                    'recall': {10: 0.75}
                }
            }
        ]
        
        # Test comparison
        comparison_df = self.evaluator.compare_models(
            evaluation_results,
            primary_metric='rmse',
            ascending=True
        )
        
        # Verify results
        self.assertIsInstance(comparison_df, pd.DataFrame)
        self.assertEqual(len(comparison_df), 2)
        self.assertIn('Model', comparison_df.columns)
        self.assertIn('RMSE', comparison_df.columns)
        
        # Verify sorting (Model_A should be first with lower RMSE)
        self.assertEqual(comparison_df.iloc[0]['Model'], 'Model_A')
        self.assertEqual(comparison_df.iloc[1]['Model'], 'Model_B')
    
    def test_generate_evaluation_report(self):
        """Test evaluation report generation."""
        # Sample evaluation results
        evaluation_results = {
            'model_name': 'TestModel',
            'evaluation_timestamp': '2025-08-17T10:00:00',
            'traditional_metrics': {'rmse': 0.85, 'mae': 0.65},
            'ranking_metrics': {
                'precision': {5: 0.80, 10: 0.75},
                'recall': {5: 0.70, 10: 0.80},
                'ndcg': {5: 0.85, 10: 0.82}
            },
            'summary': {
                'rmse': 0.85,
                'precision_at_10': 0.75,
                'recall_at_10': 0.80
            }
        }
        
        # Generate report
        report = self.evaluator.generate_evaluation_report(evaluation_results)
        
        # Verify report content
        self.assertIsInstance(report, str)
        self.assertIn('TestModel', report)
        self.assertIn('TRADITIONAL METRICS', report)
        self.assertIn('RANKING METRICS', report)
        self.assertIn('SUMMARY', report)
        self.assertIn('0.85', report)  # RMSE value
        self.assertIn('0.75', report)  # Precision@10 value


class TestEvaluationPipeline(unittest.TestCase):
    """Test cases for the EvaluationPipeline class."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.mock_evaluator = Mock(spec=ModelEvaluator)
        self.pipeline = EvaluationPipeline(self.mock_evaluator)
    
    def test_initialization(self):
        """Test EvaluationPipeline initialization."""
        self.assertEqual(self.pipeline.evaluator, self.mock_evaluator)
    
    @patch('evaluation.logger')
    def test_run_model_comparison(self, mock_logger):
        """Test model comparison pipeline."""
        # Mock model class
        mock_model_class = Mock()
        mock_model_instance = Mock()
        mock_model_class.return_value = mock_model_instance
        
        # Mock evaluator comprehensive_evaluation
        self.mock_evaluator.comprehensive_evaluation.return_value = {
            'model_name': 'TestModel',
            'traditional_metrics': {'rmse': 0.85},
            'ranking_metrics': {'precision': {10: 0.75}}
        }
        
        # Mock evaluator compare_models
        mock_comparison_df = pd.DataFrame({'Model': ['TestModel'], 'RMSE': [0.85]})
        self.mock_evaluator.compare_models.return_value = mock_comparison_df
        
        # Test configuration
        models_config = [
            {
                'name': 'TestModel',
                'class': mock_model_class,
                'params': {'n_factors': 50}
            }
        ]
        
        # Mock data
        train_df = pd.DataFrame()
        test_df = pd.DataFrame()
        surprise_trainset = Mock()
        surprise_testset = Mock()
        
        # Run pipeline
        results, comparison_table = self.pipeline.run_model_comparison(
            models_config, train_df, test_df, surprise_trainset, surprise_testset
        )
        
        # Verify results
        self.assertEqual(len(results), 1)
        self.assertIsInstance(comparison_table, pd.DataFrame)
        
        # Verify method calls
        mock_model_instance.fit.assert_called_once_with(surprise_trainset)
        self.mock_evaluator.comprehensive_evaluation.assert_called_once()
        self.mock_evaluator.compare_models.assert_called_once()


class TestUtilityFunctions(unittest.TestCase):
    """Test cases for utility functions."""
    
    def test_create_evaluation_dataset(self):
        """Test evaluation dataset creation."""
        # Create sample ratings data
        ratings_df = pd.DataFrame({
            'userId': [1, 1, 1, 2, 2, 2, 3, 3, 3] * 5,
            'movieId': list(range(101, 146)),
            'rating': np.random.choice([3, 4, 5], size=45)
        })
        
        # Test dataset creation
        train_df, test_df = create_evaluation_dataset(
            ratings_df,
            test_size=0.2,
            min_ratings_per_user=10,
            random_state=42
        )
        
        # Verify results
        self.assertIsInstance(train_df, pd.DataFrame)
        self.assertIsInstance(test_df, pd.DataFrame)
        self.assertGreater(len(train_df), 0)
        self.assertGreater(len(test_df), 0)
        
        # Verify columns
        expected_cols = ['userId', 'movieId', 'rating']
        self.assertEqual(list(train_df.columns), expected_cols)
        self.assertEqual(list(test_df.columns), expected_cols)
    
    @patch('evaluation.accuracy')
    def test_quick_rmse_evaluation(self, mock_accuracy):
        """Test quick RMSE evaluation function."""
        # Mock accuracy.rmse
        mock_accuracy.rmse.return_value = 0.85
        
        # Mock model and testset
        mock_model = Mock()
        mock_predictions = Mock()
        mock_model.test.return_value = mock_predictions
        mock_testset = Mock()
        
        # Test quick RMSE evaluation
        rmse = quick_rmse_evaluation(mock_model, mock_testset)
        
        # Verify results
        self.assertEqual(rmse, 0.85)
        mock_model.test.assert_called_once_with(mock_testset)
        mock_accuracy.rmse.assert_called_once_with(mock_predictions, verbose=False)
    
    @patch('evaluation.ModelEvaluator')
    def test_quick_ranking_evaluation(self, mock_evaluator_class):
        """Test quick ranking evaluation function."""
        # Mock evaluator instance
        mock_evaluator = Mock()
        mock_evaluator_class.return_value = mock_evaluator
        
        # Mock ranking evaluation results
        mock_evaluator.evaluate_ranking_metrics.return_value = {
            'precision': {10: 0.75},
            'recall': {10: 0.80},
            'ndcg': {10: 0.85}
        }
        
        # Test quick ranking evaluation
        mock_model = Mock()
        test_df = pd.DataFrame()
        
        results = quick_ranking_evaluation(
            mock_model, 
            test_df, 
            k=10,
            relevance_threshold=4.0,
            max_users=50
        )
        
        # Verify results
        expected_keys = ['precision_at_10', 'recall_at_10', 'ndcg_at_10']
        for key in expected_keys:
            self.assertIn(key, results)
        
        self.assertEqual(results['precision_at_10'], 0.75)
        self.assertEqual(results['recall_at_10'], 0.80)
        self.assertEqual(results['ndcg_at_10'], 0.85)
        
        # Verify evaluator initialization
        mock_evaluator_class.assert_called_once_with(
            relevance_threshold=4.0, 
            k_values=[10]
        )
        
        # Verify method call
        mock_evaluator.evaluate_ranking_metrics.assert_called_once_with(
            mock_model, test_df, sample_users=50
        )


class TestPrecisionRecallAtK(unittest.TestCase):
    """Test cases for precision_recall_at_k function."""
    
    def setUp(self):
        """Set up test fixtures."""
        # Create mock prediction objects that mimic Surprise predictions
        class MockPrediction:
            def __init__(self, uid, iid, r_ui, est):
                self.uid = uid      # user id
                self.iid = iid      # item id
                self.r_ui = r_ui    # actual rating
                self.est = est      # estimated rating
        
        # Create sample predictions for 2 users
        self.predictions = [
            # User 1: 4 items, 2 relevant (ratings >= 4.0)
            MockPrediction(uid=1, iid=101, r_ui=4.5, est=4.8),  # Relevant, top prediction
            MockPrediction(uid=1, iid=102, r_ui=3.0, est=4.2),  # Not relevant, but high est
            MockPrediction(uid=1, iid=103, r_ui=4.2, est=3.8),  # Relevant, lower est
            MockPrediction(uid=1, iid=104, r_ui=2.5, est=3.5),  # Not relevant, lowest est
            
            # User 2: 3 items, 1 relevant
            MockPrediction(uid=2, iid=201, r_ui=5.0, est=4.9),  # Relevant, top prediction
            MockPrediction(uid=2, iid=202, r_ui=3.5, est=4.1),  # Not relevant
            MockPrediction(uid=2, iid=203, r_ui=2.0, est=3.9),  # Not relevant
        ]
    
    def test_precision_recall_basic_functionality(self):
        """Test basic precision and recall calculation."""
        # Test with k=2, threshold=4.0
        result = precision_recall_at_k(self.predictions, k=2, threshold=4.0)
        
        # Verify structure
        expected_keys = ['precision_at_k', 'recall_at_k', 'num_users', 'k', 'threshold']
        for key in expected_keys:
            self.assertIn(key, result)
        
        # Verify metadata
        self.assertEqual(result['k'], 2)
        self.assertEqual(result['threshold'], 4.0)
        self.assertEqual(result['num_users'], 2)  # Both users have relevant items
        
        # Verify value ranges
        self.assertGreaterEqual(result['precision_at_k'], 0.0)
        self.assertLessEqual(result['precision_at_k'], 1.0)
        self.assertGreaterEqual(result['recall_at_k'], 0.0)
        self.assertLessEqual(result['recall_at_k'], 1.0)
    
    def test_precision_recall_calculation_correctness(self):
        """Test correctness of precision and recall calculations."""
        # Test with k=2, threshold=4.0
        result = precision_recall_at_k(self.predictions, k=2, threshold=4.0)
        
        # Expected calculation:
        # User 1: Top-2 by est_rating are [101(4.8), 102(4.2)]
        #         Relevant items in top-2: 1 (only item 101 has r_ui >= 4.0)
        #         Total relevant items: 2 (items 101, 103)
        #         Precision@2 = 1/2 = 0.5
        #         Recall@2 = 1/2 = 0.5
        
        # User 2: Top-2 by est_rating are [201(4.9), 202(4.1)]
        #         Relevant items in top-2: 1 (only item 201 has r_ui >= 4.0)
        #         Total relevant items: 1 (only item 201)
        #         Precision@2 = 1/2 = 0.5
        #         Recall@2 = 1/1 = 1.0
        
        # Average Precision@2 = (0.5 + 0.5) / 2 = 0.5
        # Average Recall@2 = (0.5 + 1.0) / 2 = 0.75
        
        self.assertAlmostEqual(result['precision_at_k'], 0.5, places=3)
        self.assertAlmostEqual(result['recall_at_k'], 0.75, places=3)
    
    def test_different_k_values(self):
        """Test behavior with different k values."""
        # Test k=1
        result_k1 = precision_recall_at_k(self.predictions, k=1, threshold=4.0)
        
        # Test k=3
        result_k3 = precision_recall_at_k(self.predictions, k=3, threshold=4.0)
        
        # Verify k values are recorded correctly
        self.assertEqual(result_k1['k'], 1)
        self.assertEqual(result_k3['k'], 3)
        
        # Recall should generally increase with larger k (more chance to find relevant items)
        # But precision might decrease (denominator increases)
        self.assertGreaterEqual(result_k3['recall_at_k'], result_k1['recall_at_k'])
    
    def test_different_thresholds(self):
        """Test behavior with different relevance thresholds."""
        # Test with lower threshold (more items considered relevant)
        result_low = precision_recall_at_k(self.predictions, k=2, threshold=3.0)
        
        # Test with higher threshold (fewer items considered relevant)
        result_high = precision_recall_at_k(self.predictions, k=2, threshold=4.5)
        
        # Verify thresholds are recorded correctly
        self.assertEqual(result_low['threshold'], 3.0)
        self.assertEqual(result_high['threshold'], 4.5)
        
        # With lower threshold, more items should be considered relevant
        # So precision and recall might be different
        self.assertIsInstance(result_low['precision_at_k'], float)
        self.assertIsInstance(result_high['precision_at_k'], float)
    
    def test_edge_case_no_relevant_items(self):
        """Test behavior when no users have relevant items."""
        # Create predictions where all ratings are below threshold
        class MockPrediction:
            def __init__(self, uid, iid, r_ui, est):
                self.uid = uid
                self.iid = iid
                self.r_ui = r_ui
                self.est = est
        
        low_rating_predictions = [
            MockPrediction(uid=1, iid=101, r_ui=2.0, est=3.0),
            MockPrediction(uid=1, iid=102, r_ui=2.5, est=2.8),
            MockPrediction(uid=2, iid=201, r_ui=3.0, est=3.2),
        ]
        
        result = precision_recall_at_k(low_rating_predictions, k=2, threshold=4.0)
        
        # Should handle gracefully with no users having relevant items
        self.assertEqual(result['num_users'], 0)
        self.assertEqual(result['precision_at_k'], 0.0)
        self.assertEqual(result['recall_at_k'], 0.0)
    
    def test_edge_case_k_larger_than_items(self):
        """Test behavior when k is larger than number of items per user."""
        # Test with k=10 when users have only 3-4 items each
        result = precision_recall_at_k(self.predictions, k=10, threshold=4.0)
        
        # Should handle gracefully
        self.assertEqual(result['k'], 10)
        self.assertIsInstance(result['precision_at_k'], float)
        self.assertIsInstance(result['recall_at_k'], float)
        
        # Precision should be lower since we're dividing by k=10
        self.assertLessEqual(result['precision_at_k'], 1.0)
    
    def test_edge_case_k_zero(self):
        """Test behavior when k=0."""
        result = precision_recall_at_k(self.predictions, k=0, threshold=4.0)
        
        # Should handle k=0 gracefully
        self.assertEqual(result['k'], 0)
        self.assertEqual(result['precision_at_k'], 0.0)
        # Recall might still be calculated based on total relevant items
    
    def test_single_user(self):
        """Test with predictions for only one user."""
        class MockPrediction:
            def __init__(self, uid, iid, r_ui, est):
                self.uid = uid
                self.iid = iid
                self.r_ui = r_ui
                self.est = est
        
        single_user_predictions = [
            MockPrediction(uid=1, iid=101, r_ui=4.5, est=4.8),
            MockPrediction(uid=1, iid=102, r_ui=3.0, est=4.2),
            MockPrediction(uid=1, iid=103, r_ui=4.2, est=3.8),
        ]
        
        result = precision_recall_at_k(single_user_predictions, k=2, threshold=4.0)
        
        # Should work with single user
        self.assertEqual(result['num_users'], 1)
        self.assertIsInstance(result['precision_at_k'], float)
        self.assertIsInstance(result['recall_at_k'], float)


if __name__ == '__main__':
    # Run tests
    unittest.main(verbosity=2)
