"""
Demonstration Script for precision_recall_at_k Function

This script demonstrates the usage of the precision_recall_at_k function
that calculates Precision@k and Recall@k metrics from Surprise predictions.

Author: LatentLens Team
"""

import sys
import os
import pandas as pd
import numpy as np
from surprise import SVD, KNNBasic, Dataset, Reader
from surprise.model_selection import train_test_split

# Add src to path
sys.path.append(os.path.join(os.path.dirname(__file__), "..", "src"))

from data_loader import DataLoader
from evaluation import precision_recall_at_k
import logging

# Configure logging
logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)


def demonstrate_precision_recall_at_k():
    """
    Demonstrate the precision_recall_at_k function with real data.
    """
    print("DEMONSTRATION: precision_recall_at_k Function")
    print("=" * 60)

    # 1. Load and prepare data
    print("\nStep 1: Loading and preparing data...")
    data_loader = DataLoader()
    ratings_df = data_loader.load_ratings()

    # Sample for demonstration
    sample_size = 5000
    if len(ratings_df) > sample_size:
        ratings_df = ratings_df.sample(n=sample_size, random_state=42)
        print(f"   Sampled {sample_size} ratings for demonstration")

    # Prepare Surprise dataset
    reader = Reader(rating_scale=(0.5, 5.0))
    surprise_data = Dataset.load_from_df(
        ratings_df[["userId", "movieId", "rating"]], reader
    )

    # Create train/test split
    trainset, testset = train_test_split(surprise_data, test_size=0.2, random_state=42)

    print(f"   Train set: {len(trainset.all_ratings())} ratings")
    print(f"   Test set: {len(testset)} ratings")
    print("   Data preparation completed")

    # 2. Train models
    print("\nStep 2: Training models...")

    # SVD Model
    print("   Training SVD model...")
    svd_model = SVD(n_factors=50, n_epochs=20, random_state=42)
    svd_model.fit(trainset)

    # KNN Model
    print("   Training KNN model...")
    knn_model = KNNBasic(k=40, sim_options={"name": "cosine", "user_based": True})
    knn_model.fit(trainset)

    print("   Model training completed")

    # 3. Generate predictions
    print("\nStep 3: Generating predictions...")

    svd_predictions = svd_model.test(testset)
    knn_predictions = knn_model.test(testset)

    print(f"   SVD predictions: {len(svd_predictions)}")
    print(f"   KNN predictions: {len(knn_predictions)}")
    print("   Predictions generated")

    # 4. Evaluate with precision_recall_at_k
    print("\nStep 4: Evaluating with precision_recall_at_k...")

    # Different k values to test
    k_values = [5, 10, 20]

    # Different thresholds to test
    thresholds = [3.5, 4.0, 4.5]

    print("\nSVD MODEL RESULTS:")
    print("-" * 40)

    for k in k_values:
        for threshold in thresholds:
            result = precision_recall_at_k(svd_predictions, k=k, threshold=threshold)

            print(f"   K={k}, Threshold={threshold}:")
            print(f"     Precision@{k}: {result['precision_at_k']:.4f}")
            print(f"     Recall@{k}: {result['recall_at_k']:.4f}")
            print(f"     Users evaluated: {result['num_users']}")
            print()

    print("\nKNN MODEL RESULTS:")
    print("-" * 40)

    for k in k_values:
        for threshold in thresholds:
            result = precision_recall_at_k(knn_predictions, k=k, threshold=threshold)

            print(f"   K={k}, Threshold={threshold}:")
            print(f"     Precision@{k}: {result['precision_at_k']:.4f}")
            print(f"     Recall@{k}: {result['recall_at_k']:.4f}")
            print(f"     Users evaluated: {result['num_users']}")
            print()

    # 5. Comparative analysis
    print("\nStep 5: Comparative Analysis")
    print("=" * 50)

    # Compare models at standard settings (k=10, threshold=4.0)
    svd_result = precision_recall_at_k(svd_predictions, k=10, threshold=4.0)
    knn_result = precision_recall_at_k(knn_predictions, k=10, threshold=4.0)

    print("STANDARD COMPARISON (K=10, Threshold=4.0):")
    print("-" * 45)
    print(f"{'Model':<10} {'Precision@10':<15} {'Recall@10':<12} {'Users':<8}")
    print("-" * 45)
    print(
        f"{'SVD':<10} {svd_result['precision_at_k']:<15.4f} {svd_result['recall_at_k']:<12.4f} {svd_result['num_users']:<8}"
    )
    print(
        f"{'KNN':<10} {knn_result['precision_at_k']:<15.4f} {knn_result['recall_at_k']:<12.4f} {knn_result['num_users']:<8}"
    )

    # Determine better model
    if svd_result["precision_at_k"] > knn_result["precision_at_k"]:
        print(
            f"\nSVD has better Precision@10 (+{svd_result['precision_at_k'] - knn_result['precision_at_k']:.4f})"
        )
    else:
        print(
            f"\nKNN has better Precision@10 (+{knn_result['precision_at_k'] - svd_result['precision_at_k']:.4f})"
        )

    if svd_result["recall_at_k"] > knn_result["recall_at_k"]:
        print(
            f"SVD has better Recall@10 (+{svd_result['recall_at_k'] - knn_result['recall_at_k']:.4f})"
        )
    else:
        print(
            f"KNN has better Recall@10 (+{knn_result['recall_at_k'] - svd_result['recall_at_k']:.4f})"
        )


def demonstrate_function_features():
    """
    Demonstrate specific features and edge cases of precision_recall_at_k.
    """
    print("\nDEMONSTRATION: Function Features and Edge Cases")
    print("=" * 60)

    # Create mock prediction class for controlled testing
    class MockPrediction:
        def __init__(self, uid, iid, r_ui, est):
            self.uid = uid  # user id
            self.iid = iid  # item id
            self.r_ui = r_ui  # actual rating
            self.est = est  # estimated rating

    # 1. Perfect ranking scenario
    print("\nScenario 1: Perfect Ranking")
    print("-" * 35)
    perfect_predictions = [
        # User 1: Perfect ordering (highest est matches highest actual)
        MockPrediction(uid=1, iid=101, r_ui=5.0, est=5.0),
        MockPrediction(uid=1, iid=102, r_ui=4.5, est=4.8),
        MockPrediction(uid=1, iid=103, r_ui=3.0, est=3.2),
        MockPrediction(uid=1, iid=104, r_ui=2.0, est=2.5),
    ]

    result = precision_recall_at_k(perfect_predictions, k=2, threshold=4.0)
    print(f"Perfect ranking - Precision@2: {result['precision_at_k']:.4f}")
    print(f"Perfect ranking - Recall@2: {result['recall_at_k']:.4f}")

    # 2. Random ranking scenario
    print("\nScenario 2: Random Ranking")
    print("-" * 35)
    random_predictions = [
        # User 1: Random ordering (no correlation between est and actual)
        MockPrediction(uid=1, iid=101, r_ui=5.0, est=2.5),
        MockPrediction(uid=1, iid=102, r_ui=4.5, est=3.2),
        MockPrediction(uid=1, iid=103, r_ui=3.0, est=5.0),
        MockPrediction(uid=1, iid=104, r_ui=2.0, est=4.8),
    ]

    result = precision_recall_at_k(random_predictions, k=2, threshold=4.0)
    print(f"Random ranking - Precision@2: {result['precision_at_k']:.4f}")
    print(f"Random ranking - Recall@2: {result['recall_at_k']:.4f}")

    # 3. Multiple users scenario
    print("\nScenario 3: Multiple Users")
    print("-" * 35)
    multi_user_predictions = [
        # User 1: 2 relevant items (>= 4.0)
        MockPrediction(uid=1, iid=101, r_ui=4.5, est=4.8),
        MockPrediction(uid=1, iid=102, r_ui=3.0, est=4.2),
        MockPrediction(uid=1, iid=103, r_ui=4.2, est=3.8),
        # User 2: 1 relevant item
        MockPrediction(uid=2, iid=201, r_ui=5.0, est=4.9),
        MockPrediction(uid=2, iid=202, r_ui=3.5, est=4.1),
        # User 3: 3 relevant items
        MockPrediction(uid=3, iid=301, r_ui=4.8, est=4.7),
        MockPrediction(uid=3, iid=302, r_ui=4.2, est=4.3),
        MockPrediction(uid=3, iid=303, r_ui=4.0, est=4.1),
        MockPrediction(uid=3, iid=304, r_ui=3.5, est=3.9),
    ]

    result = precision_recall_at_k(multi_user_predictions, k=2, threshold=4.0)
    print(f"Multi-user (3 users) - Precision@2: {result['precision_at_k']:.4f}")
    print(f"Multi-user (3 users) - Recall@2: {result['recall_at_k']:.4f}")
    print(f"Users evaluated: {result['num_users']}")

    # 4. Edge case: No relevant items
    print("\nScenario 4: No Relevant Items")
    print("-" * 35)
    no_relevant_predictions = [
        MockPrediction(uid=1, iid=101, r_ui=3.0, est=3.5),
        MockPrediction(uid=1, iid=102, r_ui=2.5, est=3.2),
        MockPrediction(uid=2, iid=201, r_ui=3.5, est=3.8),
    ]

    result = precision_recall_at_k(no_relevant_predictions, k=2, threshold=4.0)
    print(f"No relevant items - Precision@2: {result['precision_at_k']:.4f}")
    print(f"No relevant items - Recall@2: {result['recall_at_k']:.4f}")
    print(f"Users evaluated: {result['num_users']}")

    print("\nFunction features demonstration completed!")


if __name__ == "__main__":
    try:
        # Main demonstration with real data
        demonstrate_precision_recall_at_k()

        # Feature demonstration with controlled examples
        demonstrate_function_features()

        print("\n" + "=" * 80)
        print("precision_recall_at_k demonstration completed successfully!")
        print("\nKey takeaways:")
        print("Function works with real Surprise prediction objects")
        print("Supports configurable k values and relevance thresholds")
        print("Handles multiple users and edge cases gracefully")
        print("Provides detailed metrics for model comparison")
        print("Averages results across all evaluated users")

    except Exception as e:
        logger.error(f"Demonstration failed: {str(e)}")
        print(f"\nError during demonstration: {str(e)}")
        raise
