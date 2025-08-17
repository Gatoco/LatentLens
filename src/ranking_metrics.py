"""
Ranking Metrics Module for LatentLens

This module provides ranking-based evaluation metrics for recommendation systems.
These metrics focus on the quality of ranked recommendation lists rather than
prediction accuracy, which is more aligned with business objectives.

Metrics implemented:
- Precision@k: Fraction of relevant items in top-k recommendations
- Recall@k: Fraction of relevant items captured in top-k recommendations  
- MAP@k: Mean Average Precision at k
- NDCG@k: Normalized Discounted Cumulative Gain at k

Author: LatentLens Team
License: MIT
"""

import numpy as np
import pandas as pd
from typing import List, Dict, Tuple, Optional, Union
from collections import defaultdict
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class RankingMetrics:
    """
    Class for computing ranking-based evaluation metrics for recommendation systems.
    
    This class provides methods to evaluate the quality of recommendation lists
    by measuring how well they rank relevant items at the top positions.
    """
    
    def __init__(self, relevance_threshold: float = 4.0):
        """
        Initialize the ranking metrics evaluator.
        
        Args:
            relevance_threshold (float): Minimum rating to consider an item relevant.
                Default is 4.0 stars.
        """
        self.relevance_threshold = relevance_threshold
        logger.info(f"RankingMetrics initialized with relevance threshold: {relevance_threshold}")
    
    def _is_relevant(self, rating: float) -> bool:
        """
        Determine if an item is relevant based on its rating.
        
        Args:
            rating (float): The rating value to evaluate.
            
        Returns:
            bool: True if the rating meets the relevance threshold.
        """
        return rating >= self.relevance_threshold
    
    def precision_at_k(
        self, 
        predictions: List[Tuple[str, float]], 
        ground_truth: Dict[str, float], 
        k: int
    ) -> float:
        """
        Calculate Precision@k for a single user's recommendations.
        
        Precision@k = (Number of relevant items in top-k) / k
        
        Args:
            predictions (List[Tuple[str, float]]): List of (item_id, predicted_rating) pairs,
                sorted by predicted rating in descending order.
            ground_truth (Dict[str, float]): Dictionary mapping item_id to actual rating.
            k (int): Number of top recommendations to consider.
            
        Returns:
            float: Precision@k value between 0 and 1.
        """
        if k <= 0:
            return 0.0
        
        # Take top-k predictions
        top_k_items = predictions[:k]
        
        # Count relevant items in top-k
        relevant_count = 0
        for item_id, _ in top_k_items:
            if item_id in ground_truth and self._is_relevant(ground_truth[item_id]):
                relevant_count += 1
        
        return relevant_count / k
    
    def recall_at_k(
        self, 
        predictions: List[Tuple[str, float]], 
        ground_truth: Dict[str, float], 
        k: int
    ) -> float:
        """
        Calculate Recall@k for a single user's recommendations.
        
        Recall@k = (Number of relevant items in top-k) / (Total number of relevant items)
        
        Args:
            predictions (List[Tuple[str, float]]): List of (item_id, predicted_rating) pairs,
                sorted by predicted rating in descending order.
            ground_truth (Dict[str, float]): Dictionary mapping item_id to actual rating.
            k (int): Number of top recommendations to consider.
            
        Returns:
            float: Recall@k value between 0 and 1.
        """
        if k <= 0:
            return 0.0
        
        # Count total relevant items
        total_relevant = sum(1 for rating in ground_truth.values() 
                           if self._is_relevant(rating))
        
        if total_relevant == 0:
            return 0.0
        
        # Take top-k predictions
        top_k_items = predictions[:k]
        
        # Count relevant items in top-k
        relevant_in_topk = 0
        for item_id, _ in top_k_items:
            if item_id in ground_truth and self._is_relevant(ground_truth[item_id]):
                relevant_in_topk += 1
        
        return relevant_in_topk / total_relevant
    
    def average_precision_at_k(
        self, 
        predictions: List[Tuple[str, float]], 
        ground_truth: Dict[str, float], 
        k: int
    ) -> float:
        """
        Calculate Average Precision@k for a single user's recommendations.
        
        AP@k = (1/min(k, R)) * Σ(P@i * rel(i)) for i=1 to k
        where R is the total number of relevant items.
        
        Args:
            predictions (List[Tuple[str, float]]): List of (item_id, predicted_rating) pairs,
                sorted by predicted rating in descending order.
            ground_truth (Dict[str, float]): Dictionary mapping item_id to actual rating.
            k (int): Number of top recommendations to consider.
            
        Returns:
            float: Average Precision@k value between 0 and 1.
        """
        if k <= 0:
            return 0.0
        
        # Count total relevant items
        total_relevant = sum(1 for rating in ground_truth.values() 
                           if self._is_relevant(rating))
        
        if total_relevant == 0:
            return 0.0
        
        # Calculate AP@k
        average_precision = 0.0
        relevant_count = 0
        
        for i, (item_id, _) in enumerate(predictions[:k], 1):
            if item_id in ground_truth and self._is_relevant(ground_truth[item_id]):
                relevant_count += 1
                precision_at_i = relevant_count / i
                average_precision += precision_at_i
        
        return average_precision / min(k, total_relevant)
    
    def ndcg_at_k(
        self, 
        predictions: List[Tuple[str, float]], 
        ground_truth: Dict[str, float], 
        k: int
    ) -> float:
        """
        Calculate Normalized Discounted Cumulative Gain@k for a single user's recommendations.
        
        NDCG@k = DCG@k / IDCG@k
        where DCG@k = Σ(rel_i / log2(i+1)) for i=1 to k
        
        Args:
            predictions (List[Tuple[str, float]]): List of (item_id, predicted_rating) pairs,
                sorted by predicted rating in descending order.
            ground_truth (Dict[str, float]): Dictionary mapping item_id to actual rating.
            k (int): Number of top recommendations to consider.
            
        Returns:
            float: NDCG@k value between 0 and 1.
        """
        if k <= 0:
            return 0.0
        
        # Calculate DCG@k
        dcg = 0.0
        for i, (item_id, _) in enumerate(predictions[:k], 1):
            if item_id in ground_truth:
                relevance = ground_truth[item_id]
                dcg += relevance / np.log2(i + 1)
        
        # Calculate IDCG@k (ideal DCG)
        relevant_ratings = sorted([rating for rating in ground_truth.values()], reverse=True)
        idcg = 0.0
        for i, rating in enumerate(relevant_ratings[:k], 1):
            idcg += rating / np.log2(i + 1)
        
        return dcg / idcg if idcg > 0 else 0.0
    
    def evaluate_user_recommendations(
        self,
        predictions: List[Tuple[str, float]],
        ground_truth: Dict[str, float],
        k_values: List[int] = [5, 10, 20]
    ) -> Dict[str, Dict[int, float]]:
        """
        Evaluate recommendations for a single user across multiple k values.
        
        Args:
            predictions (List[Tuple[str, float]]): List of (item_id, predicted_rating) pairs,
                sorted by predicted rating in descending order.
            ground_truth (Dict[str, float]): Dictionary mapping item_id to actual rating.
            k_values (List[int]): List of k values to evaluate.
            
        Returns:
            Dict[str, Dict[int, float]]: Nested dictionary with metrics and k values.
        """
        results = {
            'precision': {},
            'recall': {},
            'average_precision': {},
            'ndcg': {}
        }
        
        for k in k_values:
            results['precision'][k] = self.precision_at_k(predictions, ground_truth, k)
            results['recall'][k] = self.recall_at_k(predictions, ground_truth, k)
            results['average_precision'][k] = self.average_precision_at_k(predictions, ground_truth, k)
            results['ndcg'][k] = self.ndcg_at_k(predictions, ground_truth, k)
        
        return results
    
    def evaluate_model_performance(
        self,
        all_predictions: Dict[str, List[Tuple[str, float]]],
        all_ground_truth: Dict[str, Dict[str, float]],
        k_values: List[int] = [5, 10, 20]
    ) -> Dict[str, Dict[int, float]]:
        """
        Evaluate model performance across all users.
        
        Args:
            all_predictions (Dict[str, List[Tuple[str, float]]]): Dictionary mapping
                user_id to list of (item_id, predicted_rating) pairs.
            all_ground_truth (Dict[str, Dict[str, float]]): Dictionary mapping
                user_id to dict of {item_id: actual_rating}.
            k_values (List[int]): List of k values to evaluate.
            
        Returns:
            Dict[str, Dict[int, float]]: Average metrics across all users.
        """
        all_metrics = defaultdict(lambda: defaultdict(list))
        
        # Collect metrics for each user
        for user_id in all_predictions:
            if user_id not in all_ground_truth:
                continue
                
            user_metrics = self.evaluate_user_recommendations(
                all_predictions[user_id],
                all_ground_truth[user_id],
                k_values
            )
            
            for metric_name, k_results in user_metrics.items():
                for k, value in k_results.items():
                    all_metrics[metric_name][k].append(value)
        
        # Calculate averages
        avg_metrics = {}
        for metric_name, k_results in all_metrics.items():
            avg_metrics[metric_name] = {}
            for k, values in k_results.items():
                avg_metrics[metric_name][k] = np.mean(values) if values else 0.0
        
        return avg_metrics


def create_test_dataset_for_ranking_evaluation(
    ratings_df: pd.DataFrame,
    test_size: float = 0.2,
    min_ratings_per_user: int = 10,
    random_state: int = 42
) -> Tuple[pd.DataFrame, pd.DataFrame]:
    """
    Create train/test split optimized for ranking evaluation.
    
    This function ensures that each user in the test set has sufficient
    ratings to enable meaningful ranking evaluation.
    
    Args:
        ratings_df (pd.DataFrame): DataFrame with columns ['userId', 'movieId', 'rating'].
        test_size (float): Proportion of ratings to use for testing.
        min_ratings_per_user (int): Minimum number of ratings per user for inclusion.
        random_state (int): Random seed for reproducibility.
        
    Returns:
        Tuple[pd.DataFrame, pd.DataFrame]: (train_df, test_df)
    """
    np.random.seed(random_state)
    
    # Filter users with sufficient ratings
    user_counts = ratings_df['userId'].value_counts()
    valid_users = user_counts[user_counts >= min_ratings_per_user].index
    
    filtered_df = ratings_df[ratings_df['userId'].isin(valid_users)].copy()
    
    logger.info(f"Filtered to {len(valid_users)} users with >= {min_ratings_per_user} ratings")
    logger.info(f"Dataset size: {len(filtered_df)} ratings")
    
    # Split by user to ensure each user appears in both train and test
    train_data = []
    test_data = []
    
    for user_id in valid_users:
        user_ratings = filtered_df[filtered_df['userId'] == user_id]
        n_test = max(1, int(len(user_ratings) * test_size))
        
        # Randomly sample test ratings for this user
        test_indices = np.random.choice(user_ratings.index, size=n_test, replace=False)
        train_indices = user_ratings.index.difference(test_indices)
        
        test_data.append(user_ratings.loc[test_indices])
        train_data.append(user_ratings.loc[train_indices])
    
    train_df = pd.concat(train_data, ignore_index=True)
    test_df = pd.concat(test_data, ignore_index=True)
    
    logger.info(f"Train set: {len(train_df)} ratings")
    logger.info(f"Test set: {len(test_df)} ratings")
    
    return train_df, test_df


def format_ranking_metrics_report(
    metrics: Dict[str, Dict[int, float]],
    model_name: str = "Model"
) -> str:
    """
    Format ranking metrics into a readable report.
    
    Args:
        metrics (Dict[str, Dict[int, float]]): Metrics dictionary from evaluate_model_performance.
        model_name (str): Name of the model being evaluated.
        
    Returns:
        str: Formatted report string.
    """
    report = f"\n*** Ranking Metrics Report - {model_name} ***\n"
    report += "=" * 50 + "\n\n"
    
    # Extract k values
    k_values = sorted(list(metrics['precision'].keys()))
    
    # Create table header
    report += f"{'Metric':<20} " + " ".join([f"@{k:<8}" for k in k_values]) + "\n"
    report += "-" * (20 + len(k_values) * 10) + "\n"
    
    # Add metrics rows
    metric_names = {
        'precision': 'Precision',
        'recall': 'Recall', 
        'average_precision': 'Avg Precision',
        'ndcg': 'NDCG'
    }
    
    for metric_key, metric_display in metric_names.items():
        if metric_key in metrics:
            row = f"{metric_display:<20} "
            for k in k_values:
                value = metrics[metric_key].get(k, 0.0)
                row += f"{value:.4f}   "
            report += row + "\n"
    
    report += "\n*** Key Insights ***\n"
    
    # Find best performing k for each metric
    for metric_key, metric_display in metric_names.items():
        if metric_key in metrics:
            best_k = max(metrics[metric_key].keys(), 
                        key=lambda k: metrics[metric_key][k])
            best_value = metrics[metric_key][best_k]
            report += f"- Best {metric_display}: {best_value:.4f} @{best_k}\n"
    
    return report
