#!/usr/bin/env python3
"""
Hybrid Model Performance Evaluation and MLflow Registration

This script evaluates the refactored hybrid recommendation system using comprehensive
ranking metrics and registers the results in MLflow for comparison with individual models.

Author: LatentLens Team
License: MIT
"""

import os
import sys
import logging
import time
from typing import Dict, List, Any
import pandas as pd
import numpy as np
import mlflow
import mlflow.pyfunc
from datetime import datetime

# Add src to Python path
sys.path.append(os.path.join(os.path.dirname(__file__), 'src'))

from src.recommender import get_recommender
from src.data_loader import DataLoader

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)


class HybridModelEvaluator:
    """Comprehensive evaluation and MLflow registration for hybrid model"""
    
    def __init__(self):
        self.recommender = get_recommender()
        self.data_loader = DataLoader()
        self.experiment_name = "Hybrid_Model_Evaluation"
        
    def setup_mlflow_experiment(self):
        """Setup MLflow experiment for hybrid model evaluation"""
        try:
            # Set MLflow tracking URI
            mlflow.set_tracking_uri("./mlruns")
            
            # Create or get experiment
            experiment = mlflow.get_experiment_by_name(self.experiment_name)
            if experiment is None:
                experiment_id = mlflow.create_experiment(self.experiment_name)
                logger.info(f"Created new MLflow experiment: {self.experiment_name} (ID: {experiment_id})")
            else:
                experiment_id = experiment.experiment_id
                logger.info(f"Using existing MLflow experiment: {self.experiment_name} (ID: {experiment_id})")
            
            mlflow.set_experiment(self.experiment_name)
            return experiment_id
            
        except Exception as e:
            logger.error(f"Error setting up MLflow experiment: {str(e)}")
            raise
    
    def prepare_evaluation_data(self, sample_users: int = 1000) -> Dict[str, Any]:
        """Prepare evaluation dataset for hybrid model testing"""
        logger.info("Preparing evaluation data...")
        
        # Load ratings data
        ratings = self.data_loader.load_ratings()
        movies = self.data_loader.load_movies()
        
        # Sample users for evaluation (active users with sufficient ratings)
        user_rating_counts = ratings.groupby('userId').size()
        active_users = user_rating_counts[user_rating_counts >= 10].index.tolist()
        
        # Sample subset for evaluation
        sample_size = min(sample_users, len(active_users))
        sampled_users = np.random.choice(active_users, size=sample_size, replace=False)
        
        # Create evaluation set (80/20 split per user)
        train_data = []
        test_data = []
        
        for user_id in sampled_users:
            user_ratings = ratings[ratings['userId'] == user_id].sort_values('timestamp')
            n_ratings = len(user_ratings)
            
            # 80% for training, 20% for testing
            split_idx = int(0.8 * n_ratings)
            
            train_data.append(user_ratings.iloc[:split_idx])
            test_data.append(user_ratings.iloc[split_idx:])
        
        train_df = pd.concat(train_data, ignore_index=True)
        test_df = pd.concat(test_data, ignore_index=True)
        
        logger.info(f"Evaluation data prepared:")
        logger.info(f"  - Sampled users: {len(sampled_users)}")
        logger.info(f"  - Training ratings: {len(train_df):,}")
        logger.info(f"  - Test ratings: {len(test_df):,}")
        
        return {
            'sampled_users': sampled_users,
            'train_data': train_df,
            'test_data': test_df,
            'movies': movies
        }
    
    def evaluate_strategy_performance(self, strategy: str, sampled_users: List[int], 
                                    test_data: pd.DataFrame, k_values: List[int] = [5, 10, 20]) -> Dict[str, float]:
        """Evaluate a specific recommendation strategy"""
        logger.info(f"Evaluating {strategy} strategy...")
        
        all_precisions = {k: [] for k in k_values}
        all_recalls = {k: [] for k in k_values}
        all_f1_scores = {k: [] for k in k_values}
        
        strategy_errors = 0
        successful_users = 0
        
        for user_id in sampled_users[:100]:  # Evaluate subset for performance
            try:
                # Get test ratings for this user
                user_test = test_data[test_data['userId'] == user_id]
                if len(user_test) == 0:
                    continue
                
                # Get actual relevant items (ratings >= 4.0)
                relevant_items = set(user_test[user_test['rating'] >= 4.0]['movieId'].tolist())
                if len(relevant_items) == 0:
                    continue
                
                # Get recommendations from the strategy
                if strategy == 'hybrid':
                    result = self.recommender.get_recommendations(
                        user_id=user_id,
                        strategy='hybrid',
                        n_recommendations=20
                    )
                elif strategy == 'collaborative':
                    result = self.recommender.get_recommendations(
                        user_id=user_id,
                        strategy='collaborative',
                        n_recommendations=20
                    )
                elif strategy == 'popularity':
                    result = self.recommender.get_recommendations(
                        user_id=user_id,
                        strategy='popularity',
                        n_recommendations=20
                    )
                else:
                    continue
                
                # Extract recommended movie IDs
                recommendations = result.get('recommendations', [])
                if not recommendations:
                    continue
                
                recommended_items = []
                for rec in recommendations:
                    if isinstance(rec, dict) and 'movie_id' in rec:
                        recommended_items.append(rec['movie_id'])
                    elif isinstance(rec, dict) and 'movieId' in rec:
                        recommended_items.append(rec['movieId'])
                
                if not recommended_items:
                    continue
                
                # Calculate metrics for different k values
                for k in k_values:
                    if len(recommended_items) >= k:
                        top_k_items = set(recommended_items[:k])
                        
                        # Precision@k
                        precision = len(top_k_items.intersection(relevant_items)) / k
                        all_precisions[k].append(precision)
                        
                        # Recall@k
                        recall = len(top_k_items.intersection(relevant_items)) / len(relevant_items) if relevant_items else 0
                        all_recalls[k].append(recall)
                        
                        # F1@k
                        if precision + recall > 0:
                            f1 = 2 * (precision * recall) / (precision + recall)
                        else:
                            f1 = 0
                        all_f1_scores[k].append(f1)
                
                successful_users += 1
                
            except Exception as e:
                strategy_errors += 1
                if strategy_errors <= 5:  # Log first 5 errors
                    logger.warning(f"Error evaluating user {user_id} for {strategy}: {str(e)}")
        
        # Calculate average metrics
        metrics = {}
        for k in k_values:
            if all_precisions[k]:
                metrics[f'precision_at_{k}'] = np.mean(all_precisions[k])
                metrics[f'recall_at_{k}'] = np.mean(all_recalls[k])
                metrics[f'f1_at_{k}'] = np.mean(all_f1_scores[k])
            else:
                metrics[f'precision_at_{k}'] = 0.0
                metrics[f'recall_at_{k}'] = 0.0
                metrics[f'f1_at_{k}'] = 0.0
        
        metrics['successful_evaluations'] = successful_users
        metrics['evaluation_errors'] = strategy_errors
        
        logger.info(f"{strategy} evaluation completed:")
        logger.info(f"  - Successful users: {successful_users}")
        logger.info(f"  - Errors: {strategy_errors}")
        for k in k_values:
            logger.info(f"  - Precision@{k}: {metrics[f'precision_at_{k}']:.4f}")
            logger.info(f"  - Recall@{k}: {metrics[f'recall_at_{k}']:.4f}")
            logger.info(f"  - F1@{k}: {metrics[f'f1_at_{k}']:.4f}")
        
        return metrics
    
    def compare_strategies(self) -> Dict[str, Dict[str, float]]:
        """Compare hybrid model against individual strategies"""
        logger.info("🔍 Starting comprehensive strategy comparison...")
        
        # Prepare evaluation data
        eval_data = self.prepare_evaluation_data(sample_users=500)
        
        # Strategies to evaluate
        strategies = ['hybrid', 'collaborative', 'popularity']
        results = {}
        
        # Evaluate each strategy
        for strategy in strategies:
            logger.info(f"\n📊 Evaluating {strategy} strategy...")
            results[strategy] = self.evaluate_strategy_performance(
                strategy=strategy,
                sampled_users=eval_data['sampled_users'][:100],  # Use subset for speed
                test_data=eval_data['test_data']
            )
        
        return results
    
    def register_hybrid_model_performance(self, strategy_results: Dict[str, Dict[str, float]]):
        """Register hybrid model performance in MLflow"""
        logger.info("📝 Registering hybrid model performance in MLflow...")
        
        with mlflow.start_run(run_name=f"hybrid_refactored_evaluation_{datetime.now().strftime('%Y%m%d_%H%M%S')}"):
            
            # Log hybrid model metrics
            hybrid_metrics = strategy_results['hybrid']
            
            # Log precision metrics
            mlflow.log_metric("precision_at_5", hybrid_metrics['precision_at_5'])
            mlflow.log_metric("precision_at_10", hybrid_metrics['precision_at_10'])
            mlflow.log_metric("precision_at_20", hybrid_metrics['precision_at_20'])
            
            # Log recall metrics
            mlflow.log_metric("recall_at_5", hybrid_metrics['recall_at_5'])
            mlflow.log_metric("recall_at_10", hybrid_metrics['recall_at_10'])
            mlflow.log_metric("recall_at_20", hybrid_metrics['recall_at_20'])
            
            # Log F1 metrics
            mlflow.log_metric("f1_at_5", hybrid_metrics['f1_at_5'])
            mlflow.log_metric("f1_at_10", hybrid_metrics['f1_at_10'])
            mlflow.log_metric("f1_at_20", hybrid_metrics['f1_at_20'])
            
            # Log evaluation metadata
            mlflow.log_metric("successful_evaluations", hybrid_metrics['successful_evaluations'])
            mlflow.log_metric("evaluation_errors", hybrid_metrics['evaluation_errors'])
            
            # Log model parameters
            mlflow.log_param("model_type", "hybrid_refactored")
            mlflow.log_param("strategies_used", "collaborative+item_similarity+content_based")
            mlflow.log_param("cold_start_enabled", True)
            mlflow.log_param("recommender_class", "unified")
            mlflow.log_param("evaluation_users", 100)
            mlflow.log_param("k_values", "5,10,20")
            
            # Log comparison with other strategies
            for strategy, metrics in strategy_results.items():
                if strategy != 'hybrid':
                    for metric_name, value in metrics.items():
                        mlflow.log_metric(f"{strategy}_{metric_name}", value)
            
            # Calculate and log performance improvements
            self.log_performance_comparisons(strategy_results)
            
            # Log system information
            mlflow.log_param("evaluation_timestamp", datetime.now().isoformat())
            mlflow.log_param("python_version", sys.version.split()[0])
            mlflow.log_param("recommender_architecture", "strategy_pattern")
            
            logger.info("✅ Hybrid model performance registered in MLflow")
    
    def log_performance_comparisons(self, strategy_results: Dict[str, Dict[str, float]]):
        """Log performance improvements of hybrid vs individual models"""
        hybrid_metrics = strategy_results['hybrid']
        
        for strategy in ['collaborative', 'popularity']:
            if strategy in strategy_results:
                strategy_metrics = strategy_results[strategy]
                
                # Calculate improvements for key metrics
                for k in [5, 10, 20]:
                    precision_key = f'precision_at_{k}'
                    recall_key = f'recall_at_{k}'
                    f1_key = f'f1_at_{k}'
                    
                    if precision_key in hybrid_metrics and precision_key in strategy_metrics:
                        if strategy_metrics[precision_key] > 0:
                            improvement = (hybrid_metrics[precision_key] - strategy_metrics[precision_key]) / strategy_metrics[precision_key] * 100
                            mlflow.log_metric(f"precision_at_{k}_improvement_vs_{strategy}", improvement)
                    
                    if recall_key in hybrid_metrics and recall_key in strategy_metrics:
                        if strategy_metrics[recall_key] > 0:
                            improvement = (hybrid_metrics[recall_key] - strategy_metrics[recall_key]) / strategy_metrics[recall_key] * 100
                            mlflow.log_metric(f"recall_at_{k}_improvement_vs_{strategy}", improvement)
                    
                    if f1_key in hybrid_metrics and f1_key in strategy_metrics:
                        if strategy_metrics[f1_key] > 0:
                            improvement = (hybrid_metrics[f1_key] - strategy_metrics[f1_key]) / strategy_metrics[f1_key] * 100
                            mlflow.log_metric(f"f1_at_{k}_improvement_vs_{strategy}", improvement)
    
    def generate_performance_report(self, strategy_results: Dict[str, Dict[str, float]]) -> str:
        """Generate comprehensive performance comparison report"""
        report = []
        report.append("🎯 HYBRID MODEL PERFORMANCE EVALUATION REPORT")
        report.append("=" * 60)
        report.append("")
        
        # Summary table
        report.append("📊 PERFORMANCE METRICS COMPARISON")
        report.append("-" * 40)
        
        strategies = ['hybrid', 'collaborative', 'popularity']
        k_values = [5, 10, 20]
        
        for k in k_values:
            report.append(f"\n📈 Metrics @{k}:")
            report.append(f"{'Strategy':<15} {'Precision':<12} {'Recall':<12} {'F1-Score':<12}")
            report.append("-" * 55)
            
            for strategy in strategies:
                if strategy in strategy_results:
                    metrics = strategy_results[strategy]
                    precision = metrics.get(f'precision_at_{k}', 0.0)
                    recall = metrics.get(f'recall_at_{k}', 0.0)
                    f1 = metrics.get(f'f1_at_{k}', 0.0)
                    
                    report.append(f"{strategy.capitalize():<15} {precision:<12.4f} {recall:<12.4f} {f1:<12.4f}")
        
        # Performance improvements
        report.append("\n🚀 HYBRID MODEL IMPROVEMENTS")
        report.append("-" * 40)
        
        hybrid_metrics = strategy_results.get('hybrid', {})
        
        for strategy in ['collaborative', 'popularity']:
            if strategy in strategy_results:
                report.append(f"\n vs {strategy.upper()}:")
                strategy_metrics = strategy_results[strategy]
                
                for k in k_values:
                    precision_key = f'precision_at_{k}'
                    if precision_key in hybrid_metrics and precision_key in strategy_metrics:
                        if strategy_metrics[precision_key] > 0:
                            improvement = (hybrid_metrics[precision_key] - strategy_metrics[precision_key]) / strategy_metrics[precision_key] * 100
                            status = "📈" if improvement > 0 else "📉"
                            report.append(f"  {status} Precision@{k}: {improvement:+.2f}%")
        
        # Winner determination
        report.append("\n🏆 PERFORMANCE WINNER")
        report.append("-" * 25)
        
        # Find best strategy for each metric
        for k in k_values:
            precision_key = f'precision_at_{k}'
            best_precision = 0
            best_strategy = ""
            
            for strategy in strategies:
                if strategy in strategy_results:
                    precision = strategy_results[strategy].get(precision_key, 0.0)
                    if precision > best_precision:
                        best_precision = precision
                        best_strategy = strategy
            
            report.append(f"🥇 Best Precision@{k}: {best_strategy.upper()} ({best_precision:.4f})")
        
        return "\n".join(report)
    
    def run_evaluation(self):
        """Run complete hybrid model evaluation and MLflow registration"""
        logger.info("🚀 Starting Hybrid Model Performance Evaluation...")
        
        try:
            # Setup MLflow
            self.setup_mlflow_experiment()
            
            # Compare strategies
            strategy_results = self.compare_strategies()
            
            # Register in MLflow
            self.register_hybrid_model_performance(strategy_results)
            
            # Generate report
            report = self.generate_performance_report(strategy_results)
            print("\n" + report)
            
            # Save report to file
            with open("hybrid_model_evaluation_report.txt", "w") as f:
                f.write(report)
            
            logger.info("✅ Hybrid model evaluation completed successfully!")
            logger.info("📊 Report saved to: hybrid_model_evaluation_report.txt")
            logger.info("🔗 View results in MLflow UI: mlflow ui --backend-store-uri ./mlruns")
            
            return strategy_results
            
        except Exception as e:
            logger.error(f"❌ Error during evaluation: {str(e)}")
            raise


if __name__ == "__main__":
    evaluator = HybridModelEvaluator()
    results = evaluator.run_evaluation()
