#!/usr/bin/env python3
"""
MLflow Quick Model Evaluation Script - Optimized Version

This is a simplified version that evaluates the hybrid model performance
and registers metrics in MLflow without exhaustive user-by-user evaluation.

Author: LatentLens Team
"""

import os
import sys
import time
import logging
from datetime import datetime
from typing import Dict, List, Any

# Add src to path for imports
sys.path.append(os.path.join(os.path.dirname(__file__), '..', '..'))
sys.path.append(os.path.join(os.path.dirname(__file__), '..', '..', 'src'))

import mlflow
import mlflow.sklearn
import pandas as pd
import numpy as np

# Import our recommendation services
from recommender import get_recommender
from data_loader import DataLoader

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class QuickModelEvaluator:
    """
    Quick evaluation class for hybrid recommendation models
    """
    
    def __init__(self):
        """Initialize the evaluator with MLflow experiment"""
        self.experiment_name = "Hybrid_Model_Quick_Evaluation"
        self.data_loader = DataLoader()
        self.recommender = get_recommender()
        
        # Load data once
        logger.info("📊 Loading datasets...")
        self.ratings = self.data_loader.load_ratings()
        self.movies = self.data_loader.load_movies()
        
        # Set up MLflow experiment
        mlflow.set_experiment(self.experiment_name)
        logger.info(f"🧪 MLflow experiment set: {self.experiment_name}")
    
    def evaluate_model_performance(self, model_name: str, strategy: str, sample_size: int = 50) -> Dict[str, float]:
        """
        Evaluate a model with a smaller sample for quick results
        
        Args:
            model_name: Name of the model for MLflow
            strategy: Strategy to use ('collaborative', 'hybrid', 'popularity')
            sample_size: Number of users to test
            
        Returns:
            Dictionary of metrics
        """
        logger.info(f"🔬 Evaluating {model_name} Model...")
        
        with mlflow.start_run(run_name=model_name) as run:
            # Get sample of active users
            user_counts = self.ratings.groupby('userId').size()
            active_users = user_counts[user_counts >= 20].index  # Users with at least 20 ratings
            
            if len(active_users) > sample_size:
                test_users = np.random.choice(active_users, sample_size, replace=False)
            else:
                test_users = active_users[:sample_size]
            
            successful_recommendations = 0
            total_recommendations = 0
            unique_movies_recommended = set()
            total_genres = set()
            
            for user_id in test_users:
                try:
                    if strategy == 'popularity':
                        result = self.recommender.get_popular_movies(n_recommendations=10)
                    else:
                        result = self.recommender.get_recommendations(
                            user_id=user_id,
                            strategy=strategy,
                            n_recommendations=10
                        )
                    
                    if result.get('recommendations'):
                        successful_recommendations += 1
                        total_recommendations += len(result['recommendations'])
                        
                        # Collect movie IDs and genres
                        for rec in result['recommendations']:
                            if 'movie_id' in rec:
                                unique_movies_recommended.add(rec['movie_id'])
                            elif 'movieId' in rec:  # Handle different key formats
                                unique_movies_recommended.add(rec['movieId'])
                            
                            # Collect genres if available
                            if 'genres' in rec and rec['genres']:
                                genres = rec['genres'].split('|') if isinstance(rec['genres'], str) else []
                                total_genres.update(genres)
                
                except Exception as e:
                    logger.warning(f"Error with user {user_id}: {str(e)}")
                    continue
            
            # Calculate metrics
            success_rate = successful_recommendations / len(test_users) if test_users.size > 0 else 0
            avg_recommendations_per_user = total_recommendations / successful_recommendations if successful_recommendations > 0 else 0
            catalog_coverage = len(unique_movies_recommended) / len(self.movies) if len(self.movies) > 0 else 0
            genre_diversity = len(total_genres)
            
            metrics = {
                'success_rate': success_rate,
                'avg_recommendations_per_user': avg_recommendations_per_user,
                'catalog_coverage': catalog_coverage,
                'unique_movies_recommended': len(unique_movies_recommended),
                'genre_diversity': genre_diversity,
                'users_tested': len(test_users),
                'successful_recommendations': successful_recommendations
            }
            
            # Log to MLflow
            mlflow.log_metrics(metrics)
            mlflow.log_param("model_strategy", strategy)
            mlflow.log_param("sample_size", sample_size)
            mlflow.log_param("evaluation_date", datetime.now().isoformat())
            
            logger.info(f"✅ {model_name} Metrics:")
            for key, value in metrics.items():
                logger.info(f"   {key}: {value:.4f}")
            
            return metrics
    
    def run_complete_evaluation(self):
        """Run evaluation of all models"""
        logger.info("🚀 Starting Quick Model Evaluation...")
        start_time = time.time()
        
        try:
            results = {}
            
            # Evaluate SVD Collaborative Filtering
            logger.info("\n" + "="*60)
            results['svd'] = self.evaluate_model_performance(
                "SVD_Collaborative_Filtering",
                "collaborative",
                50
            )
            
            # Evaluate Hybrid Model
            logger.info("\n" + "="*60)
            results['hybrid'] = self.evaluate_model_performance(
                "Hybrid_Recommendation",
                "hybrid",
                50
            )
            
            # Evaluate Popularity Baseline
            logger.info("\n" + "="*60)
            results['popular'] = self.evaluate_model_performance(
                "Popularity_Baseline",
                "popularity",
                50
            )
            
            # Model Comparison
            logger.info("\n" + "="*60)
            self.compare_models(results)
            
            elapsed_time = time.time() - start_time
            logger.info(f"\n✅ Quick evaluation completed in {elapsed_time:.2f} seconds")
            logger.info("🎉 All metrics registered in MLflow!")
            
            return results
            
        except Exception as e:
            logger.error(f"❌ Evaluation failed: {str(e)}")
            raise
    
    def compare_models(self, results: Dict):
        """Compare all models and log comparison metrics"""
        logger.info("📊 Comparing Model Performance...")
        
        with mlflow.start_run(run_name="Model_Comparison_Summary") as run:
            # Extract key metrics
            svd_success = results['svd']['success_rate']
            hybrid_success = results['hybrid']['success_rate']
            popular_success = results['popular']['success_rate']
            
            svd_coverage = results['svd']['catalog_coverage']
            hybrid_coverage = results['hybrid']['catalog_coverage']
            popular_coverage = results['popular']['catalog_coverage']
            
            # Calculate comparative metrics
            hybrid_vs_svd_success = (hybrid_success / svd_success) if svd_success > 0 else 0
            hybrid_vs_popular_success = (hybrid_success / popular_success) if popular_success > 0 else 0
            hybrid_vs_svd_coverage = (hybrid_coverage / svd_coverage) if svd_coverage > 0 else 0
            
            comparison_metrics = {
                'hybrid_vs_svd_success_ratio': hybrid_vs_svd_success,
                'hybrid_vs_popular_success_ratio': hybrid_vs_popular_success,
                'hybrid_vs_svd_coverage_ratio': hybrid_vs_svd_coverage,
                'best_success_rate': max(svd_success, hybrid_success, popular_success),
                'best_coverage': max(svd_coverage, hybrid_coverage, popular_coverage),
                'hybrid_diversity_score': results['hybrid']['genre_diversity']
            }
            
            # Log comparison metrics
            mlflow.log_metrics(comparison_metrics)
            
            # Determine winners
            success_winner = "Hybrid" if hybrid_success >= max(svd_success, popular_success) else \
                           "SVD" if svd_success >= popular_success else "Popular"
            coverage_winner = "Hybrid" if hybrid_coverage >= max(svd_coverage, popular_coverage) else \
                            "SVD" if svd_coverage >= popular_coverage else "Popular"
            
            mlflow.log_param("success_rate_winner", success_winner)
            mlflow.log_param("coverage_winner", coverage_winner)
            mlflow.log_param("evaluation_summary", f"Quick evaluation with 50 users per model")
            
            # Print results
            logger.info("🏆 QUICK EVALUATION RESULTS:")
            logger.info("=" * 50)
            
            logger.info(f"\n📊 SUCCESS RATES:")
            logger.info(f"   SVD: {svd_success:.3f}")
            logger.info(f"   Hybrid: {hybrid_success:.3f}")
            logger.info(f"   Popular: {popular_success:.3f}")
            logger.info(f"   Winner: {success_winner}")
            
            logger.info(f"\n📈 CATALOG COVERAGE:")
            logger.info(f"   SVD: {svd_coverage:.4f}")
            logger.info(f"   Hybrid: {hybrid_coverage:.4f}")
            logger.info(f"   Popular: {popular_coverage:.4f}")
            logger.info(f"   Winner: {coverage_winner}")
            
            logger.info(f"\n🎯 HYBRID MODEL PERFORMANCE:")
            logger.info(f"   vs SVD Success: {hybrid_vs_svd_success:.3f}x")
            logger.info(f"   vs Popular Success: {hybrid_vs_popular_success:.3f}x")
            logger.info(f"   Genre Diversity: {results['hybrid']['genre_diversity']} genres")
            
            if hybrid_vs_svd_success >= 1.0 and results['hybrid']['genre_diversity'] > 10:
                logger.info("✅ HYBRID MODEL SHOWS STRONG PERFORMANCE!")
            elif hybrid_vs_svd_success >= 0.9:
                logger.info("✅ HYBRID MODEL PERFORMS COMPETITIVELY WITH ADDED DIVERSITY!")
            else:
                logger.info("ℹ️  HYBRID MODEL PROVIDES DIVERSITY BUT NEEDS OPTIMIZATION")


def main():
    """Main evaluation function"""
    print("🎯 MLflow Quick Model Evaluation")
    print("=" * 50)
    
    evaluator = QuickModelEvaluator()
    results = evaluator.run_complete_evaluation()
    
    print("\n🎊 QUICK EVALUATION SUMMARY:")
    print("✅ SVD Model evaluated and registered")
    print("✅ Hybrid Model evaluated and registered") 
    print("✅ Popularity Baseline evaluated and registered")
    print("✅ Model comparison metrics calculated")
    print("✅ All results stored in MLflow")
    
    print(f"\n📊 Access MLflow UI to view detailed results:")
    print(f"💻 Command: mlflow ui --backend-store-uri ./mlruns --port 5000")
    print(f"🌐 URL: http://localhost:5000")


if __name__ == "__main__":
    main()
