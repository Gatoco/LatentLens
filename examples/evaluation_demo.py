"""
Demonstration Script for Evaluation Module

This script shows how to use the new evaluation.py module to perform
comprehensive evaluation of recommendation models, combining traditional
accuracy metrics with advanced ranking-based evaluation.

Author: LatentLens Team
"""

import sys
import os
import pandas as pd
import numpy as np
from surprise import SVD, KNNBasic, Dataset, Reader

# Add src to path
sys.path.append(os.path.join(os.path.dirname(__file__), "..", "src"))

from data_loader import DataLoader
from evaluation import ModelEvaluator, EvaluationPipeline, create_evaluation_dataset
import logging

# Configure logging
logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)


def demonstrate_evaluation_module():
    """
    Demonstrate the comprehensive evaluation capabilities of the evaluation module.
    """
    print("DEMONSTRATION: Comprehensive Model Evaluation Framework")
    print("=" * 80)

    # 1. Load and prepare data
    print("\nStep 1: Loading and preparing data...")
    data_loader = DataLoader()
    ratings_df = data_loader.load_ratings()

    # Sample for demonstration
    sample_size = 10000
    if len(ratings_df) > sample_size:
        ratings_df = ratings_df.sample(n=sample_size, random_state=42)
        print(f"   Sampled {sample_size} ratings for demonstration")

    # Create evaluation dataset
    train_df, test_df = create_evaluation_dataset(
        ratings_df, test_size=0.2, min_ratings_per_user=8, random_state=42
    )

    print(f"   Train set: {len(train_df)} ratings")
    print(f"   Test set: {len(test_df)} ratings")
    print(f"   Users in test: {test_df['userId'].nunique()}")

    # Prepare Surprise datasets
    reader = Reader(rating_scale=(0.5, 5.0))

    # Create Surprise trainset
    surprise_data = Dataset.load_from_df(
        train_df[["userId", "movieId", "rating"]], reader
    )
    surprise_trainset = surprise_data.build_full_trainset()

    # Create Surprise testset
    surprise_testset = []
    for _, row in test_df.iterrows():
        surprise_testset.append((row["userId"], row["movieId"], row["rating"]))

    print("   Data preparation completed")

    # 2. Initialize evaluation framework
    print("\nStep 2: Initializing evaluation framework...")
    evaluator = ModelEvaluator(
        relevance_threshold=4.0, k_values=[5, 10, 20], cv_folds=3, random_state=42
    )

    pipeline = EvaluationPipeline(evaluator)
    print("   Evaluation framework initialized")

    # 3. Define models for comparison
    print("\nStep 3: Defining models for evaluation...")
    models_config = [
        {
            "name": "SVD_Basic",
            "class": SVD,
            "params": {
                "n_factors": 50,
                "n_epochs": 20,
                "lr_all": 0.005,
                "reg_all": 0.02,
            },
        },
        {
            "name": "SVD_Optimized",
            "class": SVD,
            "params": {
                "n_factors": 100,
                "n_epochs": 30,
                "lr_all": 0.005,
                "reg_all": 0.02,
            },
        },
        {
            "name": "KNN_User_Based",
            "class": KNNBasic,
            "params": {"k": 40, "sim_options": {"name": "cosine", "user_based": True}},
        },
    ]

    for model in models_config:
        print(
            f"   - {model['name']}: {model['class'].__name__} with {len(model['params'])} parameters"
        )

    # 4. Run comprehensive evaluation
    print("\nStep 4: Running comprehensive evaluation...")
    print("   This may take a few minutes...")

    evaluation_results, comparison_table = pipeline.run_model_comparison(
        models_config=models_config,
        train_df=train_df,
        test_df=test_df,
        surprise_trainset=surprise_trainset,
        surprise_testset=surprise_testset,
    )

    print("   Evaluation completed")

    # 5. Display results
    print("\nStep 5: Results Analysis")
    print("=" * 50)

    # Individual model reports
    print("\nINDIVIDUAL MODEL REPORTS:")
    print("-" * 40)
    for result in evaluation_results:
        report = evaluator.generate_evaluation_report(result, include_details=True)
        print(report)
        print()

    # Comparison table
    print("\nMODEL COMPARISON TABLE:")
    print("-" * 30)
    print(comparison_table.to_string(index=False, float_format="%.4f"))

    # Best model analysis
    best_rmse_model = comparison_table.iloc[0]["Model"]
    best_rmse_value = comparison_table.iloc[0]["RMSE"]

    if "precision_at_10" in comparison_table.columns:
        best_precision_idx = comparison_table["precision_at_10"].idxmax()
        best_precision_model = comparison_table.iloc[best_precision_idx]["Model"]
        best_precision_value = comparison_table.iloc[best_precision_idx][
            "precision_at_10"
        ]
    else:
        best_precision_model = "N/A"
        best_precision_value = 0.0

    print("\nSUMMARY:")
    print(f"   Best RMSE: {best_rmse_model} ({best_rmse_value:.4f})")
    print(f"   Best Precision@10: {best_precision_model} ({best_precision_value:.4f})")

    # 6. Demonstrate quick evaluation functions
    print("\nStep 6: Quick evaluation functions demonstration...")

    # Train a simple model for quick evaluation
    quick_model = SVD(n_factors=50, n_epochs=10)
    quick_model.fit(surprise_trainset)

    # Quick RMSE
    from evaluation import quick_rmse_evaluation, quick_ranking_evaluation

    quick_rmse = quick_rmse_evaluation(quick_model, surprise_testset[:100])
    print(f"   Quick RMSE (100 predictions): {quick_rmse:.4f}")

    # Quick ranking evaluation
    quick_ranking = quick_ranking_evaluation(
        quick_model, test_df.head(50), k=10, relevance_threshold=4.0, max_users=10
    )

    print(f"   Quick Ranking Metrics (10 users):")
    for metric, value in quick_ranking.items():
        print(f"     {metric}: {value:.4f}")

    print("\nDemonstration completed successfully!")
    print("\nThe evaluation module provides:")
    print("Comprehensive evaluation combining traditional and ranking metrics")
    print("Model comparison pipeline for systematic evaluation")
    print("Flexible configuration for different evaluation scenarios")
    print("Quick evaluation functions for rapid testing")
    print("Detailed reporting and analysis capabilities")


def demonstrate_cross_validation():
    """
    Demonstrate cross-validation capabilities.
    """
    print("\nBONUS: Cross-Validation Demonstration")
    print("-" * 50)

    # Load small dataset for CV
    data_loader = DataLoader()
    ratings_df = data_loader.load_ratings().sample(n=5000, random_state=42)

    # Prepare Surprise dataset
    reader = Reader(rating_scale=(0.5, 5.0))
    surprise_data = Dataset.load_from_df(
        ratings_df[["userId", "movieId", "rating"]], reader
    )

    # Initialize evaluator
    evaluator = ModelEvaluator(cv_folds=3)

    # Perform cross-validation
    print("   Running 3-fold cross-validation...")
    cv_results = evaluator.cross_validate_model(
        model_class=SVD,
        data=surprise_data,
        model_params={"n_factors": 50, "n_epochs": 10},
        metrics=["rmse", "mae"],
    )

    # Display CV results
    print("   Cross-Validation Results:")
    for metric, values in cv_results.items():
        mean_val = np.mean(values)
        std_val = np.std(values)
        print(f"     {metric.upper()}: {mean_val:.4f} (±{std_val:.4f})")
        print(f"       Individual folds: {[f'{v:.4f}' for v in values]}")


if __name__ == "__main__":
    try:
        # Main demonstration
        demonstrate_evaluation_module()

        # Cross-validation demonstration
        demonstrate_cross_validation()

        print("\n" + "=" * 80)
        print("All demonstrations completed successfully!")
        print("The evaluation module is ready for use in LatentLens.")

    except Exception as e:
        logger.error(f"Demonstration failed: {str(e)}")
        print(f"\nError during demonstration: {str(e)}")
        raise
