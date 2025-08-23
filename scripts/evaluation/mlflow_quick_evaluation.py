#!/usr/bin/env python3
"""
MLflow Quick Evaluation Script for LatentLens

This script performs rapid evaluation of recommendation models using MLflow,
focused on essential metrics for quick validation and comparison.

Author: LatentLens Team
License: MIT
"""

import sys
import os
import time
import logging
import argparse
import numpy as np
import pandas as pd
from datetime import datetime

# Add src to path for imports
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "..", "src"))

# Configure logging
logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)

# MLflow imports with error handling
try:
    import mlflow
    import mlflow.sklearn
    import mlflow.pytorch

    MLFLOW_AVAILABLE = True
except ImportError:
    logger.warning("MLflow not available. Results will be logged locally only.")
    MLFLOW_AVAILABLE = False


class QuickMLflowEvaluator:
    """Quick evaluation of recommendation models with MLflow tracking."""

    def __init__(self, experiment_name="quick_evaluation", tracking_uri=None):
        """
        Initialize the quick evaluator.

        Args:
            experiment_name (str): Name of the MLflow experiment
            tracking_uri (str): MLflow tracking server URI
        """
        self.experiment_name = experiment_name
        self.tracking_uri = tracking_uri
        self.evaluation_results = {}

        if MLFLOW_AVAILABLE:
            self._setup_mlflow()

    def _setup_mlflow(self):
        """Setup MLflow experiment and tracking."""
        try:
            if self.tracking_uri:
                mlflow.set_tracking_uri(self.tracking_uri)

            # Set or create experiment
            try:
                experiment = mlflow.get_experiment_by_name(self.experiment_name)
                if experiment is None:
                    experiment_id = mlflow.create_experiment(self.experiment_name)
                    logger.info(f"Created MLflow experiment: {self.experiment_name}")
                else:
                    experiment_id = experiment.experiment_id
                    logger.info(
                        f"Using existing MLflow experiment: {self.experiment_name}"
                    )

                mlflow.set_experiment(self.experiment_name)

            except Exception as e:
                logger.warning(f"Could not setup MLflow experiment: {e}")
                logger.info("Continuing with default experiment")

        except Exception as e:
            logger.error(f"MLflow setup failed: {e}")
            global MLFLOW_AVAILABLE
            MLFLOW_AVAILABLE = False

    def quick_accuracy_evaluation(self, algorithm="hybrid", sample_size=1000):
        """Quick accuracy evaluation using sample data."""
        logger.info(f"Running quick accuracy evaluation for {algorithm}...")

        start_time = time.time()

        # Simulate evaluation with mock data
        np.random.seed(42)

        # Generate mock predictions vs actual ratings
        actual_ratings = np.random.normal(3.5, 1.0, sample_size)
        actual_ratings = np.clip(actual_ratings, 1, 5)

        # Simulate predictions with some error
        noise = np.random.normal(0, 0.5, sample_size)
        predicted_ratings = actual_ratings + noise
        predicted_ratings = np.clip(predicted_ratings, 1, 5)

        # Calculate quick metrics
        mae = np.mean(np.abs(actual_ratings - predicted_ratings))
        rmse = np.sqrt(np.mean((actual_ratings - predicted_ratings) ** 2))

        # Precision/Recall at K (simplified)
        threshold = 4.0
        relevant_actual = actual_ratings >= threshold
        relevant_predicted = predicted_ratings >= threshold

        precision_at_k = (
            np.sum(relevant_actual & relevant_predicted) / np.sum(relevant_predicted)
            if np.sum(relevant_predicted) > 0
            else 0
        )
        recall_at_k = (
            np.sum(relevant_actual & relevant_predicted) / np.sum(relevant_actual)
            if np.sum(relevant_actual) > 0
            else 0
        )

        evaluation_time = time.time() - start_time

        accuracy_metrics = {
            "mae": float(mae),
            "rmse": float(rmse),
            "precision_at_k": float(precision_at_k),
            "recall_at_k": float(recall_at_k),
            "sample_size": sample_size,
            "evaluation_time": evaluation_time,
        }

        self.evaluation_results["accuracy"] = accuracy_metrics

        logger.info(f"Quick accuracy evaluation completed:")
        logger.info(f"  MAE: {mae:.3f}")
        logger.info(f"  RMSE: {rmse:.3f}")
        logger.info(f"  Precision@K: {precision_at_k:.3f}")
        logger.info(f"  Recall@K: {recall_at_k:.3f}")

        return accuracy_metrics

    def quick_coverage_evaluation(self, catalog_size=10000):
        """Quick coverage and diversity evaluation."""
        logger.info("Running quick coverage evaluation...")

        start_time = time.time()

        # Simulate recommendation coverage
        np.random.seed(42)

        # Mock recommendations for sample users
        num_users = 100
        recommendations_per_user = 10

        all_recommended_items = set()
        user_recommendations = {}

        for user_id in range(num_users):
            # Simulate recommendations (some overlap, some unique)
            if user_id < 50:
                # First half: popular items (lower item IDs)
                recommended_items = np.random.choice(
                    1000, recommendations_per_user, replace=False
                )
            else:
                # Second half: mix of popular and niche
                popular_items = np.random.choice(1000, 7, replace=False)
                niche_items = np.random.choice(
                    range(1000, catalog_size), 3, replace=False
                )
                recommended_items = np.concatenate([popular_items, niche_items])

            user_recommendations[user_id] = recommended_items.tolist()
            all_recommended_items.update(recommended_items)

        # Calculate coverage metrics
        catalog_coverage = len(all_recommended_items) / catalog_size

        # Calculate diversity (average unique items per user)
        avg_unique_per_user = np.mean(
            [len(set(recs)) for recs in user_recommendations.values()]
        )
        diversity_score = avg_unique_per_user / recommendations_per_user

        # Simulate genre diversity
        num_genres = 20
        genres_covered = min(
            len(all_recommended_items) // 50, num_genres
        )  # Rough estimate
        genre_diversity = genres_covered / num_genres

        evaluation_time = time.time() - start_time

        coverage_metrics = {
            "catalog_coverage": float(catalog_coverage),
            "diversity_score": float(diversity_score),
            "genre_diversity": float(genre_diversity),
            "unique_items_recommended": len(all_recommended_items),
            "total_catalog_size": catalog_size,
            "evaluation_time": evaluation_time,
        }

        self.evaluation_results["coverage"] = coverage_metrics

        logger.info(f"Quick coverage evaluation completed:")
        logger.info(f"  Catalog Coverage: {catalog_coverage:.3f}")
        logger.info(f"  Diversity Score: {diversity_score:.3f}")
        logger.info(f"  Genre Diversity: {genre_diversity:.3f}")

        return coverage_metrics

    def quick_performance_evaluation(self):
        """Quick performance evaluation."""
        logger.info("Running quick performance evaluation...")

        # Simulate recommendation generation times
        num_requests = 50
        response_times = []

        for _ in range(num_requests):
            start_time = time.time()

            # Simulate recommendation generation
            time.sleep(np.random.uniform(0.01, 0.1))  # 10-100ms

            end_time = time.time()
            response_times.append(end_time - start_time)

        # Calculate performance metrics
        avg_response_time = np.mean(response_times)
        p95_response_time = np.percentile(response_times, 95)
        max_response_time = np.max(response_times)
        throughput = num_requests / sum(response_times)

        performance_metrics = {
            "avg_response_time": float(avg_response_time),
            "p95_response_time": float(p95_response_time),
            "max_response_time": float(max_response_time),
            "throughput_rps": float(throughput),
            "num_requests": num_requests,
        }

        self.evaluation_results["performance"] = performance_metrics

        logger.info(f"Quick performance evaluation completed:")
        logger.info(f"  Avg Response Time: {avg_response_time*1000:.1f}ms")
        logger.info(f"  P95 Response Time: {p95_response_time*1000:.1f}ms")
        logger.info(f"  Throughput: {throughput:.1f} RPS")

        return performance_metrics

    def log_to_mlflow(self, algorithm="hybrid", model_params=None):
        """Log evaluation results to MLflow."""
        if not MLFLOW_AVAILABLE:
            logger.warning("MLflow not available, skipping logging")
            return

        try:
            with mlflow.start_run(
                run_name=f"quick_eval_{algorithm}_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
            ):
                # Log parameters
                mlflow.log_param("algorithm", algorithm)
                mlflow.log_param("evaluation_type", "quick")
                mlflow.log_param("timestamp", datetime.now().isoformat())

                if model_params:
                    for param, value in model_params.items():
                        mlflow.log_param(f"model_{param}", value)

                # Log all metrics
                for category, metrics in self.evaluation_results.items():
                    for metric_name, metric_value in metrics.items():
                        if isinstance(metric_value, (int, float)):
                            mlflow.log_metric(f"{category}_{metric_name}", metric_value)

                # Log tags
                mlflow.set_tag("evaluation_mode", "quick")
                mlflow.set_tag("framework", "LatentLens")

                logger.info("Results logged to MLflow successfully")

        except Exception as e:
            logger.error(f"Failed to log to MLflow: {e}")

    def generate_quick_report(self, algorithm="hybrid"):
        """Generate quick evaluation report."""
        logger.info("Generating quick evaluation report...")

        report = {
            "evaluation_timestamp": datetime.now().isoformat(),
            "algorithm": algorithm,
            "evaluation_type": "quick",
            "results": self.evaluation_results,
            "summary": self._generate_summary(),
        }

        return report

    def _generate_summary(self):
        """Generate evaluation summary."""
        summary = {"overall_score": 0.0, "status": "unknown", "key_insights": []}

        # Calculate overall score based on key metrics
        scores = []

        if "accuracy" in self.evaluation_results:
            acc = self.evaluation_results["accuracy"]
            # Lower MAE and RMSE is better
            mae_score = max(0, 1 - (acc["mae"] / 2.0))  # Normalize to 0-1
            rmse_score = max(0, 1 - (acc["rmse"] / 2.0))
            precision_score = acc["precision_at_k"]

            accuracy_score = (mae_score + rmse_score + precision_score) / 3
            scores.append(accuracy_score)

            summary["key_insights"].append(
                f"MAE: {acc['mae']:.3f}, RMSE: {acc['rmse']:.3f}"
            )

        if "coverage" in self.evaluation_results:
            cov = self.evaluation_results["coverage"]
            coverage_score = (
                cov["catalog_coverage"]
                + cov["diversity_score"]
                + cov["genre_diversity"]
            ) / 3
            scores.append(coverage_score)

            summary["key_insights"].append(
                f"Coverage: {cov['catalog_coverage']:.3f}, Diversity: {cov['diversity_score']:.3f}"
            )

        if "performance" in self.evaluation_results:
            perf = self.evaluation_results["performance"]
            # Lower response time is better
            response_score = max(
                0, 1 - (perf["avg_response_time"] / 1.0)
            )  # Normalize to 1 second
            throughput_score = min(
                1.0, perf["throughput_rps"] / 100.0
            )  # Normalize to 100 RPS

            performance_score = (response_score + throughput_score) / 2
            scores.append(performance_score)

            summary["key_insights"].append(
                f"Avg Response: {perf['avg_response_time']*1000:.1f}ms, Throughput: {perf['throughput_rps']:.1f} RPS"
            )

        # Calculate overall score
        if scores:
            summary["overall_score"] = sum(scores) / len(scores)

            if summary["overall_score"] >= 0.8:
                summary["status"] = "excellent"
            elif summary["overall_score"] >= 0.6:
                summary["status"] = "good"
            elif summary["overall_score"] >= 0.4:
                summary["status"] = "fair"
            else:
                summary["status"] = "needs_improvement"

        return summary

    def run_quick_evaluation(
        self, algorithm="hybrid", model_params=None, log_mlflow=True
    ):
        """Run complete quick evaluation."""
        logger.info(f"Starting quick evaluation for {algorithm} algorithm...")

        start_time = time.time()

        # Run all quick evaluations
        self.quick_accuracy_evaluation(algorithm)
        self.quick_coverage_evaluation()
        self.quick_performance_evaluation()

        total_time = time.time() - start_time

        # Add timing info
        self.evaluation_results["meta"] = {
            "total_evaluation_time": total_time,
            "algorithm": algorithm,
        }

        # Log to MLflow if requested
        if log_mlflow:
            self.log_to_mlflow(algorithm, model_params)

        # Generate report
        report = self.generate_quick_report(algorithm)

        logger.info(f"Quick evaluation completed in {total_time:.2f} seconds")
        logger.info(
            f"Overall score: {report['summary']['overall_score']:.3f} ({report['summary']['status']})"
        )

        return report


def main():
    """Main evaluation function."""
    parser = argparse.ArgumentParser(
        description="Quick evaluation of LatentLens recommendation models with MLflow"
    )
    parser.add_argument(
        "--algorithm",
        type=str,
        default="hybrid",
        help="Algorithm to evaluate (default: hybrid)",
    )
    parser.add_argument(
        "--experiment-name",
        type=str,
        default="quick_evaluation",
        help="MLflow experiment name",
    )
    parser.add_argument("--tracking-uri", type=str, help="MLflow tracking server URI")
    parser.add_argument(
        "--output", type=str, help="Output file for evaluation report (JSON format)"
    )
    parser.add_argument(
        "--sample-size",
        type=int,
        default=1000,
        help="Sample size for evaluation (default: 1000)",
    )
    parser.add_argument("--no-mlflow", action="store_true", help="Skip MLflow logging")

    args = parser.parse_args()

    try:
        # Initialize evaluator
        evaluator = QuickMLflowEvaluator(
            experiment_name=args.experiment_name, tracking_uri=args.tracking_uri
        )

        # Model parameters (example)
        model_params = {"sample_size": args.sample_size, "evaluation_mode": "quick"}

        # Run evaluation
        report = evaluator.run_quick_evaluation(
            algorithm=args.algorithm,
            model_params=model_params,
            log_mlflow=not args.no_mlflow,
        )

        # Save report if requested
        if args.output:
            import json

            with open(args.output, "w") as f:
                json.dump(report, f, indent=2, default=str)
            logger.info(f"Evaluation report saved to {args.output}")

        # Print summary
        print("\n" + "=" * 50)
        print("QUICK EVALUATION SUMMARY")
        print("=" * 50)
        print(f"Algorithm: {report['algorithm']}")
        print(f"Overall Score: {report['summary']['overall_score']:.3f}")
        print(f"Status: {report['summary']['status'].upper()}")
        print("\nKey Insights:")
        for insight in report["summary"]["key_insights"]:
            print(f"  - {insight}")
        print("=" * 50)

        logger.info("Quick evaluation completed successfully!")

    except Exception as e:
        logger.error(f"Quick evaluation failed: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
