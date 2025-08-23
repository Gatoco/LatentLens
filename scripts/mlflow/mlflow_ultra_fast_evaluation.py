#!/usr/bin/env python3
"""
MLflow Ultra-Fast Model Evaluation Script

This version focuses on speed over comprehensive evaluation.
Tests only basic functionality with minimal data loading.

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
import pandas as pd
import numpy as np

# Import our recommendation services
from recommender import get_recommender

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class UltraFastEvaluator:
    """
    Ultra-fast evaluation class - minimal data loading, maximum speed
    """
    
    def __init__(self):
        """Initialize the evaluator with minimal setup"""
        self.experiment_name = "Ultra_Fast_Model_Evaluation"
        self.recommender = get_recommender()
        
        # Set up MLflow experiment
        mlflow.set_experiment(self.experiment_name)
        logger.info(f"🧪 MLflow experiment set: {self.experiment_name}")
    
    def test_model_basic_functionality(self, model_name: str, strategy: str) -> Dict[str, float]:
        """
        Test basic functionality with minimal overhead
        
        Args:
            model_name: Name of the model for MLflow
            strategy: Strategy to use ('collaborative', 'hybrid', 'popularity')
            
        Returns:
            Dictionary of basic metrics
        """
        logger.info(f"⚡ Testing {model_name} Model (ultra-fast)...")
        
        with mlflow.start_run(run_name=model_name) as run:
            # Test with a small set of known user IDs
            test_users = [1, 2, 3, 5, 10]  # Known existing users
            
            successful_calls = 0
            total_recommendations = 0
            unique_movies = set()
            response_times = []
            
            for user_id in test_users:
                try:
                    start_time = time.time()
                    
                    if strategy == 'popularity':
                        result = self.recommender.get_popular_movies(n_recommendations=5)
                    else:
                        result = self.recommender.get_recommendations(
                            user_id=user_id,
                            strategy=strategy,
                            n_recommendations=5
                        )
                    
                    end_time = time.time()
                    response_times.append(end_time - start_time)
                    
                    if result and result.get('recommendations'):
                        successful_calls += 1
                        recs = result['recommendations']
                        total_recommendations += len(recs)
                        
                        # Extract movie IDs
                        for rec in recs:
                            if isinstance(rec, dict):
                                movie_id = rec.get('movie_id') or rec.get('movieId')
                                if movie_id:
                                    unique_movies.add(movie_id)
                            
                except Exception as e:
                    logger.warning(f"Error with user {user_id} on {strategy}: {str(e)}")
                    response_times.append(999)  # High penalty for errors
                    continue
            
            # Calculate basic metrics
            success_rate = successful_calls / len(test_users)
            avg_response_time = np.mean(response_times) if response_times else 999
            total_unique_movies = len(unique_movies)
            avg_recs_per_call = total_recommendations / successful_calls if successful_calls > 0 else 0
            
            # Create simple performance score
            performance_score = success_rate * (1 / max(avg_response_time, 0.001)) * total_unique_movies
            
            metrics = {
                'success_rate': success_rate,
                'avg_response_time_seconds': avg_response_time,
                'unique_movies_returned': total_unique_movies,
                'avg_recommendations_per_call': avg_recs_per_call,
                'performance_score': performance_score,
                'total_successful_calls': successful_calls
            }
            
            # Log to MLflow
            mlflow.log_metrics(metrics)
            mlflow.log_param("model_strategy", strategy)
            mlflow.log_param("test_users_count", len(test_users))
            mlflow.log_param("evaluation_type", "ultra_fast")
            mlflow.log_param("evaluation_date", datetime.now().isoformat())
            
            logger.info(f"✅ {model_name} Fast Metrics:")
            logger.info(f"   Success Rate: {success_rate:.2f}")
            logger.info(f"   Avg Response Time: {avg_response_time:.3f}s")
            logger.info(f"   Unique Movies: {total_unique_movies}")
            logger.info(f"   Performance Score: {performance_score:.2f}")
            
            return metrics
    
    def run_ultra_fast_evaluation(self):
        """Run ultra-fast evaluation of all models"""
        logger.info("⚡ Starting Ultra-Fast Model Evaluation...")
        start_time = time.time()
        
        try:
            results = {}
            
            # Test Popularity Model (fastest)
            logger.info("\n" + "="*50)
            results['popularity'] = self.test_model_basic_functionality(
                "Popularity_Model_Fast",
                "popularity"
            )
            
            # Test Collaborative Filtering
            logger.info("\n" + "="*50)
            results['collaborative'] = self.test_model_basic_functionality(
                "Collaborative_Model_Fast",
                "collaborative"
            )
            
            # Test Hybrid Model
            logger.info("\n" + "="*50)
            results['hybrid'] = self.test_model_basic_functionality(
                "Hybrid_Model_Fast",
                "hybrid"
            )
            
            # Quick Comparison
            logger.info("\n" + "="*50)
            self.quick_comparison(results)
            
            elapsed_time = time.time() - start_time
            logger.info(f"\n⚡ Ultra-fast evaluation completed in {elapsed_time:.2f} seconds")
            logger.info("🎉 Basic metrics registered in MLflow!")
            
            return results
            
        except Exception as e:
            logger.error(f"❌ Ultra-fast evaluation failed: {str(e)}")
            raise
    
    def quick_comparison(self, results: Dict):
        """Quick comparison of models"""
        logger.info("📊 Quick Model Comparison...")
        
        with mlflow.start_run(run_name="Ultra_Fast_Comparison") as run:
            # Extract metrics
            models = ['popularity', 'collaborative', 'hybrid']
            
            comparison_data = {}
            for model in models:
                if model in results:
                    comparison_data[f"{model}_success_rate"] = results[model]['success_rate']
                    comparison_data[f"{model}_response_time"] = results[model]['avg_response_time_seconds']
                    comparison_data[f"{model}_unique_movies"] = results[model]['unique_movies_returned']
                    comparison_data[f"{model}_performance_score"] = results[model]['performance_score']
            
            # Calculate ratios
            if 'hybrid' in results and 'collaborative' in results:
                hybrid_vs_collab_score = (results['hybrid']['performance_score'] / 
                                        results['collaborative']['performance_score']) if results['collaborative']['performance_score'] > 0 else 0
                comparison_data['hybrid_vs_collaborative_ratio'] = hybrid_vs_collab_score
            
            if 'hybrid' in results and 'popularity' in results:
                hybrid_vs_pop_score = (results['hybrid']['performance_score'] / 
                                      results['popularity']['performance_score']) if results['popularity']['performance_score'] > 0 else 0
                comparison_data['hybrid_vs_popularity_ratio'] = hybrid_vs_pop_score
            
            # Log comparison metrics
            mlflow.log_metrics(comparison_data)
            mlflow.log_param("evaluation_type", "ultra_fast_comparison")
            mlflow.log_param("total_models_tested", len(results))
            
            # Print quick results
            logger.info("🏆 ULTRA-FAST RESULTS:")
            logger.info("=" * 40)
            
            for model in models:
                if model in results:
                    logger.info(f"\n📊 {model.upper()}:")
                    logger.info(f"   Success: {results[model]['success_rate']:.2f}")
                    logger.info(f"   Speed: {results[model]['avg_response_time_seconds']:.3f}s")
                    logger.info(f"   Movies: {results[model]['unique_movies_returned']}")
                    logger.info(f"   Score: {results[model]['performance_score']:.2f}")
            
            # Determine winner by performance score
            best_model = max(results.keys(), key=lambda k: results[k]['performance_score'])
            logger.info(f"\n🏆 Best Overall Performance: {best_model.upper()}")
            
            mlflow.log_param("performance_winner", best_model)


def main():
    """Main evaluation function"""
    print("⚡ MLflow Ultra-Fast Model Evaluation")
    print("=" * 50)
    
    evaluator = UltraFastEvaluator()
    results = evaluator.run_ultra_fast_evaluation()
    
    print("\n🎊 ULTRA-FAST EVALUATION SUMMARY:")
    print("✅ Basic functionality tested for all models")
    print("✅ Performance metrics captured") 
    print("✅ Speed optimization achieved")
    print("✅ Results stored in MLflow")
    
    print(f"\n📊 Access MLflow UI:")
    print(f"💻 Command: mlflow ui --backend-store-uri ./mlruns --port 5000")
    print(f"🌐 URL: http://localhost:5000")


if __name__ == "__main__":
    main()
