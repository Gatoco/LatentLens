"""
MLflow Model Registry and Ranking Evaluation Experiment

This script demonstrates:
1. Training an SVD model with hyperparameter optimization
2. Registering the best model in MLflow Model Registry
3. Evaluating the model using ranking metrics (Precision@k, Recall@k, etc.)
4. Comparing ranking performance with traditional RMSE metrics

Author: LatentLens Team
"""

import os
import sys
import pandas as pd
import numpy as np
from datetime import datetime
import mlflow
import mlflow.sklearn
from mlflow.tracking import MlflowClient
from surprise import SVD, Dataset, Reader, accuracy
from surprise.model_selection import cross_validate, GridSearchCV
import logging

# Add src to path for imports
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'src'))

from data_loader import DataLoader
from ranking_metrics import RankingMetrics, create_test_dataset_for_ranking_evaluation, format_ranking_metrics_report

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)


class ModelRegistryExperiment:
    """
    Class to manage MLflow model registry experiments with ranking evaluation.
    """
    
    def __init__(self, tracking_uri: str = "http://127.0.0.1:5000"):
        """
        Initialize the experiment.
        
        Args:
            tracking_uri (str): MLflow tracking server URI.
        """
        self.tracking_uri = tracking_uri
        self.client = MlflowClient(tracking_uri)
        
        # Set MLflow tracking URI
        mlflow.set_tracking_uri(tracking_uri)
        
        # Create or get experiment
        experiment_name = "SVD-Model-Registry-Ranking"
        try:
            experiment_id = mlflow.create_experiment(experiment_name)
        except mlflow.exceptions.MlflowException:
            experiment_id = mlflow.get_experiment_by_name(experiment_name).experiment_id
        
        mlflow.set_experiment(experiment_name)
        self.experiment_id = experiment_id
        
        logger.info(f"Using experiment: {experiment_name} (ID: {experiment_id})")
    
    def load_and_prepare_data(self, sample_size: int = 50000) -> tuple:
        """
        Load and prepare data for training and ranking evaluation.
        
        Args:
            sample_size (int): Number of ratings to sample for faster processing.
            
        Returns:
            tuple: (train_df, test_df, surprise_trainset)
        """
        logger.info("Loading and preparing data...")
        
        # Load data
        data_loader = DataLoader()
        ratings_df = data_loader.load_ratings()
        
        logger.info(f"Original dataset: {len(ratings_df)} ratings")
        
        # Sample for performance
        if len(ratings_df) > sample_size:
            ratings_df = ratings_df.sample(n=sample_size, random_state=42)
            logger.info(f"Sampled to {sample_size} ratings")
        
        # Create train/test split optimized for ranking evaluation
        train_df, test_df = create_test_dataset_for_ranking_evaluation(
            ratings_df, 
            test_size=0.2, 
            min_ratings_per_user=10,
            random_state=42
        )
        
        # Prepare Surprise dataset
        reader = Reader(rating_scale=(0.5, 5.0))
        surprise_data = Dataset.load_from_df(train_df[['userId', 'movieId', 'rating']], reader)
        surprise_trainset = surprise_data.build_full_trainset()
        
        return train_df, test_df, surprise_trainset
    
    def optimize_svd_hyperparameters(self, trainset) -> dict:
        """
        Optimize SVD hyperparameters using grid search.
        
        Args:
            trainset: Surprise trainset object.
            
        Returns:
            dict: Best hyperparameters.
        """
        logger.info("Optimizing SVD hyperparameters...")
        
        # Define parameter grid
        param_grid = {
            'n_factors': [50, 100, 150],
            'n_epochs': [20, 30],
            'lr_all': [0.005, 0.01],
            'reg_all': [0.02, 0.05]
        }
        
        # Grid search with cross-validation
        gs = GridSearchCV(SVD, param_grid, measures=['rmse'], cv=3, n_jobs=-1)
        gs.fit(Dataset.load_from_df(pd.DataFrame(), Reader()))
        
        best_params = gs.best_params['rmse']
        best_rmse = gs.best_score['rmse']
        
        logger.info(f"Best RMSE: {best_rmse:.4f}")
        logger.info(f"Best parameters: {best_params}")
        
        return best_params
    
    def train_and_evaluate_svd(self, trainset, test_df: pd.DataFrame, params: dict = None) -> tuple:
        """
        Train SVD model and evaluate with both RMSE and ranking metrics.
        
        Args:
            trainset: Surprise trainset object.
            test_df: Test dataframe for evaluation.
            params: SVD parameters (if None, uses defaults).
            
        Returns:
            tuple: (model, rmse, ranking_metrics_dict)
        """
        logger.info("Training SVD model...")
        
        # Use provided parameters or defaults
        if params is None:
            params = {
                'n_factors': 100,
                'n_epochs': 30,
                'lr_all': 0.005,
                'reg_all': 0.02
            }
        
        # Train model
        model = SVD(**params)
        model.fit(trainset)
        
        # Evaluate RMSE on test set
        testset = []
        for _, row in test_df.iterrows():
            testset.append((row['userId'], row['movieId'], row['rating']))
        
        predictions = model.test(testset)
        rmse = accuracy.rmse(predictions, verbose=False)
        
        logger.info(f"Test RMSE: {rmse:.4f}")
        
        # Evaluate ranking metrics
        ranking_metrics = self.evaluate_ranking_performance(model, test_df)
        
        return model, rmse, ranking_metrics
    
    def evaluate_ranking_performance(self, model, test_df: pd.DataFrame) -> dict:
        """
        Evaluate model using ranking metrics.
        
        Args:
            model: Trained Surprise model.
            test_df: Test dataframe.
            
        Returns:
            dict: Ranking metrics results.
        """
        logger.info("Evaluating ranking performance...")
        
        # Initialize ranking metrics evaluator
        ranking_evaluator = RankingMetrics(relevance_threshold=4.0)
        
        # Get unique users from test set
        test_users = test_df['userId'].unique()
        
        # Prepare predictions and ground truth for ranking evaluation
        all_predictions = {}
        all_ground_truth = {}
        
        # Get all unique movies for generating recommendations
        all_movies = test_df['movieId'].unique()
        
        for user_id in test_users[:100]:  # Limit to 100 users for performance
            # Get user's test ratings (ground truth)
            user_test_data = test_df[test_df['userId'] == user_id]
            ground_truth = dict(zip(user_test_data['movieId'].astype(str), user_test_data['rating']))
            
            # Generate predictions for all movies this user hasn't rated in training
            user_predictions = []
            for movie_id in all_movies:
                if movie_id not in ground_truth:  # Skip movies user has already rated
                    continue
                pred = model.predict(user_id, movie_id)
                user_predictions.append((str(movie_id), pred.est))
            
            # Sort by predicted rating (descending)
            user_predictions.sort(key=lambda x: x[1], reverse=True)
            
            all_predictions[str(user_id)] = user_predictions
            all_ground_truth[str(user_id)] = ground_truth
        
        # Evaluate ranking metrics
        ranking_results = ranking_evaluator.evaluate_model_performance(
            all_predictions, 
            all_ground_truth, 
            k_values=[5, 10, 20]
        )
        
        return ranking_results
    
    def register_model_in_mlflow(
        self, 
        model, 
        model_name: str, 
        rmse: float, 
        ranking_metrics: dict, 
        params: dict
    ) -> str:
        """
        Register model in MLflow Model Registry.
        
        Args:
            model: Trained model.
            model_name: Name for the registered model.
            rmse: RMSE performance.
            ranking_metrics: Ranking metrics results.
            params: Model parameters.
            
        Returns:
            str: Model version.
        """
        logger.info(f"Registering model '{model_name}' in MLflow...")
        
        with mlflow.start_run() as run:
            # Log parameters
            mlflow.log_params(params)
            
            # Log RMSE metric
            mlflow.log_metric("rmse", rmse)
            
            # Log ranking metrics
            for metric_name, k_results in ranking_metrics.items():
                for k, value in k_results.items():
                    mlflow.log_metric(f"{metric_name}_at_{k}", value)
            
            # Log ranking metrics summary as artifact
            metrics_report = format_ranking_metrics_report(ranking_metrics, model_name)
            with open("ranking_metrics_report.txt", "w", encoding='utf-8') as f:
                f.write(metrics_report)
            mlflow.log_artifact("ranking_metrics_report.txt")
            
            # Log model
            mlflow.sklearn.log_model(
                sk_model=model,
                artifact_path="model",
                registered_model_name=model_name
            )
            
            run_id = run.info.run_id
        
        # Get the registered model version
        model_version = self.client.get_latest_versions(model_name, stages=["None"])[0].version
        
        logger.info(f"Model registered successfully. Version: {model_version}")
        
        return model_version
    
    def run_complete_experiment(self, sample_size: int = 50000) -> dict:
        """
        Run the complete experiment: data preparation, training, evaluation, and registration.
        
        Args:
            sample_size: Number of ratings to use.
            
        Returns:
            dict: Experiment results.
        """
        logger.info("*** Starting complete MLflow Model Registry experiment...")
        
        # 1. Data preparation
        train_df, test_df, trainset = self.load_and_prepare_data(sample_size)
        
        # 2. Hyperparameter optimization (simplified for demo)
        best_params = {
            'n_factors': 100,
            'n_epochs': 30,
            'lr_all': 0.005,
            'reg_all': 0.02
        }
        
        # 3. Train and evaluate model
        model, rmse, ranking_metrics = self.train_and_evaluate_svd(trainset, test_df, best_params)
        
        # 4. Register model
        model_name = f"SVD_RecommendationModel_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        model_version = self.register_model_in_mlflow(model, model_name, rmse, ranking_metrics, best_params)
        
        # 5. Print results
        print("\n*** Experiment Complete! ***")
        print(f"Model registered: {model_name} (Version: {model_version})")
        print(f"RMSE: {rmse:.4f}")
        print(format_ranking_metrics_report(ranking_metrics, model_name))
        
        results = {
            'model_name': model_name,
            'model_version': model_version,
            'rmse': rmse,
            'ranking_metrics': ranking_metrics,
            'train_size': len(train_df),
            'test_size': len(test_df)
        }
        
        return results


def main():
    """
    Main function to run the experiment.
    """
    try:
        # Initialize experiment
        experiment = ModelRegistryExperiment()
        
        # Run complete experiment
        results = experiment.run_complete_experiment(sample_size=30000)
        
        logger.info("*** Experiment completed successfully!")
        
        return results
        
    except Exception as e:
        logger.error(f"*** Experiment failed: {str(e)}")
        raise


if __name__ == "__main__":
    results = main()
