#!/usr/bin/env python3
"""
Comprehensive Hybrid Model Performance Analysis

This script provides detailed analysis of hybrid model performance vs individual models,
including advanced metrics and statistical comparisons registered in MLflow.

Author: LatentLens Team
License: MIT
"""

import os
import sys
import logging
import pandas as pd
import numpy as np
import mlflow
from datetime import datetime
from typing import Dict, List, Any

# Add src to Python path
sys.path.append(os.path.join(os.path.dirname(__file__), 'src'))

from src.recommender import get_recommender
from src.data_loader import DataLoader

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)


class ComprehensiveModelAnalysis:
    """Detailed comparison analysis between hybrid and individual models"""
    
    def __init__(self):
        self.recommender = get_recommender()
        self.data_loader = DataLoader()
        
    def setup_mlflow_experiment(self):
        """Setup MLflow experiment for comprehensive analysis"""
        try:
            mlflow.set_tracking_uri("./mlruns")
            
            experiment_name = "Comprehensive_Model_Comparison"
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
    
    def analyze_recommendation_quality(self, user_id: int, strategy: str) -> Dict[str, Any]:
        """Analyze the quality and diversity of recommendations"""
        try:
            result = self.recommender.get_recommendations(
                user_id=user_id,
                strategy=strategy,
                n_recommendations=20
            )
            
            recommendations = result.get('recommendations', [])
            if not recommendations:
                return {'count': 0, 'diversity': 0, 'avg_score': 0}
            
            # Extract scores and movie info
            scores = []
            movie_ids = []
            
            for rec in recommendations:
                if isinstance(rec, dict):
                    if 'predicted_rating' in rec:
                        scores.append(rec['predicted_rating'])
                    elif 'score' in rec:
                        scores.append(rec['score'])
                    else:
                        scores.append(3.5)  # Default score
                    
                    if 'movie_id' in rec:
                        movie_ids.append(rec['movie_id'])
                    elif 'movieId' in rec:
                        movie_ids.append(rec['movieId'])
            
            # Calculate diversity (number of unique recommendations)
            diversity = len(set(movie_ids)) / len(movie_ids) if movie_ids else 0
            
            return {
                'count': len(recommendations),
                'diversity': diversity,
                'avg_score': np.mean(scores) if scores else 0,
                'score_std': np.std(scores) if scores else 0,
                'min_score': min(scores) if scores else 0,
                'max_score': max(scores) if scores else 0
            }
            
        except Exception as e:
            logger.warning(f"Error analyzing recommendations for user {user_id} with {strategy}: {str(e)}")
            return {'count': 0, 'diversity': 0, 'avg_score': 0, 'score_std': 0, 'min_score': 0, 'max_score': 0}
    
    def comprehensive_comparison(self, test_users: List[int] = None) -> Dict[str, Dict[str, float]]:
        """Comprehensive comparison between strategies"""
        if test_users is None:
            test_users = [1, 50, 100, 200, 500, 1000]  # Diverse user sample
        
        strategies = ['hybrid', 'collaborative', 'popularity']
        results = {strategy: {
            'success_count': 0,
            'total_recommendations': 0,
            'avg_diversity': 0,
            'avg_score': 0,
            'score_consistency': 0,
            'coverage': 0
        } for strategy in strategies}
        
        all_movies_recommended = {strategy: set() for strategy in strategies}
        
        logger.info("🔍 Running comprehensive strategy comparison...")
        
        for strategy in strategies:
            logger.info(f"  📊 Analyzing {strategy} strategy...")
            
            diversities = []
            scores = []
            score_stds = []
            successful_recommendations = 0
            
            for user_id in test_users:
                analysis = self.analyze_recommendation_quality(user_id, strategy)
                
                if analysis['count'] > 0:
                    successful_recommendations += 1
                    diversities.append(analysis['diversity'])
                    scores.append(analysis['avg_score'])
                    score_stds.append(analysis['score_std'])
                    
                    # Get movie IDs for coverage analysis
                    try:
                        result = self.recommender.get_recommendations(user_id=user_id, strategy=strategy, n_recommendations=10)
                        recommendations = result.get('recommendations', [])
                        for rec in recommendations:
                            if isinstance(rec, dict):
                                movie_id = rec.get('movie_id') or rec.get('movieId')
                                if movie_id:
                                    all_movies_recommended[strategy].add(movie_id)
                    except:
                        pass
            
            # Calculate aggregated metrics
            results[strategy]['success_count'] = successful_recommendations
            results[strategy]['success_rate'] = successful_recommendations / len(test_users)
            results[strategy]['avg_diversity'] = np.mean(diversities) if diversities else 0
            results[strategy]['avg_score'] = np.mean(scores) if scores else 0
            results[strategy]['score_consistency'] = 1 - np.mean(score_stds) if score_stds else 0
            results[strategy]['coverage'] = len(all_movies_recommended[strategy])
            results[strategy]['total_recommendations'] = successful_recommendations * 10  # Assuming 10 recs per user
            
            logger.info(f"    ✅ {strategy}: {successful_recommendations}/{len(test_users)} successful")
            logger.info(f"    📈 Avg diversity: {results[strategy]['avg_diversity']:.3f}")
            logger.info(f"    ⭐ Avg score: {results[strategy]['avg_score']:.3f}")
            logger.info(f"    📚 Coverage: {results[strategy]['coverage']} unique movies")
        
        return results
    
    def calculate_hybrid_advantages(self, comparison_results: Dict[str, Dict[str, float]]) -> Dict[str, float]:
        """Calculate specific advantages of hybrid model"""
        hybrid = comparison_results['hybrid']
        collaborative = comparison_results['collaborative']
        popularity = comparison_results['popularity']
        
        advantages = {}
        
        # Success rate improvements
        advantages['success_rate_vs_collaborative'] = ((hybrid['success_rate'] - collaborative['success_rate']) / collaborative['success_rate'] * 100) if collaborative['success_rate'] > 0 else 0
        advantages['success_rate_vs_popularity'] = ((hybrid['success_rate'] - popularity['success_rate']) / popularity['success_rate'] * 100) if popularity['success_rate'] > 0 else 0
        
        # Diversity improvements
        advantages['diversity_vs_collaborative'] = ((hybrid['avg_diversity'] - collaborative['avg_diversity']) / collaborative['avg_diversity'] * 100) if collaborative['avg_diversity'] > 0 else 0
        advantages['diversity_vs_popularity'] = ((hybrid['avg_diversity'] - popularity['avg_diversity']) / popularity['avg_diversity'] * 100) if popularity['avg_diversity'] > 0 else 0
        
        # Coverage improvements
        advantages['coverage_vs_collaborative'] = ((hybrid['coverage'] - collaborative['coverage']) / collaborative['coverage'] * 100) if collaborative['coverage'] > 0 else 0
        advantages['coverage_vs_popularity'] = ((hybrid['coverage'] - popularity['coverage']) / popularity['coverage'] * 100) if popularity['coverage'] > 0 else 0
        
        # Score quality improvements
        advantages['score_vs_collaborative'] = ((hybrid['avg_score'] - collaborative['avg_score']) / collaborative['avg_score'] * 100) if collaborative['avg_score'] > 0 else 0
        advantages['score_vs_popularity'] = ((hybrid['avg_score'] - popularity['avg_score']) / popularity['avg_score'] * 100) if popularity['avg_score'] > 0 else 0
        
        # Overall hybrid advantage score
        positive_improvements = sum(1 for v in advantages.values() if v > 0)
        total_metrics = len(advantages)
        advantages['overall_advantage_percentage'] = (positive_improvements / total_metrics) * 100
        
        return advantages
    
    def register_comprehensive_analysis(self, comparison_results: Dict[str, Dict[str, float]], 
                                      hybrid_advantages: Dict[str, float]):
        """Register comprehensive analysis in MLflow"""
        logger.info("📝 Registering comprehensive analysis in MLflow...")
        
        with mlflow.start_run(run_name=f"comprehensive_analysis_{datetime.now().strftime('%Y%m%d_%H%M%S')}"):
            
            # Log hybrid model performance
            hybrid_metrics = comparison_results['hybrid']
            for metric_name, value in hybrid_metrics.items():
                mlflow.log_metric(f"hybrid_{metric_name}", value)
            
            # Log collaborative model performance
            collab_metrics = comparison_results['collaborative']
            for metric_name, value in collab_metrics.items():
                mlflow.log_metric(f"collaborative_{metric_name}", value)
            
            # Log popularity model performance
            pop_metrics = comparison_results['popularity']
            for metric_name, value in pop_metrics.items():
                mlflow.log_metric(f"popularity_{metric_name}", value)
            
            # Log hybrid advantages
            for advantage_name, value in hybrid_advantages.items():
                mlflow.log_metric(f"advantage_{advantage_name}", value)
            
            # Determine if hybrid is superior
            hybrid_wins = hybrid_advantages['overall_advantage_percentage'] > 50
            mlflow.log_metric("hybrid_superiority_score", hybrid_advantages['overall_advantage_percentage'])
            mlflow.log_param("hybrid_wins_overall", hybrid_wins)
            
            # Log analysis parameters
            mlflow.log_param("analysis_type", "comprehensive_model_comparison")
            mlflow.log_param("models_compared", "hybrid,collaborative,popularity")
            mlflow.log_param("metrics_evaluated", "success_rate,diversity,coverage,score_quality")
            mlflow.log_param("test_users_count", 6)
            mlflow.log_param("evaluation_timestamp", datetime.now().isoformat())
            
            # Set tags
            mlflow.set_tag("analysis_status", "completed")
            mlflow.set_tag("hybrid_superior", "yes" if hybrid_wins else "no")
            mlflow.set_tag("evaluation_type", "production_ready")
            
            logger.info("✅ Comprehensive analysis registered in MLflow")
    
    def generate_detailed_report(self, comparison_results: Dict[str, Dict[str, float]], 
                               hybrid_advantages: Dict[str, float]) -> str:
        """Generate detailed analysis report"""
        lines = []
        lines.append("🎯 COMPREHENSIVE HYBRID MODEL ANALYSIS REPORT")
        lines.append("=" * 65)
        lines.append("")
        
        # Executive Summary
        hybrid_wins = hybrid_advantages['overall_advantage_percentage'] > 50
        lines.append("📋 EXECUTIVE SUMMARY")
        lines.append("-" * 25)
        if hybrid_wins:
            lines.append("🏆 RESULT: HYBRID MODEL OUTPERFORMS INDIVIDUAL MODELS")
            lines.append(f"   Overall Advantage: {hybrid_advantages['overall_advantage_percentage']:.1f}%")
        else:
            lines.append("⚠️  RESULT: MIXED PERFORMANCE - FURTHER OPTIMIZATION NEEDED")
            lines.append(f"   Overall Advantage: {hybrid_advantages['overall_advantage_percentage']:.1f}%")
        lines.append("")
        
        # Detailed Metrics Comparison
        lines.append("📊 DETAILED METRICS COMPARISON")
        lines.append("-" * 35)
        
        strategies = ['hybrid', 'collaborative', 'popularity']
        metrics = ['success_rate', 'avg_diversity', 'avg_score', 'coverage']
        metric_names = ['Success Rate', 'Diversity', 'Avg Score', 'Coverage']
        
        for i, metric in enumerate(metrics):
            lines.append(f"\n{metric_names[i]}:")
            for strategy in strategies:
                value = comparison_results[strategy][metric]
                if metric == 'success_rate':
                    lines.append(f"  {strategy.capitalize():<15}: {value:.1%}")
                elif metric == 'coverage':
                    lines.append(f"  {strategy.capitalize():<15}: {value:,.0f} movies")
                else:
                    lines.append(f"  {strategy.capitalize():<15}: {value:.3f}")
        
        # Hybrid Advantages
        lines.append("\n\n🚀 HYBRID MODEL ADVANTAGES")
        lines.append("-" * 30)
        
        advantage_categories = [
            ("Success Rate", "success_rate"),
            ("Diversity", "diversity"),
            ("Coverage", "coverage"),
            ("Score Quality", "score")
        ]
        
        for category, prefix in advantage_categories:
            vs_collab = hybrid_advantages.get(f'{prefix}_vs_collaborative', 0)
            vs_pop = hybrid_advantages.get(f'{prefix}_vs_popularity', 0)
            
            lines.append(f"\n{category}:")
            lines.append(f"  vs Collaborative: {vs_collab:+.1f}%")
            lines.append(f"  vs Popularity:    {vs_pop:+.1f}%")
        
        # Recommendations
        lines.append("\n\n💡 RECOMMENDATIONS")
        lines.append("-" * 20)
        
        if hybrid_wins:
            lines.append("✅ Deploy hybrid model to production")
            lines.append("✅ Monitor performance metrics continuously")
            lines.append("✅ Consider A/B testing for optimization")
        else:
            lines.append("⚠️  Optimize hybrid model weights")
            lines.append("⚠️  Consider additional strategies")
            lines.append("⚠️  Evaluate on larger test set")
        
        # Technical Details
        lines.append(f"\n\n🔧 TECHNICAL DETAILS")
        lines.append("-" * 20)
        lines.append(f"Test Users: 6")
        lines.append(f"Recommendations per User: 10-20")
        lines.append(f"Strategies Evaluated: 3")
        lines.append(f"Metrics Calculated: 8")
        lines.append(f"Evaluation Date: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        
        return "\n".join(lines)
    
    def run_comprehensive_analysis(self):
        """Run complete comprehensive analysis"""
        logger.info("🚀 Starting Comprehensive Hybrid Model Analysis...")
        
        try:
            # Setup MLflow
            self.setup_mlflow_experiment()
            
            # Run comprehensive comparison
            comparison_results = self.comprehensive_comparison()
            
            # Calculate hybrid advantages
            hybrid_advantages = self.calculate_hybrid_advantages(comparison_results)
            
            # Register in MLflow
            self.register_comprehensive_analysis(comparison_results, hybrid_advantages)
            
            # Generate detailed report
            report = self.generate_detailed_report(comparison_results, hybrid_advantages)
            print("\n" + report)
            
            # Save report
            with open("comprehensive_model_analysis_report.txt", "w", encoding='utf-8') as f:
                f.write(report)
            
            # Summary conclusion
            hybrid_wins = hybrid_advantages['overall_advantage_percentage'] > 50
            if hybrid_wins:
                logger.info("🎉 CONCLUSION: Hybrid model outperforms individual models!")
            else:
                logger.info("⚠️  CONCLUSION: Hybrid model shows mixed results - optimization needed")
            
            logger.info("✅ Comprehensive analysis completed!")
            logger.info("📄 Report saved to: comprehensive_model_analysis_report.txt")
            logger.info("🔗 View MLflow results: mlflow ui --backend-store-uri ./mlruns")
            
            return comparison_results, hybrid_advantages
            
        except Exception as e:
            logger.error(f"❌ Error during comprehensive analysis: {str(e)}")
            raise


if __name__ == "__main__":
    analyzer = ComprehensiveModelAnalysis()
    comparison_results, advantages = analyzer.run_comprehensive_analysis()
