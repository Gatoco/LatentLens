#!/usr/bin/env python3
"""
MLflow Hybrid Evaluation Script for LatentLens

This script evaluates the hybrid recommendation model with comprehensive
MLflow tracking and experiment management.

Author: LatentLens Team
License: MIT
"""

import sys
import os
import time
import logging
import json
import pandas as pd
import numpy as np
from datetime import datetime

# Add src to path for imports
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "..", "src"))

# Configure logging
logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)

try:
    import mlflow
    import mlflow.sklearn
    from mlflow.tracking import MlflowClient

    MLFLOW_AVAILABLE = True
except ImportError:
    logger.warning("MLflow not available, using mock implementation")
    MLFLOW_AVAILABLE = False


class MLflowHybridEvaluator:
    """MLflow-integrated evaluator for hybrid recommendation model."""

    def __init__(
        self,
        experiment_name="LatentLens_Hybrid_Evaluation",
        tracking_uri=None,
        data_path="data/ml-25m",
    ):
        """
        Initialize the MLflow hybrid evaluator.

        Args:
            experiment_name (str): Name of the MLflow experiment
            tracking_uri (str): MLflow tracking server URI
            data_path (str): Path to the MovieLens dataset
        """
        self.experiment_name = experiment_name
        self.data_path = data_path
        self.evaluation_results = {}

        if MLFLOW_AVAILABLE:
            if tracking_uri:
                mlflow.set_tracking_uri(tracking_uri)

            # Set or create experiment
            try:
                mlflow.set_experiment(experiment_name)
                self.experiment = mlflow.get_experiment_by_name(experiment_name)
                logger.info(f"Using MLflow experiment: {experiment_name}")
            except Exception as e:
                logger.warning(f"Could not set MLflow experiment: {e}")
                self.experiment = None
        else:
            self.experiment = None

    def start_evaluation_run(self, run_name=None):
        """Start MLflow evaluation run."""
        if not run_name:
            run_name = f"hybrid_evaluation_{datetime.now().strftime('%Y%m%d_%H%M%S')}"

        if MLFLOW_AVAILABLE and self.experiment:
            try:
                mlflow.start_run(run_name=run_name)
                logger.info(f"Started MLflow run: {run_name}")
                return True
            except Exception as e:
                logger.warning(f"Could not start MLflow run: {e}")
                return False
        else:
            logger.info(f"Mock MLflow run started: {run_name}")
            return True

    def log_parameters(self, params):
        """Log evaluation parameters to MLflow."""
        if MLFLOW_AVAILABLE:
            try:
                for key, value in params.items():
                    mlflow.log_param(key, value)
                logger.info(f"Logged {len(params)} parameters to MLflow")
            except Exception as e:
                logger.warning(f"Could not log parameters: {e}")
        else:
            logger.info(f"Mock parameter logging: {len(params)} parameters")

    def log_metrics(self, metrics, step=None):
        """Log evaluation metrics to MLflow."""
        if MLFLOW_AVAILABLE:
            try:
                for key, value in metrics.items():
                    if isinstance(value, (int, float)) and not np.isnan(value):
                        mlflow.log_metric(key, value, step=step)
                logger.info(f"Logged {len(metrics)} metrics to MLflow")
            except Exception as e:
                logger.warning(f"Could not log metrics: {e}")
        else:
            logger.info(f"Mock metrics logging: {len(metrics)} metrics")

    def log_artifact(self, file_path, artifact_path=None):
        """Log artifact to MLflow."""
        if MLFLOW_AVAILABLE:
            try:
                mlflow.log_artifact(file_path, artifact_path)
                logger.info(f"Logged artifact: {file_path}")
            except Exception as e:
                logger.warning(f"Could not log artifact: {e}")
        else:
            logger.info(f"Mock artifact logging: {file_path}")

    def load_and_prepare_data(self):
        """Load and prepare evaluation data."""
        logger.info("Loading evaluation data...")

        try:
            # Load ratings data
            ratings_path = os.path.join(self.data_path, "ratings.csv")
            if os.path.exists(ratings_path):
                # Load sample for evaluation (full dataset is too large for quick evaluation)
                self.ratings_df = pd.read_csv(ratings_path, nrows=50000)
                logger.info(f"Loaded {len(self.ratings_df)} ratings for evaluation")
            else:
                logger.info("Generating mock ratings data")
                self.ratings_df = self._generate_mock_ratings()

            # Load movies data
            movies_path = os.path.join(self.data_path, "movies.csv")
            if os.path.exists(movies_path):
                self.movies_df = pd.read_csv(movies_path)
                logger.info(f"Loaded {len(self.movies_df)} movies")
            else:
                logger.info("Generating mock movies data")
                self.movies_df = self._generate_mock_movies()

        except Exception as e:
            logger.error(f"Failed to load data: {e}")
            self.ratings_df = self._generate_mock_ratings()
            self.movies_df = self._generate_mock_movies()

    def _generate_mock_ratings(self):
        """Generate mock ratings for testing."""
        np.random.seed(42)
        data = []

        for user_id in range(1, 1001):  # 1000 users
            num_ratings = np.random.randint(10, 50)
            for _ in range(num_ratings):
                movie_id = np.random.randint(1, 101)  # 100 movies
                rating = np.random.choice([1, 2, 3, 4, 5], p=[0.1, 0.1, 0.2, 0.3, 0.3])
                data.append(
                    {
                        "userId": user_id,
                        "movieId": movie_id,
                        "rating": float(rating),
                        "timestamp": int(time.time()),
                    }
                )

        return pd.DataFrame(data)

    def _generate_mock_movies(self):
        """Generate mock movies for testing."""
        genres = [
            "Action",
            "Comedy",
            "Drama",
            "Horror",
            "Romance",
            "Sci-Fi",
            "Thriller",
        ]
        data = []

        for movie_id in range(1, 101):
            num_genres = np.random.randint(1, 3)
            movie_genres = np.random.choice(genres, num_genres, replace=False)
            data.append(
                {
                    "movieId": movie_id,
                    "title": f"Movie {movie_id} ({np.random.randint(1990, 2025)})",
                    "genres": "|".join(movie_genres),
                }
            )

        return pd.DataFrame(data)

    def evaluate_hybrid_model(self, test_size=0.2, num_test_users=50):
        """Evaluate hybrid model with comprehensive metrics."""
        logger.info("Starting hybrid model evaluation...")

        # Split data
        self.create_train_test_split(test_size)

        # Log dataset parameters
        dataset_params = {
            "total_ratings": len(self.ratings_df),
            "total_users": self.ratings_df["userId"].nunique(),
            "total_movies": len(self.movies_df),
            "train_size": len(self.train_df),
            "test_size": len(self.test_df),
            "test_ratio": test_size,
            "data_path": self.data_path,
        }
        self.log_parameters(dataset_params)

        # Initialize hybrid service (mock if not available)
        self.initialize_hybrid_service()

        # Model parameters
        model_params = {
            "model_type": "hybrid",
            "algorithms": ["svd", "knn", "content_based"],
            "weights": {"svd": 0.5, "knn": 0.3, "content": 0.2},
            "num_test_users": num_test_users,
        }
        self.log_parameters(model_params)

        # Run evaluations
        accuracy_metrics = self.evaluate_accuracy(num_test_users)
        coverage_metrics = self.evaluate_coverage(num_test_users)
        diversity_metrics = self.evaluate_diversity(num_test_users)
        performance_metrics = self.evaluate_performance(num_test_users)

        # Combine all metrics
        all_metrics = {
            **accuracy_metrics,
            **coverage_metrics,
            **diversity_metrics,
            **performance_metrics,
        }

        # Log metrics to MLflow
        self.log_metrics(all_metrics)

        # Store results
        self.evaluation_results = {
            "accuracy": accuracy_metrics,
            "coverage": coverage_metrics,
            "diversity": diversity_metrics,
            "performance": performance_metrics,
            "dataset_info": dataset_params,
            "model_config": model_params,
        }

        logger.info("Hybrid model evaluation completed")
        return all_metrics

    def create_train_test_split(self, test_size=0.2):
        """Create train/test split."""
        logger.info(f"Creating train/test split with {test_size} test ratio...")

        if "timestamp" in self.ratings_df.columns:
            self.ratings_df = self.ratings_df.sort_values("timestamp")

        split_idx = int(len(self.ratings_df) * (1 - test_size))
        self.train_df = self.ratings_df.iloc[:split_idx].copy()
        self.test_df = self.ratings_df.iloc[split_idx:].copy()

        logger.info(f"Train set: {len(self.train_df)} ratings")
        logger.info(f"Test set: {len(self.test_df)} ratings")

    def initialize_hybrid_service(self):
        """Initialize hybrid recommendation service."""
        try:
            from src.hybrid_recommendation_service import HybridRecommendationService

            self.hybrid_service = HybridRecommendationService(data_path=self.data_path)
            self.hybrid_service.initialize()
            logger.info("Hybrid service initialized")
        except Exception as e:
            logger.warning(f"Could not initialize hybrid service: {e}")
            self.hybrid_service = None

    def evaluate_accuracy(self, num_users=50):
        """Evaluate recommendation accuracy."""
        logger.info("Evaluating accuracy metrics...")

        test_users = self.test_df["userId"].unique()[:num_users]
        precisions = []
        recalls = []
        ndcg_scores = []

        for user_id in test_users:
            try:
                # Get test items for user
                user_test_items = self.test_df[self.test_df["userId"] == user_id][
                    "movieId"
                ].values

                if len(user_test_items) == 0:
                    continue

                # Get recommendations
                if self.hybrid_service:
                    recommendations = self.hybrid_service.get_recommendations(
                        user_id=int(user_id), num_recommendations=10
                    )
                    if recommendations and "recommendations" in recommendations:
                        rec_items = [
                            r["movie_id"] for r in recommendations["recommendations"]
                        ]
                    else:
                        rec_items = []
                else:
                    # Mock recommendations
                    rec_items = np.random.choice(
                        self.movies_df["movieId"].values, size=10, replace=False
                    ).tolist()

                # Calculate metrics
                relevant_items = set(user_test_items)
                recommended_items = set(rec_items)
                relevant_recommended = relevant_items & recommended_items

                precision = (
                    len(relevant_recommended) / len(recommended_items)
                    if recommended_items
                    else 0
                )
                recall = (
                    len(relevant_recommended) / len(relevant_items)
                    if relevant_items
                    else 0
                )

                precisions.append(precision)
                recalls.append(recall)

                # Simple NDCG calculation
                ndcg = self._calculate_ndcg(rec_items, user_test_items)
                ndcg_scores.append(ndcg)

            except Exception as e:
                logger.warning(f"Error evaluating user {user_id}: {e}")
                continue

        # Calculate averages
        avg_precision = np.mean(precisions) if precisions else 0
        avg_recall = np.mean(recalls) if recalls else 0
        avg_ndcg = np.mean(ndcg_scores) if ndcg_scores else 0
        avg_f1 = (
            2 * (avg_precision * avg_recall) / (avg_precision + avg_recall)
            if (avg_precision + avg_recall) > 0
            else 0
        )

        accuracy_metrics = {
            "precision_at_10": avg_precision,
            "recall_at_10": avg_recall,
            "ndcg_at_10": avg_ndcg,
            "f1_score": avg_f1,
            "num_users_evaluated": len(precisions),
        }

        logger.info(f"Accuracy evaluation completed for {len(precisions)} users")
        return accuracy_metrics

    def _calculate_ndcg(self, recommendations, relevant_items, k=10):
        """Calculate NDCG score."""
        if not recommendations or len(relevant_items) == 0:
            return 0.0

        relevant_set = set(relevant_items)
        dcg = 0.0

        for i, item_id in enumerate(recommendations[:k]):
            if item_id in relevant_set:
                dcg += 1.0 / np.log2(i + 2)

        # Ideal DCG
        idcg = sum(1.0 / np.log2(i + 2) for i in range(min(k, len(relevant_set))))

        return dcg / idcg if idcg > 0 else 0.0

    def evaluate_coverage(self, num_users=50):
        """Evaluate recommendation coverage."""
        logger.info("Evaluating coverage metrics...")

        test_users = self.test_df["userId"].unique()[:num_users]
        all_recommended_items = set()

        for user_id in test_users:
            try:
                if self.hybrid_service:
                    recommendations = self.hybrid_service.get_recommendations(
                        user_id=int(user_id), num_recommendations=10
                    )
                    if recommendations and "recommendations" in recommendations:
                        rec_items = [
                            r["movie_id"] for r in recommendations["recommendations"]
                        ]
                    else:
                        rec_items = []
                else:
                    # Mock recommendations
                    rec_items = np.random.choice(
                        self.movies_df["movieId"].values, size=10, replace=False
                    ).tolist()

                all_recommended_items.update(rec_items)

            except Exception as e:
                logger.warning(f"Error in coverage evaluation for user {user_id}: {e}")
                continue

        # Calculate coverage metrics
        total_items = len(self.movies_df)
        catalog_coverage = (
            len(all_recommended_items) / total_items if total_items > 0 else 0
        )

        coverage_metrics = {
            "catalog_coverage": catalog_coverage,
            "unique_items_recommended": len(all_recommended_items),
            "total_catalog_items": total_items,
            "coverage_percentage": catalog_coverage * 100,
        }

        logger.info("Coverage evaluation completed")
        return coverage_metrics

    def evaluate_diversity(self, num_users=50):
        """Evaluate recommendation diversity."""
        logger.info("Evaluating diversity metrics...")

        test_users = self.test_df["userId"].unique()[:num_users]
        genre_diversities = []
        intra_list_diversities = []

        for user_id in test_users:
            try:
                if self.hybrid_service:
                    recommendations = self.hybrid_service.get_recommendations(
                        user_id=int(user_id), num_recommendations=10
                    )
                    if recommendations and "recommendations" in recommendations:
                        rec_items = [
                            r["movie_id"] for r in recommendations["recommendations"]
                        ]
                    else:
                        rec_items = []
                else:
                    # Mock recommendations
                    rec_items = np.random.choice(
                        self.movies_df["movieId"].values, size=10, replace=False
                    ).tolist()

                # Calculate genre diversity
                user_genres = []
                for movie_id in rec_items:
                    movie_info = self.movies_df[self.movies_df["movieId"] == movie_id]
                    if not movie_info.empty and "genres" in movie_info.columns:
                        genres = movie_info.iloc[0]["genres"].split("|")
                        user_genres.extend(genres)

                unique_genres = len(set(user_genres))
                genre_diversities.append(unique_genres)

                # Calculate intra-list diversity (simplified)
                if len(rec_items) > 1:
                    diversity_score = len(set(rec_items)) / len(rec_items)
                    intra_list_diversities.append(diversity_score)

            except Exception as e:
                logger.warning(f"Error in diversity evaluation for user {user_id}: {e}")
                continue

        # Calculate average diversities
        avg_genre_diversity = np.mean(genre_diversities) if genre_diversities else 0
        avg_intra_list_diversity = (
            np.mean(intra_list_diversities) if intra_list_diversities else 0
        )

        diversity_metrics = {
            "avg_genre_diversity": avg_genre_diversity,
            "avg_intra_list_diversity": avg_intra_list_diversity,
            "genre_diversity_std": (
                np.std(genre_diversities) if genre_diversities else 0
            ),
            "num_users_diversity_evaluated": len(genre_diversities),
        }

        logger.info("Diversity evaluation completed")
        return diversity_metrics

    def evaluate_performance(self, num_users=20):
        """Evaluate system performance."""
        logger.info("Evaluating performance metrics...")

        test_users = self.test_df["userId"].unique()[:num_users]
        response_times = []

        for user_id in test_users:
            try:
                start_time = time.time()

                if self.hybrid_service:
                    recommendations = self.hybrid_service.get_recommendations(
                        user_id=int(user_id), num_recommendations=10
                    )
                else:
                    # Mock processing time
                    time.sleep(0.01)
                    recommendations = []

                end_time = time.time()
                response_time = end_time - start_time
                response_times.append(response_time)

            except Exception as e:
                logger.warning(
                    f"Error in performance evaluation for user {user_id}: {e}"
                )
                continue

        # Calculate performance metrics
        performance_metrics = {
            "avg_response_time": np.mean(response_times) if response_times else 0,
            "max_response_time": np.max(response_times) if response_times else 0,
            "min_response_time": np.min(response_times) if response_times else 0,
            "response_time_std": np.std(response_times) if response_times else 0,
            "throughput_rps": (
                1 / np.mean(response_times)
                if response_times and np.mean(response_times) > 0
                else 0
            ),
        }

        logger.info("Performance evaluation completed")
        return performance_metrics

    def save_evaluation_report(self):
        """Save evaluation report and log as artifact."""
        logger.info("Saving evaluation report...")

        report = {
            "evaluation_timestamp": datetime.now().isoformat(),
            "experiment_name": self.experiment_name,
            "evaluation_results": self.evaluation_results,
            "mlflow_tracking": MLFLOW_AVAILABLE and self.experiment is not None,
        }

        # Save report to file
        report_path = "mlflow_hybrid_evaluation_report.json"
        with open(report_path, "w") as f:
            json.dump(report, f, indent=2, default=str)

        # Log as MLflow artifact
        self.log_artifact(report_path, "evaluation_reports")

        logger.info(f"Evaluation report saved to {report_path}")
        return report_path

    def end_evaluation_run(self):
        """End MLflow evaluation run."""
        if MLFLOW_AVAILABLE:
            try:
                mlflow.end_run()
                logger.info("MLflow run ended")
            except Exception as e:
                logger.warning(f"Could not end MLflow run: {e}")
        else:
            logger.info("Mock MLflow run ended")

    def print_evaluation_summary(self):
        """Print evaluation summary."""
        print("\n" + "=" * 60)
        print("MLFLOW HYBRID EVALUATION SUMMARY")
        print("=" * 60)

        if self.evaluation_results:
            # Accuracy metrics
            if "accuracy" in self.evaluation_results:
                acc = self.evaluation_results["accuracy"]
                print(f"\nACCURACY METRICS:")
                print(f"  Precision@10: {acc.get('precision_at_10', 0):.4f}")
                print(f"  Recall@10: {acc.get('recall_at_10', 0):.4f}")
                print(f"  NDCG@10: {acc.get('ndcg_at_10', 0):.4f}")
                print(f"  F1-Score: {acc.get('f1_score', 0):.4f}")

            # Coverage metrics
            if "coverage" in self.evaluation_results:
                cov = self.evaluation_results["coverage"]
                print(f"\nCOVERAGE METRICS:")
                print(f"  Catalog Coverage: {cov.get('catalog_coverage', 0):.4f}")
                print(f"  Unique Items: {cov.get('unique_items_recommended', 0)}")

            # Diversity metrics
            if "diversity" in self.evaluation_results:
                div = self.evaluation_results["diversity"]
                print(f"\nDIVERSITY METRICS:")
                print(f"  Avg Genre Diversity: {div.get('avg_genre_diversity', 0):.2f}")
                print(
                    f"  Intra-list Diversity: {div.get('avg_intra_list_diversity', 0):.4f}"
                )

            # Performance metrics
            if "performance" in self.evaluation_results:
                perf = self.evaluation_results["performance"]
                print(f"\nPERFORMANCE METRICS:")
                print(f"  Avg Response Time: {perf.get('avg_response_time', 0):.4f}s")
                print(f"  Throughput: {perf.get('throughput_rps', 0):.1f} rps")

        print("\n" + "=" * 60)


def main():
    """Main evaluation function."""
    import argparse

    parser = argparse.ArgumentParser(description="MLflow Hybrid Model Evaluation")
    parser.add_argument(
        "--experiment",
        default="LatentLens_Hybrid_Evaluation",
        help="MLflow experiment name",
    )
    parser.add_argument("--tracking-uri", help="MLflow tracking server URI")
    parser.add_argument(
        "--test-users", type=int, default=50, help="Number of test users for evaluation"
    )
    parser.add_argument(
        "--test-size", type=float, default=0.2, help="Test set size ratio"
    )

    args = parser.parse_args()

    print("Starting MLflow Hybrid Model Evaluation...")

    try:
        # Initialize evaluator
        evaluator = MLflowHybridEvaluator(
            experiment_name=args.experiment, tracking_uri=args.tracking_uri
        )

        # Start MLflow run
        evaluator.start_evaluation_run()

        # Load data
        evaluator.load_and_prepare_data()

        # Run evaluation
        metrics = evaluator.evaluate_hybrid_model(
            test_size=args.test_size, num_test_users=args.test_users
        )

        # Save results
        report_path = evaluator.save_evaluation_report()

        # Print summary
        evaluator.print_evaluation_summary()

        # End MLflow run
        evaluator.end_evaluation_run()

        print(f"\nMLflow evaluation completed successfully!")
        print(f"Report saved to: {report_path}")

        if MLFLOW_AVAILABLE:
            print("Check MLflow UI for detailed tracking results")

    except Exception as e:
        logger.error(f"Evaluation failed: {e}")
        raise


if __name__ == "__main__":
    main()
