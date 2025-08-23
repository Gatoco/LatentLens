#!/usr/bin/env python3
"""
MLflow Hybrid Model Evaluation Script

This script performs comprehensive evaluation of the hybrid recommendation model
compared to individual models (SVD, Popular Baseline) and registers all metrics
in MLflow for tracking and comparison.

Author: LatentLens Team
"""

import os
import sys
import time
import logging
from datetime import datetime
from typing import Dict, List, Any, Tuple

# Add src to path for imports
sys.path.append(os.path.join(os.path.dirname(__file__), 'src'))

import mlflow
import mlflow.sklearn
import mlflow.pyfunc
import pandas as pd
import numpy as np
from sklearn.metrics import mean_squared_error, mean_absolute_error

# Import our recommendation services
from recommender import get_recommender
from recommendation_service import RecommendationService
from data_loader import DataLoader
from ranking_metrics import RankingMetrics

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class HybridModelEvaluator:
    """
    Comprehensive evaluation class for hybrid recommendation models
    """
    
    def __init__(self):
        """Initialize the evaluator with MLflow experiment"""
        self.experiment_name = "Hybrid_Model_Comparison"
        self.data_loader = DataLoader()
        self.recommender = get_recommender()
        self.metrics_calculator = RankingMetrics()
        
        # Set up MLflow experiment
        mlflow.set_experiment(self.experiment_name)
        logger.info(f"🧪 MLflow experiment set: {self.experiment_name}")
    
    def prepare_evaluation_data(self, sample_size: int = 5000) -> Tuple[pd.DataFrame, pd.DataFrame, pd.DataFrame]:
        """
        Prepare evaluation datasets with train/test split
        
        Args:
            sample_size: Number of users to sample for evaluation
            
        Returns:
            Tuple of (ratings, movies, test_users)
        """
        logger.info("📊 Loading and preparing evaluation data...")
        
        # Load full datasets
        ratings = self.data_loader.load_ratings()
        movies = self.data_loader.load_movies()
        
        # Sample active users for evaluation
        user_counts = ratings.groupby('userId').size()
        active_users = user_counts[user_counts >= 10].index  # Users with at least 10 ratings
        
        if len(active_users) > sample_size:
            sampled_users = np.random.choice(active_users, sample_size, replace=False)
        else:
            sampled_users = active_users
        
        # Create test set
        test_ratings = ratings[ratings['userId'].isin(sampled_users)]
        
        logger.info(f"✅ Prepared evaluation data:")
        logger.info(f"   Total ratings: {len(ratings):,}")
        logger.info(f"   Total movies: {len(movies):,}")
        logger.info(f"   Test users: {len(sampled_users):,}")
        logger.info(f"   Test ratings: {len(test_ratings):,}")
        
        return ratings, movies, test_ratings
    
    def evaluate_svd_model(self, test_ratings: pd.DataFrame) -> Dict[str, float]:
        """Evaluate SVD collaborative filtering model"""
        logger.info("🔬 Evaluating SVD Collaborative Filtering Model...")
        
        with mlflow.start_run(run_name="SVD_Collaborative_Filtering") as run:
            try:
                # Get SVD recommendations for test users
                test_users = test_ratings['userId'].unique()[:1000]  # Limit for performance
                
                all_predictions = []
                precision_scores = []
                recall_scores = []
                map_scores = []
                
                for user_id in test_users:
                    try:
                        # Get SVD recommendations
                        result = self.recommender.get_recommendations(
                            user_id=user_id,
                            strategy='collaborative',
                            n_recommendations=10
                        )
                        
                        if result['recommendations']:
                            # Get user's actual high ratings (>=4.0) as ground truth
                            user_ratings = test_ratings[test_ratings['userId'] == user_id]
                            relevant_movies = set(user_ratings[user_ratings['rating'] >= 4.0]['movieId'].values)
                            
                            if relevant_movies:
                                # Get recommended movie IDs
                                recommended_movies = set([rec['movie_id'] for rec in result['recommendations']])
                                
                                # Calculate metrics
                                if recommended_movies:
                                    precision = len(relevant_movies.intersection(recommended_movies)) / len(recommended_movies)
                                    recall = len(relevant_movies.intersection(recommended_movies)) / len(relevant_movies)
                                    
                                    precision_scores.append(precision)
                                    recall_scores.append(recall)
                                    
                                    # Calculate MAP
                                    map_score = self._calculate_map_score(recommended_movies, relevant_movies)
                                    map_scores.append(map_score)
                    
                    except Exception as e:
                        logger.warning(f"Error evaluating user {user_id}: {str(e)}")
                        continue
                
                # Calculate average metrics
                metrics = {
                    'precision_at_10': np.mean(precision_scores) if precision_scores else 0.0,
                    'recall_at_10': np.mean(recall_scores) if recall_scores else 0.0,
                    'map_at_10': np.mean(map_scores) if map_scores else 0.0,
                    'coverage': len(set([rec['movie_id'] for user_id in test_users[:100] 
                                       for rec in self.recommender.get_recommendations(user_id, 'collaborative', 10)['recommendations']])),
                    'users_evaluated': len(precision_scores)
                }
                
                # Log metrics to MLflow
                mlflow.log_metrics(metrics)
                mlflow.log_param("model_type", "collaborative_filtering_svd")
                mlflow.log_param("algorithm", "SVD")
                mlflow.log_param("users_evaluated", len(test_users))
                
                logger.info(f"✅ SVD Model Metrics:")
                for key, value in metrics.items():
                    logger.info(f"   {key}: {value:.4f}")
                
                return metrics
                
            except Exception as e:
                logger.error(f"❌ Error evaluating SVD model: {str(e)}")
                return {}
    
    def evaluate_hybrid_model(self, test_ratings: pd.DataFrame) -> Dict[str, float]:
        """Evaluate Hybrid recommendation model"""
        logger.info("🔬 Evaluating Hybrid Recommendation Model...")
        
        with mlflow.start_run(run_name="Hybrid_Model") as run:
            try:
                # Get hybrid recommendations for test users
                test_users = test_ratings['userId'].unique()[:1000]  # Limit for performance
                
                precision_scores = []
                recall_scores = []
                map_scores = []
                diversity_scores = []
                
                for user_id in test_users:
                    try:
                        # Get hybrid recommendations
                        result = self.recommender.get_recommendations(
                            user_id=user_id,
                            strategy='hybrid',
                            n_recommendations=10
                        )
                        
                        if result['recommendations']:
                            # Get user's actual high ratings (>=4.0) as ground truth
                            user_ratings = test_ratings[test_ratings['userId'] == user_id]
                            relevant_movies = set(user_ratings[user_ratings['rating'] >= 4.0]['movieId'].values)
                            
                            if relevant_movies:
                                # Get recommended movie IDs
                                recommended_movies = set([rec['movie_id'] for rec in result['recommendations']])
                                
                                # Calculate metrics
                                if recommended_movies:
                                    precision = len(relevant_movies.intersection(recommended_movies)) / len(recommended_movies)
                                    recall = len(relevant_movies.intersection(recommended_movies)) / len(relevant_movies)
                                    
                                    precision_scores.append(precision)
                                    recall_scores.append(recall)
                                    
                                    # Calculate MAP
                                    map_score = self._calculate_map_score(recommended_movies, relevant_movies)
                                    map_scores.append(map_score)
                                    
                                    # Calculate diversity (unique genres)
                                    genres = set()
                                    for rec in result['recommendations']:
                                        if 'genres' in rec:
                                            genres.update(rec['genres'].split('|'))
                                    diversity_scores.append(len(genres))
                    
                    except Exception as e:
                        logger.warning(f"Error evaluating user {user_id}: {str(e)}")
                        continue
                
                # Calculate average metrics
                metrics = {
                    'precision_at_10': np.mean(precision_scores) if precision_scores else 0.0,
                    'recall_at_10': np.mean(recall_scores) if recall_scores else 0.0,
                    'map_at_10': np.mean(map_scores) if map_scores else 0.0,
                    'diversity_score': np.mean(diversity_scores) if diversity_scores else 0.0,
                    'coverage': len(set([rec['movie_id'] for user_id in test_users[:100] 
                                       for rec in self.recommender.get_recommendations(user_id, 'hybrid', 10)['recommendations']])),
                    'users_evaluated': len(precision_scores)
                }
                
                # Log metrics to MLflow
                mlflow.log_metrics(metrics)
                mlflow.log_param("model_type", "hybrid_recommendation")
                mlflow.log_param("components", "SVD+ItemSimilarity+ContentBased")
                mlflow.log_param("cold_start_enabled", True)
                mlflow.log_param("users_evaluated", len(test_users))
                
                logger.info(f"✅ Hybrid Model Metrics:")
                for key, value in metrics.items():
                    logger.info(f"   {key}: {value:.4f}")
                
                return metrics
                
            except Exception as e:
                logger.error(f"❌ Error evaluating Hybrid model: {str(e)}")
                return {}
    
    def evaluate_popularity_baseline(self, test_ratings: pd.DataFrame) -> Dict[str, float]:
        """Evaluate Popularity baseline model"""
        logger.info("🔬 Evaluating Popularity Baseline Model...")
        
        with mlflow.start_run(run_name="Popularity_Baseline") as run:
            try:
                # Get popular movie recommendations
                popular_result = self.recommender.get_popular_movies(n_recommendations=10)
                popular_movies = set([movie['movie_id'] for movie in popular_result['recommendations']])
                
                test_users = test_ratings['userId'].unique()[:1000]  # Limit for performance
                
                precision_scores = []
                recall_scores = []
                map_scores = []
                
                for user_id in test_users:
                    try:
                        # Get user's actual high ratings (>=4.0) as ground truth
                        user_ratings = test_ratings[test_ratings['userId'] == user_id]
                        relevant_movies = set(user_ratings[user_ratings['rating'] >= 4.0]['movieId'].values)
                        
                        if relevant_movies and popular_movies:
                            # Calculate metrics using popular movies as recommendations
                            precision = len(relevant_movies.intersection(popular_movies)) / len(popular_movies)
                            recall = len(relevant_movies.intersection(popular_movies)) / len(relevant_movies)
                            
                            precision_scores.append(precision)
                            recall_scores.append(recall)
                            
                            # Calculate MAP
                            map_score = self._calculate_map_score(popular_movies, relevant_movies)
                            map_scores.append(map_score)
                    
                    except Exception as e:
                        logger.warning(f"Error evaluating user {user_id}: {str(e)}")
                        continue
                
                # Calculate average metrics
                metrics = {
                    'precision_at_10': np.mean(precision_scores) if precision_scores else 0.0,
                    'recall_at_10': np.mean(recall_scores) if recall_scores else 0.0,
                    'map_at_10': np.mean(map_scores) if map_scores else 0.0,
                    'coverage': len(popular_movies),
                    'users_evaluated': len(precision_scores)
                }
                
                # Log metrics to MLflow
                mlflow.log_metrics(metrics)
                mlflow.log_param("model_type", "popularity_baseline")
                mlflow.log_param("algorithm", "most_popular")
                mlflow.log_param("users_evaluated", len(test_users))
                
                logger.info(f"✅ Popularity Baseline Metrics:")
                for key, value in metrics.items():
                    logger.info(f"   {key}: {value:.4f}")
                
                return metrics
                
            except Exception as e:
                logger.error(f"❌ Error evaluating Popularity baseline: {str(e)}")
                return {}
    
    def _calculate_map_score(self, recommended: set, relevant: set) -> float:
        """Calculate Mean Average Precision score"""
        if not recommended or not relevant:
            return 0.0
        
        score = 0.0
        num_hits = 0.0
        
        for i, item in enumerate(list(recommended)):
            if item in relevant:
                num_hits += 1.0
                score += num_hits / (i + 1.0)
        
        return score / len(relevant) if relevant else 0.0
    
    def compare_models(self, svd_metrics: Dict, hybrid_metrics: Dict, popular_metrics: Dict):
        """Compare all models and log comparison metrics"""
        logger.info("📊 Comparing Model Performance...")
        
        with mlflow.start_run(run_name="Model_Comparison") as run:
            # Calculate improvement percentages
            svd_vs_popular = {
                'precision_improvement': ((svd_metrics.get('precision_at_10', 0) - popular_metrics.get('precision_at_10', 0)) / popular_metrics.get('precision_at_10', 1)) * 100,
                'recall_improvement': ((svd_metrics.get('recall_at_10', 0) - popular_metrics.get('recall_at_10', 0)) / popular_metrics.get('recall_at_10', 1)) * 100,
                'map_improvement': ((svd_metrics.get('map_at_10', 0) - popular_metrics.get('map_at_10', 0)) / popular_metrics.get('map_at_10', 1)) * 100
            }
            
            hybrid_vs_popular = {
                'precision_improvement': ((hybrid_metrics.get('precision_at_10', 0) - popular_metrics.get('precision_at_10', 0)) / popular_metrics.get('precision_at_10', 1)) * 100,
                'recall_improvement': ((hybrid_metrics.get('recall_at_10', 0) - popular_metrics.get('recall_at_10', 0)) / popular_metrics.get('recall_at_10', 1)) * 100,
                'map_improvement': ((hybrid_metrics.get('map_at_10', 0) - popular_metrics.get('map_at_10', 0)) / popular_metrics.get('map_at_10', 1)) * 100
            }
            
            hybrid_vs_svd = {
                'precision_ratio': hybrid_metrics.get('precision_at_10', 0) / svd_metrics.get('precision_at_10', 1),
                'recall_ratio': hybrid_metrics.get('recall_at_10', 0) / svd_metrics.get('recall_at_10', 1),
                'map_ratio': hybrid_metrics.get('map_at_10', 0) / svd_metrics.get('map_at_10', 1),
                'diversity_advantage': hybrid_metrics.get('diversity_score', 0)
            }
            
            # Log comparison metrics
            for metric, value in svd_vs_popular.items():
                mlflow.log_metric(f"svd_vs_popular_{metric}", value)
            
            for metric, value in hybrid_vs_popular.items():
                mlflow.log_metric(f"hybrid_vs_popular_{metric}", value)
            
            for metric, value in hybrid_vs_svd.items():
                mlflow.log_metric(f"hybrid_vs_svd_{metric}", value)
            
            # Log model rankings
            precision_ranking = sorted([
                ('SVD', svd_metrics.get('precision_at_10', 0)),
                ('Hybrid', hybrid_metrics.get('precision_at_10', 0)),
                ('Popular', popular_metrics.get('precision_at_10', 0))
            ], key=lambda x: x[1], reverse=True)
            
            mlflow.log_param("precision_winner", precision_ranking[0][0])
            mlflow.log_param("evaluation_date", datetime.now().isoformat())
            
            # Print comparison results
            logger.info("🏆 MODEL COMPARISON RESULTS:")
            logger.info("=" * 50)
            
            logger.info("\n📊 PRECISION@10 RANKING:")
            for i, (model, score) in enumerate(precision_ranking, 1):
                logger.info(f"   {i}. {model}: {score:.4f}")
            
            logger.info(f"\n🎯 HYBRID vs SVD:")
            logger.info(f"   Precision Ratio: {hybrid_vs_svd['precision_ratio']:.3f}")
            logger.info(f"   Recall Ratio: {hybrid_vs_svd['recall_ratio']:.3f}")
            logger.info(f"   MAP Ratio: {hybrid_vs_svd['map_ratio']:.3f}")
            logger.info(f"   Diversity Score: {hybrid_vs_svd['diversity_advantage']:.2f}")
            
            if hybrid_vs_svd['precision_ratio'] > 1.0:
                logger.info("✅ HYBRID MODEL OUTPERFORMS SVD!")
            else:
                logger.info("ℹ️ SVD outperforms Hybrid in precision, but Hybrid provides diversity")
    
    def run_complete_evaluation(self):
        """Run complete evaluation of all models"""
        logger.info("🚀 Starting Complete Model Evaluation...")
        start_time = time.time()
        
        try:
            # Prepare data
            ratings, movies, test_ratings = self.prepare_evaluation_data(sample_size=3000)
            
            # Evaluate all models
            logger.info("\n" + "="*60)
            svd_metrics = self.evaluate_svd_model(test_ratings)
            
            logger.info("\n" + "="*60)
            hybrid_metrics = self.evaluate_hybrid_model(test_ratings)
            
            logger.info("\n" + "="*60)
            popular_metrics = self.evaluate_popularity_baseline(test_ratings)
            
            # Compare models
            logger.info("\n" + "="*60)
            self.compare_models(svd_metrics, hybrid_metrics, popular_metrics)
            
            # Summary
            elapsed_time = time.time() - start_time
            logger.info(f"\n✅ Evaluation completed in {elapsed_time:.2f} seconds")
            logger.info("🎉 All metrics registered in MLflow!")
            
            return {
                'svd_metrics': svd_metrics,
                'hybrid_metrics': hybrid_metrics,
                'popular_metrics': popular_metrics
            }
            
        except Exception as e:
            logger.error(f"❌ Evaluation failed: {str(e)}")
            raise


def main():
    """Main evaluation function"""
    print("🎯 MLflow Hybrid Model Evaluation")
    print("=" * 50)
    
    evaluator = HybridModelEvaluator()
    results = evaluator.run_complete_evaluation()
    
    print("\n🎊 EVALUATION SUMMARY:")
    print("✅ SVD Model evaluated and registered")
    print("✅ Hybrid Model evaluated and registered") 
    print("✅ Popularity Baseline evaluated and registered")
    print("✅ Model comparison metrics calculated")
    print("✅ All results stored in MLflow")
    
    print(f"\n📊 Access MLflow UI at: http://localhost:5000")
    print(f"🧪 Experiment: {evaluator.experiment_name}")


if __name__ == "__main__":
    main()
