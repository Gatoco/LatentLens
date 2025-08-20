#!/usr/bin/env python3
"""
Simplified Hybrid Model Performance Evaluation for MLflow

This script provides a faster evaluation of the hybrid model focused on key metrics
and efficient MLflow registration.

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


class QuickHybridEvaluator:
    """Fast evaluation and MLflow registration for hybrid model"""
    
    def __init__(self):
        self.recommender = get_recommender()
        self.data_loader = DataLoader()
        
    def setup_mlflow_experiment(self):
        """Setup MLflow experiment"""
        try:
            mlflow.set_tracking_uri("./mlruns")
            
            experiment_name = "Hybrid_Model_Quick_Evaluation"
            experiment = mlflow.get_experiment_by_name(experiment_name)
            if experiment is None:
                experiment_id = mlflow.create_experiment(experiment_name)
                logger.info(f"Created MLflow experiment: {experiment_name}")
            else:
                experiment_id = experiment.experiment_id
                logger.info(f"Using existing MLflow experiment: {experiment_name}")
            
            mlflow.set_experiment(experiment_name)
            return experiment_id
            
        except Exception as e:
            logger.error(f"Error setting up MLflow experiment: {str(e)}")
            raise
    
    def quick_performance_test(self, test_users: List[int] = None) -> Dict[str, Any]:
        """Quick performance test with limited users"""
        if test_users is None:
            test_users = [1, 100, 500, 1000, 2000]  # Small sample
        
        results = {
            'hybrid': {'successful_recommendations': 0, 'errors': 0, 'avg_response_time': 0},
            'collaborative': {'successful_recommendations': 0, 'errors': 0, 'avg_response_time': 0},
            'popularity': {'successful_recommendations': 0, 'errors': 0, 'avg_response_time': 0}
        }
        
        strategies = ['hybrid', 'collaborative', 'popularity']
        
        for strategy in strategies:
            logger.info(f"🔍 Testing {strategy} strategy...")
            times = []
            successful = 0
            errors = 0
            
            for user_id in test_users:
                try:
                    start_time = time.time()
                    
                    # Get recommendations
                    result = self.recommender.get_recommendations(
                        user_id=user_id,
                        strategy=strategy,
                        n_recommendations=10
                    )
                    
                    end_time = time.time()
                    
                    if result.get('recommendations'):
                        successful += 1
                        times.append(end_time - start_time)
                    else:
                        errors += 1
                        
                except Exception as e:
                    errors += 1
                    logger.warning(f"Error for user {user_id} with {strategy}: {str(e)}")
            
            results[strategy]['successful_recommendations'] = successful
            results[strategy]['errors'] = errors
            results[strategy]['avg_response_time'] = np.mean(times) if times else 0
            
            logger.info(f"  ✅ {strategy}: {successful} successful, {errors} errors, avg time: {np.mean(times) if times else 0:.3f}s")
        
        return results
    
    def calculate_performance_metrics(self, performance_results: Dict[str, Any]) -> Dict[str, float]:
        """Calculate key performance metrics"""
        hybrid_success = performance_results['hybrid']['successful_recommendations']
        collab_success = performance_results['collaborative']['successful_recommendations']
        pop_success = performance_results['popularity']['successful_recommendations']
        
        # Success rates
        total_tests = 5  # Number of test users
        
        metrics = {
            'hybrid_success_rate': hybrid_success / total_tests,
            'collaborative_success_rate': collab_success / total_tests,
            'popularity_success_rate': pop_success / total_tests,
            
            'hybrid_response_time': performance_results['hybrid']['avg_response_time'],
            'collaborative_response_time': performance_results['collaborative']['avg_response_time'],
            'popularity_response_time': performance_results['popularity']['avg_response_time'],
            
            'hybrid_error_rate': performance_results['hybrid']['errors'] / total_tests,
            'collaborative_error_rate': performance_results['collaborative']['errors'] / total_tests,
            'popularity_error_rate': performance_results['popularity']['errors'] / total_tests,
        }
        
        # Performance improvements
        if collab_success > 0:
            metrics['hybrid_vs_collaborative_improvement'] = (hybrid_success - collab_success) / collab_success * 100
        else:
            metrics['hybrid_vs_collaborative_improvement'] = 0
            
        if pop_success > 0:
            metrics['hybrid_vs_popularity_improvement'] = (hybrid_success - pop_success) / pop_success * 100
        else:
            metrics['hybrid_vs_popularity_improvement'] = 0
        
        return metrics
    
    def get_system_info(self) -> Dict[str, Any]:
        """Get system information for the hybrid model"""
        try:
            # Get data statistics
            ratings = self.data_loader.load_ratings()
            movies = self.data_loader.load_movies()
            
            return {
                'total_users': ratings['userId'].nunique(),
                'total_movies': len(movies),
                'total_ratings': len(ratings),
                'rating_density': len(ratings) / (ratings['userId'].nunique() * len(movies)),
                'avg_ratings_per_user': ratings.groupby('userId').size().mean(),
                'avg_ratings_per_movie': ratings.groupby('movieId').size().mean(),
            }
        except Exception as e:
            logger.warning(f"Could not get system info: {str(e)}")
            return {}
    
    def register_in_mlflow(self, metrics: Dict[str, float], system_info: Dict[str, Any]):
        """Register hybrid model performance in MLflow"""
        logger.info("📝 Registering hybrid model in MLflow...")
        
        with mlflow.start_run(run_name=f"hybrid_quick_eval_{datetime.now().strftime('%Y%m%d_%H%M%S')}"):
            
            # Log performance metrics
            for metric_name, value in metrics.items():
                mlflow.log_metric(metric_name, value)
            
            # Log model parameters
            mlflow.log_param("model_type", "hybrid_refactored")
            mlflow.log_param("architecture", "strategy_pattern")
            mlflow.log_param("strategies_included", "collaborative,item_similarity,content_based")
            mlflow.log_param("cold_start_enabled", True)
            mlflow.log_param("evaluation_type", "quick_performance_test")
            mlflow.log_param("test_users", 5)
            mlflow.log_param("recommendations_per_test", 10)
            
            # Log system information
            for info_name, value in system_info.items():
                mlflow.log_param(info_name, value)
            
            # Log additional metadata
            mlflow.log_param("evaluation_timestamp", datetime.now().isoformat())
            mlflow.log_param("python_version", sys.version.split()[0])
            mlflow.log_param("framework", "scikit-surprise + custom")
            
            # Log tags
            mlflow.set_tag("model_stage", "production_ready")
            mlflow.set_tag("evaluation_status", "completed")
            mlflow.set_tag("model_version", "v2_refactored")
            
            logger.info("✅ Hybrid model registered successfully in MLflow")
    
    def generate_comparison_report(self, metrics: Dict[str, float], system_info: Dict[str, Any]) -> str:
        """Generate a comparison report"""
        report_lines = []
        report_lines.append("🎯 HYBRID MODEL QUICK EVALUATION REPORT")
        report_lines.append("=" * 55)
        report_lines.append("")
        
        # Performance Summary
        report_lines.append("📊 PERFORMANCE SUMMARY")
        report_lines.append("-" * 30)
        report_lines.append(f"Hybrid Success Rate:       {metrics['hybrid_success_rate']:.1%}")
        report_lines.append(f"Collaborative Success Rate: {metrics['collaborative_success_rate']:.1%}")
        report_lines.append(f"Popularity Success Rate:    {metrics['popularity_success_rate']:.1%}")
        report_lines.append("")
        
        # Response Times
        report_lines.append("⚡ RESPONSE TIMES")
        report_lines.append("-" * 20)
        report_lines.append(f"Hybrid:        {metrics['hybrid_response_time']:.3f}s")
        report_lines.append(f"Collaborative: {metrics['collaborative_response_time']:.3f}s")
        report_lines.append(f"Popularity:    {metrics['popularity_response_time']:.3f}s")
        report_lines.append("")
        
        # Improvements
        report_lines.append("🚀 PERFORMANCE IMPROVEMENTS")
        report_lines.append("-" * 35)
        report_lines.append(f"vs Collaborative: {metrics['hybrid_vs_collaborative_improvement']:+.1f}%")
        report_lines.append(f"vs Popularity:    {metrics['hybrid_vs_popularity_improvement']:+.1f}%")
        report_lines.append("")
        
        # System Stats
        report_lines.append("📈 SYSTEM STATISTICS")
        report_lines.append("-" * 25)
        if system_info:
            report_lines.append(f"Total Users:    {system_info.get('total_users', 'N/A'):,}")
            report_lines.append(f"Total Movies:   {system_info.get('total_movies', 'N/A'):,}")
            report_lines.append(f"Total Ratings:  {system_info.get('total_ratings', 'N/A'):,}")
            if 'rating_density' in system_info:
                report_lines.append(f"Rating Density: {system_info['rating_density']:.6f}")
        report_lines.append("")
        
        # Winner
        report_lines.append("🏆 EVALUATION RESULT")
        report_lines.append("-" * 25)
        best_success = max(metrics['hybrid_success_rate'], 
                          metrics['collaborative_success_rate'], 
                          metrics['popularity_success_rate'])
        
        if metrics['hybrid_success_rate'] == best_success:
            report_lines.append("🥇 HYBRID MODEL WINS!")
            report_lines.append("   ✅ Best success rate")
            report_lines.append("   ✅ Combines multiple strategies")
            report_lines.append("   ✅ Cold start support")
        else:
            report_lines.append("⚠️  Other models performed better in this quick test")
            report_lines.append("   (Recommend running full evaluation)")
        
        return "\n".join(report_lines)
    
    def run_evaluation(self):
        """Run complete quick evaluation"""
        logger.info("🚀 Starting Quick Hybrid Model Evaluation...")
        
        try:
            # Setup MLflow
            self.setup_mlflow_experiment()
            
            # Run performance tests
            logger.info("🔍 Running performance tests...")
            performance_results = self.quick_performance_test()
            
            # Calculate metrics
            metrics = self.calculate_performance_metrics(performance_results)
            
            # Get system info
            system_info = self.get_system_info()
            
            # Register in MLflow
            self.register_in_mlflow(metrics, system_info)
            
            # Generate report
            report = self.generate_comparison_report(metrics, system_info)
            print("\n" + report)
            
            # Save report
            with open("hybrid_quick_evaluation_report.txt", "w", encoding='utf-8') as f:
                f.write(report)
            
            logger.info("✅ Quick evaluation completed!")
            logger.info("📄 Report saved to: hybrid_quick_evaluation_report.txt")
            logger.info("🔗 View MLflow results: mlflow ui --backend-store-uri ./mlruns")
            
            return metrics
            
        except Exception as e:
            logger.error(f"❌ Error during evaluation: {str(e)}")
            raise


if __name__ == "__main__":
    evaluator = QuickHybridEvaluator()
    results = evaluator.run_evaluation()
