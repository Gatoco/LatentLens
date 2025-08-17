"""
Evaluation Module for LatentLens

This module provides a comprehensive evaluation framework for recommendation systems,
orchestrating different types of evaluations including traditional accuracy metrics
and advanced ranking-based metrics.

This module acts as a high-level coordinator that integrates:
- Traditional metrics (RMSE, MAE) 
- Ranking metrics (Precision@k, Recall@k, NDCG@k)
- Cross-validation procedures
- Model comparison utilities
- Evaluation reporting

Author: LatentLens Team
License: MIT
"""

import os
import sys
import pandas as pd
import numpy as np
from typing import Dict, List, Tuple, Optional, Any, Union
from datetime import datetime
import logging
from collections import defaultdict

# Surprise imports for traditional evaluation
from surprise import accuracy
from surprise.model_selection import cross_validate, KFold

# Local imports
try:
    from .ranking_metrics import RankingMetrics, create_test_dataset_for_ranking_evaluation
except ImportError:
    from ranking_metrics import RankingMetrics, create_test_dataset_for_ranking_evaluation

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class ModelEvaluator:
    """
    Comprehensive model evaluation framework that combines traditional 
    accuracy metrics with advanced ranking-based evaluation.
    """
    
    def __init__(
        self, 
        relevance_threshold: float = 4.0,
        k_values: List[int] = [5, 10, 20],
        cv_folds: int = 5,
        random_state: int = 42
    ):
        """
        Initialize the model evaluator.
        
        Args:
            relevance_threshold (float): Minimum rating to consider an item relevant.
            k_values (List[int]): List of k values for ranking metrics evaluation.
            cv_folds (int): Number of folds for cross-validation.
            random_state (int): Random seed for reproducibility.
        """
        self.relevance_threshold = relevance_threshold
        self.k_values = k_values
        self.cv_folds = cv_folds
        self.random_state = random_state
        
        # Initialize ranking metrics evaluator
        self.ranking_evaluator = RankingMetrics(relevance_threshold=relevance_threshold)
        
        logger.info(f"ModelEvaluator initialized with:")
        logger.info(f"  - Relevance threshold: {relevance_threshold}")
        logger.info(f"  - K values: {k_values}")
        logger.info(f"  - CV folds: {cv_folds}")
    
    def evaluate_traditional_metrics(
        self, 
        model, 
        testset, 
        metrics: List[str] = ['rmse', 'mae']
    ) -> Dict[str, float]:
        """
        Evaluate traditional accuracy metrics (RMSE, MAE, etc.).
        
        Args:
            model: Trained Surprise model.
            testset: Surprise testset for evaluation.
            metrics (List[str]): List of metrics to evaluate.
            
        Returns:
            Dict[str, float]: Dictionary with metric names and values.
        """
        logger.info("Evaluating traditional metrics...")
        
        # Generate predictions
        predictions = model.test(testset)
        
        # Calculate metrics
        results = {}
        
        if 'rmse' in metrics:
            results['rmse'] = accuracy.rmse(predictions, verbose=False)
        
        if 'mae' in metrics:
            results['mae'] = accuracy.mae(predictions, verbose=False)
        
        if 'fcp' in metrics:  # Fraction of Concordant Pairs
            results['fcp'] = accuracy.fcp(predictions, verbose=False)
        
        logger.info(f"Traditional metrics calculated: {list(results.keys())}")
        
        return results
    
    def evaluate_ranking_metrics(
        self, 
        model, 
        test_df: pd.DataFrame,
        sample_users: Optional[int] = None
    ) -> Dict[str, Dict[int, float]]:
        """
        Evaluate ranking-based metrics using the RankingMetrics class.
        
        Args:
            model: Trained Surprise model.
            test_df: Test dataframe with user-item ratings.
            sample_users (Optional[int]): Number of users to sample for evaluation.
                                        If None, uses all users.
            
        Returns:
            Dict[str, Dict[int, float]]: Ranking metrics results.
        """
        logger.info("Evaluating ranking metrics...")
        
        # Get unique users from test set
        test_users = test_df['userId'].unique()
        
        if sample_users is not None and len(test_users) > sample_users:
            np.random.seed(self.random_state)
            test_users = np.random.choice(test_users, size=sample_users, replace=False)
            logger.info(f"Sampled {sample_users} users for ranking evaluation")
        
        # Get all unique movies for generating recommendations
        all_movies = test_df['movieId'].unique()
        
        # Prepare predictions and ground truth for ranking evaluation
        all_predictions = {}
        all_ground_truth = {}
        
        logger.info(f"Processing {len(test_users)} users for ranking evaluation...")
        
        for user_id in test_users:
            # Get user's test ratings (ground truth)
            user_test_data = test_df[test_df['userId'] == user_id]
            ground_truth = dict(zip(user_test_data['movieId'].astype(str), user_test_data['rating']))
            
            # Generate predictions for movies this user has rated in test set
            user_predictions = []
            for movie_id in user_test_data['movieId']:
                pred = model.predict(user_id, movie_id)
                user_predictions.append((str(movie_id), pred.est))
            
            # Sort by predicted rating (descending)
            user_predictions.sort(key=lambda x: x[1], reverse=True)
            
            all_predictions[str(user_id)] = user_predictions
            all_ground_truth[str(user_id)] = ground_truth
        
        # Evaluate ranking metrics
        ranking_results = self.ranking_evaluator.evaluate_model_performance(
            all_predictions, 
            all_ground_truth, 
            k_values=self.k_values
        )
        
        logger.info("Ranking metrics evaluation completed")
        
        return ranking_results
    
    def cross_validate_model(
        self, 
        model_class, 
        data, 
        model_params: Dict[str, Any] = None,
        metrics: List[str] = ['rmse', 'mae']
    ) -> Dict[str, List[float]]:
        """
        Perform cross-validation evaluation with traditional metrics.
        
        Args:
            model_class: Surprise model class (e.g., SVD, KNNBasic).
            data: Surprise Dataset object.
            model_params (Dict[str, Any]): Parameters for model initialization.
            metrics (List[str]): Metrics to evaluate during CV.
            
        Returns:
            Dict[str, List[float]]: CV results for each metric.
        """
        logger.info(f"Performing {self.cv_folds}-fold cross-validation...")
        
        # Initialize model with parameters
        if model_params is None:
            model_params = {}
        
        model = model_class(**model_params)
        
        # Perform cross-validation
        cv_results = cross_validate(
            model, 
            data, 
            measures=metrics,
            cv=KFold(n_splits=self.cv_folds, random_state=self.random_state),
            verbose=False
        )
        
        # Extract results
        results = {}
        for metric in metrics:
            test_metric = f'test_{metric.lower()}'
            if test_metric in cv_results:
                results[metric] = cv_results[test_metric]
        
        logger.info("Cross-validation completed")
        
        return results
    
    def comprehensive_evaluation(
        self,
        model,
        testset,
        test_df: pd.DataFrame,
        model_name: str = "Model",
        include_ranking: bool = True,
        sample_users: Optional[int] = 100
    ) -> Dict[str, Any]:
        """
        Perform comprehensive evaluation combining traditional and ranking metrics.
        
        Args:
            model: Trained Surprise model.
            testset: Surprise testset for traditional metrics.
            test_df: Test dataframe for ranking metrics.
            model_name (str): Name of the model for reporting.
            include_ranking (bool): Whether to include ranking metrics evaluation.
            sample_users (Optional[int]): Number of users to sample for ranking evaluation.
            
        Returns:
            Dict[str, Any]: Comprehensive evaluation results.
        """
        logger.info(f"Starting comprehensive evaluation for {model_name}...")
        
        evaluation_results = {
            'model_name': model_name,
            'evaluation_timestamp': datetime.now().isoformat(),
            'traditional_metrics': {},
            'ranking_metrics': {},
            'summary': {}
        }
        
        # 1. Traditional metrics evaluation
        traditional_results = self.evaluate_traditional_metrics(model, testset)
        evaluation_results['traditional_metrics'] = traditional_results
        
        # 2. Ranking metrics evaluation (if requested)
        if include_ranking:
            ranking_results = self.evaluate_ranking_metrics(model, test_df, sample_users)
            evaluation_results['ranking_metrics'] = ranking_results
        
        # 3. Create summary
        summary = {
            'rmse': traditional_results.get('rmse', None),
            'mae': traditional_results.get('mae', None)
        }
        
        if include_ranking and ranking_results:
            # Add key ranking metrics to summary
            summary['precision_at_10'] = ranking_results.get('precision', {}).get(10, None)
            summary['recall_at_10'] = ranking_results.get('recall', {}).get(10, None)
            summary['ndcg_at_10'] = ranking_results.get('ndcg', {}).get(10, None)
        
        evaluation_results['summary'] = summary
        
        logger.info(f"Comprehensive evaluation completed for {model_name}")
        
        return evaluation_results
    
    def compare_models(
        self,
        evaluation_results: List[Dict[str, Any]],
        primary_metric: str = 'rmse',
        ascending: bool = True
    ) -> pd.DataFrame:
        """
        Compare multiple models based on evaluation results.
        
        Args:
            evaluation_results (List[Dict[str, Any]]): List of evaluation results from comprehensive_evaluation.
            primary_metric (str): Primary metric for ranking models.
            ascending (bool): Whether lower values are better for primary metric.
            
        Returns:
            pd.DataFrame: Comparison table sorted by primary metric.
        """
        logger.info(f"Comparing {len(evaluation_results)} models...")
        
        comparison_data = []
        
        for result in evaluation_results:
            model_data = {
                'Model': result['model_name'],
                'Evaluation_Time': result['evaluation_timestamp']
            }
            
            # Add traditional metrics
            for metric, value in result['traditional_metrics'].items():
                model_data[metric.upper()] = value
            
            # Add ranking metrics summary
            if result['ranking_metrics']:
                ranking_metrics = result['ranking_metrics']
                for metric_name, k_results in ranking_metrics.items():
                    for k, value in k_results.items():
                        model_data[f'{metric_name}_at_{k}'] = value
            
            comparison_data.append(model_data)
        
        # Create DataFrame
        comparison_df = pd.DataFrame(comparison_data)
        
        # Sort by primary metric if it exists
        if primary_metric.upper() in comparison_df.columns:
            comparison_df = comparison_df.sort_values(primary_metric.upper(), ascending=ascending)
        
        logger.info("Model comparison completed")
        
        return comparison_df
    
    def generate_evaluation_report(
        self,
        evaluation_results: Dict[str, Any],
        include_details: bool = True
    ) -> str:
        """
        Generate a formatted evaluation report.
        
        Args:
            evaluation_results (Dict[str, Any]): Results from comprehensive_evaluation.
            include_details (bool): Whether to include detailed metrics breakdown.
            
        Returns:
            str: Formatted evaluation report.
        """
        model_name = evaluation_results['model_name']
        timestamp = evaluation_results['evaluation_timestamp']
        
        report = f"\n*** EVALUATION REPORT - {model_name} ***\n"
        report += "=" * 60 + "\n"
        report += f"Evaluation Time: {timestamp}\n\n"
        
        # Traditional metrics
        report += "TRADITIONAL METRICS\n"
        report += "-" * 25 + "\n"
        for metric, value in evaluation_results['traditional_metrics'].items():
            report += f"{metric.upper():<10}: {value:.4f}\n"
        
        # Ranking metrics
        if evaluation_results['ranking_metrics']:
            report += "\nRANKING METRICS\n"
            report += "-" * 20 + "\n"
            
            ranking_metrics = evaluation_results['ranking_metrics']
            
            # Create table header
            k_values = sorted(list(ranking_metrics['precision'].keys()))
            header = f"{'Metric':<15} " + " ".join([f"@{k:<6}" for k in k_values])
            report += header + "\n"
            report += "-" * len(header) + "\n"
            
            # Add metrics rows
            metric_names = {
                'precision': 'Precision',
                'recall': 'Recall',
                'average_precision': 'Avg Precision',
                'ndcg': 'NDCG'
            }
            
            for metric_key, metric_display in metric_names.items():
                if metric_key in ranking_metrics:
                    row = f"{metric_display:<15} "
                    for k in k_values:
                        value = ranking_metrics[metric_key].get(k, 0.0)
                        row += f"{value:.4f} "
                    report += row + "\n"
        
        # Summary
        report += "\nSUMMARY\n"
        report += "-" * 10 + "\n"
        summary = evaluation_results['summary']
        for metric, value in summary.items():
            if value is not None:
                report += f"{metric:<20}: {value:.4f}\n"
        
        return report


class EvaluationPipeline:
    """
    High-level pipeline for evaluating multiple models with consistent methodology.
    """
    
    def __init__(self, evaluator: ModelEvaluator):
        """
        Initialize evaluation pipeline.
        
        Args:
            evaluator (ModelEvaluator): Configured model evaluator instance.
        """
        self.evaluator = evaluator
        logger.info("EvaluationPipeline initialized")
    
    def run_model_comparison(
        self,
        models_config: List[Dict[str, Any]],
        train_df: pd.DataFrame,
        test_df: pd.DataFrame,
        surprise_trainset,
        surprise_testset
    ) -> Tuple[List[Dict[str, Any]], pd.DataFrame]:
        """
        Run comprehensive evaluation for multiple models.
        
        Args:
            models_config (List[Dict[str, Any]]): List of model configurations.
                Each dict should contain: 'name', 'class', 'params'
            train_df (pd.DataFrame): Training dataframe.
            test_df (pd.DataFrame): Test dataframe.
            surprise_trainset: Surprise trainset object.
            surprise_testset: Surprise testset object.
            
        Returns:
            Tuple[List[Dict[str, Any]], pd.DataFrame]: (evaluation_results, comparison_table)
        """
        logger.info(f"Starting model comparison pipeline with {len(models_config)} models...")
        
        all_results = []
        
        for model_config in models_config:
            model_name = model_config['name']
            model_class = model_config['class']
            model_params = model_config.get('params', {})
            
            logger.info(f"Evaluating model: {model_name}")
            
            # Train model
            model = model_class(**model_params)
            model.fit(surprise_trainset)
            
            # Comprehensive evaluation
            evaluation_result = self.evaluator.comprehensive_evaluation(
                model=model,
                testset=surprise_testset,
                test_df=test_df,
                model_name=model_name,
                include_ranking=True,
                sample_users=100
            )
            
            all_results.append(evaluation_result)
            
            # Print individual report
            report = self.evaluator.generate_evaluation_report(evaluation_result)
            logger.info(f"Completed evaluation for {model_name}")
        
        # Generate comparison table
        comparison_table = self.evaluator.compare_models(all_results, primary_metric='rmse')
        
        logger.info("Model comparison pipeline completed")
        
        return all_results, comparison_table


def create_evaluation_dataset(
    ratings_df: pd.DataFrame,
    test_size: float = 0.2,
    min_ratings_per_user: int = 10,
    random_state: int = 42
) -> Tuple[pd.DataFrame, pd.DataFrame]:
    """
    Create train/test split optimized for both traditional and ranking evaluation.
    
    This is a convenience function that wraps the ranking_metrics implementation.
    
    Args:
        ratings_df (pd.DataFrame): DataFrame with columns ['userId', 'movieId', 'rating'].
        test_size (float): Proportion of ratings to use for testing.
        min_ratings_per_user (int): Minimum number of ratings per user for inclusion.
        random_state (int): Random seed for reproducibility.
        
    Returns:
        Tuple[pd.DataFrame, pd.DataFrame]: (train_df, test_df)
    """
    return create_test_dataset_for_ranking_evaluation(
        ratings_df, test_size, min_ratings_per_user, random_state
    )


# Utility functions for quick evaluation tasks

def quick_rmse_evaluation(model, testset) -> float:
    """
    Quick RMSE evaluation for a model.
    
    Args:
        model: Trained Surprise model.
        testset: Surprise testset.
        
    Returns:
        float: RMSE value.
    """
    predictions = model.test(testset)
    return accuracy.rmse(predictions, verbose=False)


def quick_ranking_evaluation(
    model, 
    test_df: pd.DataFrame, 
    k: int = 10,
    relevance_threshold: float = 4.0,
    max_users: int = 50
) -> Dict[str, float]:
    """
    Quick ranking evaluation for a model.
    
    Args:
        model: Trained Surprise model.
        test_df: Test dataframe.
        k (int): Number of top recommendations to evaluate.
        relevance_threshold (float): Minimum rating to consider relevant.
        max_users (int): Maximum number of users to evaluate.
        
    Returns:
        Dict[str, float]: Dictionary with precision@k, recall@k, ndcg@k.
    """
    evaluator = ModelEvaluator(relevance_threshold=relevance_threshold, k_values=[k])
    ranking_results = evaluator.evaluate_ranking_metrics(model, test_df, sample_users=max_users)
    
    return {
        f'precision_at_{k}': ranking_results['precision'][k],
        f'recall_at_{k}': ranking_results['recall'][k],
        f'ndcg_at_{k}': ranking_results['ndcg'][k]
    }


def precision_recall_at_k(predictions, k: int = 10, threshold: float = 4.0) -> Dict[str, Any]:
    """
    Calculate Precision@k and Recall@k metrics from Surprise predictions.
    
    This function implements the core logic for calculating ranking-based metrics
    from a list of Surprise prediction objects. It groups predictions by user,
    sorts them by estimated rating, and calculates precision and recall metrics.
    
    Args:
        predictions: List of Surprise prediction objects from model.test().
                    Each prediction should have attributes: uid, iid, r_ui, est
        k (int): Number of top recommendations to evaluate. Default is 10.
        threshold (float): Minimum rating threshold to consider an item relevant. Default is 4.0.
    
    Returns:
        Dict[str, Any]: Dictionary containing:
            - 'precision_at_k' (float): Average precision@k across all users
            - 'recall_at_k' (float): Average recall@k across all users  
            - 'num_users' (int): Total number of users evaluated
            - 'k' (int): The k value used for evaluation
            - 'threshold' (float): The relevance threshold used
    
    Example:
        >>> from surprise import SVD, Dataset, Reader
        >>> from surprise.model_selection import train_test_split
        >>> # ... train model and generate predictions ...
        >>> metrics = precision_recall_at_k(predictions, k=10, threshold=4.0)
        >>> print(f"Precision@10: {metrics['precision_at_k']:.4f}")
        >>> print(f"Recall@10: {metrics['recall_at_k']:.4f}")
    """
    logger.info(f"Calculating Precision@{k} and Recall@{k} with threshold={threshold}")
    
    # Group predictions by user
    user_predictions = defaultdict(list)
    
    for prediction in predictions:
        user_id = prediction.uid
        item_id = prediction.iid
        actual_rating = prediction.r_ui
        estimated_rating = prediction.est
        
        user_predictions[user_id].append({
            'item_id': item_id,
            'actual_rating': actual_rating,
            'estimated_rating': estimated_rating
        })
    
    logger.info(f"Processing {len(user_predictions)} users")
    
    # Calculate metrics for each user
    precision_scores = []
    recall_scores = []
    
    for user_id, user_items in user_predictions.items():
        # Sort items by estimated rating in descending order
        user_items.sort(key=lambda x: x['estimated_rating'], reverse=True)
        
        # Calculate total relevant items for this user (across all predictions)
        total_relevant = sum(1 for item in user_items if item['actual_rating'] >= threshold)
        
        # Skip users with no relevant items to avoid division by zero in recall
        if total_relevant == 0:
            continue
        
        # Get top-k recommendations
        top_k_items = user_items[:k]
        
        # Calculate relevant items in top-k recommendations
        relevant_in_top_k = sum(1 for item in top_k_items if item['actual_rating'] >= threshold)
        
        # Calculate Precision@k for this user
        # Precision@k = (relevant items in top-k) / k
        user_precision = relevant_in_top_k / k if k > 0 else 0.0
        
        # Calculate Recall@k for this user  
        # Recall@k = (relevant items in top-k) / (total relevant items)
        user_recall = relevant_in_top_k / total_relevant if total_relevant > 0 else 0.0
        
        precision_scores.append(user_precision)
        recall_scores.append(user_recall)
    
    # Calculate average metrics across all users
    num_users_evaluated = len(precision_scores)
    
    if num_users_evaluated == 0:
        logger.warning("No users with relevant items found for evaluation")
        avg_precision = 0.0
        avg_recall = 0.0
    else:
        avg_precision = np.mean(precision_scores)
        avg_recall = np.mean(recall_scores)
    
    logger.info(f"Evaluation completed for {num_users_evaluated} users")
    logger.info(f"Average Precision@{k}: {avg_precision:.4f}")
    logger.info(f"Average Recall@{k}: {avg_recall:.4f}")
    
    return {
        'precision_at_k': avg_precision,
        'recall_at_k': avg_recall,
        'num_users': num_users_evaluated,
        'k': k,
        'threshold': threshold
    }
