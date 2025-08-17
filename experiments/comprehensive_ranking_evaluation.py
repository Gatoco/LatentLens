"""
Advanced Ranking Evaluation with Larger Dataset

This script runs a comprehensive evaluation of ranking metrics with a more substantial 
dataset to demonstrate meaningful metric values and comparison between algorithms.

Author: LatentLens Team
"""

import os
import sys
import pandas as pd
import numpy as np
from datetime import datetime
import mlflow
import mlflow.sklearn
from mlflow.tracking import MlflowClient
from surprise import SVD, KNNBasic, Dataset, Reader, accuracy
import logging

# Add src to path for imports
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'src'))

from data_loader import DataLoader
from ranking_metrics import RankingMetrics, create_test_dataset_for_ranking_evaluation, format_ranking_metrics_report

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)


def run_comprehensive_ranking_experiment(sample_size: int = 100000):
    """
    Run comprehensive ranking evaluation experiment.
    
    Args:
        sample_size: Number of ratings to use for the experiment.
    """
    logger.info("*** Starting Comprehensive Ranking Evaluation Experiment ***")
    
    # Set MLflow tracking
    mlflow.set_tracking_uri("http://127.0.0.1:5000")
    
    experiment_name = "Ranking-Metrics-Comparison"
    try:
        experiment_id = mlflow.create_experiment(experiment_name)
    except mlflow.exceptions.MlflowException:
        experiment_id = mlflow.get_experiment_by_name(experiment_name).experiment_id
    
    mlflow.set_experiment(experiment_name)
    
    # Load and prepare data
    logger.info("Loading and preparing data...")
    data_loader = DataLoader()
    ratings_df = data_loader.load_ratings()
    
    logger.info(f"Original dataset: {len(ratings_df)} ratings")
    
    # Sample for performance
    if len(ratings_df) > sample_size:
        ratings_df = ratings_df.sample(n=sample_size, random_state=42)
        logger.info(f"Sampled to {sample_size} ratings")
    
    # Create train/test split optimized for ranking evaluation
    train_df, test_df = create_test_dataset_for_ranking_evaluation(
        ratings_df, 
        test_size=0.2, 
        min_ratings_per_user=20,  # Higher threshold for better evaluation
        random_state=42
    )
    
    # Prepare Surprise dataset
    reader = Reader(rating_scale=(0.5, 5.0))
    surprise_data = Dataset.load_from_df(train_df[['userId', 'movieId', 'rating']], reader)
    surprise_trainset = surprise_data.build_full_trainset()
    
    # Initialize ranking metrics evaluator
    ranking_evaluator = RankingMetrics(relevance_threshold=4.0)
    
    # Models to evaluate
    models = {
        'SVD': SVD(n_factors=50, n_epochs=20, random_state=42),
        'KNN_User': KNNBasic(k=40, sim_options={'name': 'cosine', 'user_based': True}),
        'KNN_Item': KNNBasic(k=40, sim_options={'name': 'cosine', 'user_based': False})
    }
    
    results = {}
    
    for model_name, model in models.items():
        logger.info(f"Training and evaluating {model_name}...")
        
        with mlflow.start_run(run_name=f"{model_name}_ranking_eval"):
            # Train model
            model.fit(surprise_trainset)
            
            # Evaluate RMSE
            testset = [(row['userId'], row['movieId'], row['rating']) 
                      for _, row in test_df.iterrows()]
            predictions = model.test(testset)
            rmse = accuracy.rmse(predictions, verbose=False)
            
            mlflow.log_metric("rmse", rmse)
            logger.info(f"{model_name} RMSE: {rmse:.4f}")
            
            # Evaluate ranking metrics
            ranking_metrics = evaluate_ranking_performance_optimized(
                model, test_df, ranking_evaluator, max_users=50
            )
            
            # Log ranking metrics
            for metric_name, k_results in ranking_metrics.items():
                for k, value in k_results.items():
                    mlflow.log_metric(f"{metric_name}_at_{k}", value)
            
            # Log model parameters
            if hasattr(model, 'n_factors'):
                mlflow.log_param("n_factors", model.n_factors)
            if hasattr(model, 'n_epochs'):
                mlflow.log_param("n_epochs", model.n_epochs)
            if hasattr(model, 'k'):
                mlflow.log_param("k_neighbors", model.k)
            
            mlflow.log_param("model_type", model_name)
            
            # Create and log ranking report
            metrics_report = format_ranking_metrics_report(ranking_metrics, model_name)
            with open(f"{model_name}_ranking_report.txt", "w", encoding='utf-8') as f:
                f.write(metrics_report)
            mlflow.log_artifact(f"{model_name}_ranking_report.txt")
            
            # Store results
            results[model_name] = {
                'rmse': rmse,
                'ranking_metrics': ranking_metrics
            }
            
            logger.info(f"Completed evaluation for {model_name}")
    
    # Print comparison results
    print("\n" + "="*80)
    print("*** RANKING METRICS COMPARISON RESULTS ***")
    print("="*80)
    
    # RMSE comparison
    print("\n--- RMSE (Lower is Better) ---")
    for model_name, result in results.items():
        print(f"{model_name:<12}: {result['rmse']:.4f}")
    
    # Ranking metrics comparison
    k_values = [5, 10, 20]
    metric_names = ['precision', 'recall', 'average_precision', 'ndcg']
    
    for metric in metric_names:
        print(f"\n--- {metric.replace('_', ' ').title()} @k (Higher is Better) ---")
        for k in k_values:
            print(f"\n@{k}:")
            for model_name, result in results.items():
                value = result['ranking_metrics'][metric].get(k, 0.0)
                print(f"  {model_name:<12}: {value:.4f}")
    
    # Find best models for each metric
    print("\n--- BEST PERFORMING MODELS ---")
    
    # Best RMSE
    best_rmse_model = min(results.keys(), key=lambda m: results[m]['rmse'])
    print(f"Best RMSE: {best_rmse_model} ({results[best_rmse_model]['rmse']:.4f})")
    
    # Best ranking metrics
    for metric in metric_names:
        for k in [10]:  # Focus on @10 for summary
            best_model = max(results.keys(), 
                           key=lambda m: results[m]['ranking_metrics'][metric].get(k, 0.0))
            best_value = results[best_model]['ranking_metrics'][metric].get(k, 0.0)
            print(f"Best {metric.replace('_', ' ').title()} @{k}: {best_model} ({best_value:.4f})")
    
    logger.info("*** Comprehensive ranking evaluation completed successfully! ***")
    
    return results


def evaluate_ranking_performance_optimized(
    model, 
    test_df: pd.DataFrame, 
    ranking_evaluator: RankingMetrics,
    max_users: int = 50
) -> dict:
    """
    Optimized ranking performance evaluation.
    
    Args:
        model: Trained Surprise model.
        test_df: Test dataframe.
        ranking_evaluator: RankingMetrics instance.
        max_users: Maximum number of users to evaluate (for performance).
        
    Returns:
        dict: Ranking metrics results.
    """
    logger.info("Evaluating ranking performance...")
    
    # Get unique users from test set (limited for performance)
    test_users = test_df['userId'].unique()[:max_users]
    
    # Get all unique movies for generating recommendations
    all_movies = test_df['movieId'].unique()
    
    # Prepare predictions and ground truth for ranking evaluation
    all_predictions = {}
    all_ground_truth = {}
    
    for user_id in test_users:
        # Get user's test ratings (ground truth)
        user_test_data = test_df[test_df['userId'] == user_id]
        if len(user_test_data) < 5:  # Skip users with too few test ratings
            continue
            
        ground_truth = dict(zip(user_test_data['movieId'].astype(str), user_test_data['rating']))
        
        # Generate predictions for movies this user rated in test set
        user_predictions = []
        for movie_id in user_test_data['movieId']:
            pred = model.predict(user_id, movie_id)
            user_predictions.append((str(movie_id), pred.est))
        
        # Sort by predicted rating (descending)
        user_predictions.sort(key=lambda x: x[1], reverse=True)
        
        all_predictions[str(user_id)] = user_predictions
        all_ground_truth[str(user_id)] = ground_truth
    
    # Evaluate ranking metrics
    ranking_results = ranking_evaluator.evaluate_model_performance(
        all_predictions, 
        all_ground_truth, 
        k_values=[5, 10, 20]
    )
    
    return ranking_results


if __name__ == "__main__":
    results = run_comprehensive_ranking_experiment(sample_size=200000)
