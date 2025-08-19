"""
MLflow SVD Model Training and Loading Service

This module handles training SVD models and saving/loading them with MLflow.
"""

import mlflow
import mlflow.sklearn
import numpy as np
import pandas as pd
from surprise import SVD, Dataset, Reader
from surprise.model_selection import train_test_split
import joblib
import os
import logging
from typing import Optional, Tuple, Dict, Any
from pathlib import Path

logger = logging.getLogger(__name__)

class MLflowSVDService:
    """
    Service for training, saving, and loading SVD models with MLflow
    """
    
    def __init__(self, mlflow_tracking_uri: str = "./mlruns"):
        """
        Initialize MLflow SVD service
        
        Args:
            mlflow_tracking_uri: Path to MLflow tracking directory
        """
        self.tracking_uri = mlflow_tracking_uri
        mlflow.set_tracking_uri(mlflow_tracking_uri)
        
        # Set or create experiment
        experiment_name = "SVD_Recommendation_Experiments"
        try:
            experiment = mlflow.get_experiment_by_name(experiment_name)
            if experiment is None:
                experiment_id = mlflow.create_experiment(experiment_name)
                logger.info(f"Created new experiment: {experiment_name} (ID: {experiment_id})")
            else:
                experiment_id = experiment.experiment_id
                logger.info(f"Using existing experiment: {experiment_name} (ID: {experiment_id})")
            
            mlflow.set_experiment(experiment_name)
            
        except Exception as e:
            logger.warning(f"Could not set experiment: {e}. Using default experiment.")
        
        self.model_name = "SVD-Recommendation-Model"
        self.model = None
        self.trainset = None
        
    def train_and_save_model(
        self, 
        ratings_df: pd.DataFrame,
        n_factors: int = 100,
        n_epochs: int = 20,
        lr_all: float = 0.005,
        reg_all: float = 0.02
    ) -> str:
        """
        Train SVD model and save to MLflow
        
        Args:
            ratings_df: DataFrame with columns [userId, movieId, rating]
            n_factors: Number of factors for SVD
            n_epochs: Number of training epochs
            lr_all: Learning rate
            reg_all: Regularization parameter
            
        Returns:
            Model URI in MLflow
        """
        logger.info("Training SVD model with MLflow tracking...")
        
        with mlflow.start_run(run_name=f"SVD_Training_{pd.Timestamp.now().strftime('%Y%m%d_%H%M%S')}"):
            
            # Log parameters
            mlflow.log_param("n_factors", n_factors)
            mlflow.log_param("n_epochs", n_epochs)
            mlflow.log_param("lr_all", lr_all)
            mlflow.log_param("reg_all", reg_all)
            mlflow.log_param("num_ratings", len(ratings_df))
            mlflow.log_param("num_users", ratings_df['userId'].nunique())
            mlflow.log_param("num_movies", ratings_df['movieId'].nunique())
            
            # Prepare data for Surprise
            reader = Reader(rating_scale=(1, 5))
            data = Dataset.load_from_df(ratings_df[['userId', 'movieId', 'rating']], reader)
            
            # Train-test split
            trainset, testset = train_test_split(data, test_size=0.2, random_state=42)
            
            # Initialize and train SVD model
            svd_model = SVD(
                n_factors=n_factors,
                n_epochs=n_epochs,
                lr_all=lr_all,
                reg_all=reg_all,
                random_state=42
            )
            
            logger.info("Training SVD model...")
            svd_model.fit(trainset)
            self.model = svd_model
            self.trainset = trainset
            
            # Evaluate model
            from surprise import accuracy
            predictions = svd_model.test(testset)
            rmse = accuracy.rmse(predictions, verbose=False)
            mae = accuracy.mae(predictions, verbose=False)
            
            # Log metrics
            mlflow.log_metric("rmse", rmse)
            mlflow.log_metric("mae", mae)
            
            # Save model to temporary file
            temp_model_path = "temp_svd_model.pkl"
            joblib.dump({
                'model': svd_model,
                'trainset': trainset,
                'params': {
                    'n_factors': n_factors,
                    'n_epochs': n_epochs,
                    'lr_all': lr_all,
                    'reg_all': reg_all
                },
                'metrics': {
                    'rmse': rmse,
                    'mae': mae
                }
            }, temp_model_path)
            
            # Log model artifact
            mlflow.log_artifact(temp_model_path, "model")
            
            # Register model
            model_uri = mlflow.get_artifact_uri("model")
            
            try:
                mlflow.register_model(
                    model_uri=f"{model_uri}/{temp_model_path}",
                    name=self.model_name
                )
                logger.info(f"Model registered as {self.model_name}")
            except Exception as e:
                logger.warning(f"Model registration failed: {e}")
            
            # Clean up temp file
            if os.path.exists(temp_model_path):
                os.remove(temp_model_path)
            
            run_id = mlflow.active_run().info.run_id
            logger.info(f"SVD model trained and saved. Run ID: {run_id}")
            logger.info(f"RMSE: {rmse:.4f}, MAE: {mae:.4f}")
            
            return f"runs:/{run_id}/model/{temp_model_path}"
    
    def load_latest_model(self) -> bool:
        """
        Load the latest SVD model from MLflow
        
        Returns:
            True if model loaded successfully, False otherwise
        """
        try:
            logger.info("Loading latest SVD model from MLflow...")
            
            # Try to load from model registry first
            try:
                model_version = mlflow.MlflowClient().get_latest_versions(
                    self.model_name, 
                    stages=["None", "Staging", "Production"]
                )[0]
                
                model_uri = f"models:/{self.model_name}/{model_version.version}"
                logger.info(f"Loading model from registry: {model_uri}")
                
            except Exception as e:
                logger.info(f"Model registry not available: {e}")
                # Fallback: find latest run with SVD model
                model_uri = self._find_latest_model_uri()
                if not model_uri:
                    return False
            
            # Load model artifact
            model_path = mlflow.artifacts.download_artifacts(model_uri)
            
            if os.path.isfile(model_path):
                # Single file
                model_data = joblib.load(model_path)
            else:
                # Directory - find the model file
                model_files = [f for f in os.listdir(model_path) if f.endswith('.pkl')]
                if not model_files:
                    logger.error("No .pkl files found in model artifacts")
                    return False
                
                model_data = joblib.load(os.path.join(model_path, model_files[0]))
            
            # Extract model components
            self.model = model_data['model']
            self.trainset = model_data['trainset']
            
            logger.info("✅ SVD model loaded successfully from MLflow")
            logger.info(f"Model params: {model_data.get('params', {})}")
            logger.info(f"Model metrics: {model_data.get('metrics', {})}")
            
            return True
            
        except Exception as e:
            logger.error(f"Failed to load SVD model from MLflow: {e}")
            return False
    
    def _find_latest_model_uri(self) -> Optional[str]:
        """Find the latest model URI from MLflow runs"""
        try:
            client = mlflow.MlflowClient()
            experiments = client.search_experiments()
            
            latest_run = None
            latest_timestamp = 0
            
            for experiment in experiments:
                runs = client.search_runs(
                    experiment_ids=[experiment.experiment_id],
                    filter_string="tags.mlflow.runName LIKE 'SVD_Training_%'",
                    order_by=["start_time DESC"],
                    max_results=10
                )
                
                for run in runs:
                    if run.info.start_time > latest_timestamp:
                        # Check if run has model artifact
                        artifacts = client.list_artifacts(run.info.run_id, "model")
                        if artifacts:
                            latest_run = run
                            latest_timestamp = run.info.start_time
            
            if latest_run:
                model_files = [a.path for a in client.list_artifacts(latest_run.info.run_id, "model") 
                              if a.path.endswith('.pkl')]
                if model_files:
                    return f"runs:/{latest_run.info.run_id}/{model_files[0]}"
            
            return None
            
        except Exception as e:
            logger.error(f"Error finding latest model: {e}")
            return None
    
    def predict(self, user_id: int, movie_id: int) -> float:
        """
        Make prediction for user-movie pair
        
        Args:
            user_id: User ID
            movie_id: Movie ID
            
        Returns:
            Predicted rating
        """
        if not self.model:
            raise ValueError("Model not loaded. Call load_latest_model() first.")
        
        prediction = self.model.predict(user_id, movie_id)
        return prediction.est
    
    def get_user_recommendations(
        self, 
        user_id: int, 
        movie_ids: list, 
        n_recommendations: int = 10
    ) -> list:
        """
        Get recommendations for a user
        
        Args:
            user_id: User ID
            movie_ids: List of candidate movie IDs
            n_recommendations: Number of recommendations
            
        Returns:
            List of (movie_id, predicted_rating) tuples
        """
        if not self.model:
            raise ValueError("Model not loaded. Call load_latest_model() first.")
        
        predictions = []
        for movie_id in movie_ids:
            pred_rating = self.predict(user_id, movie_id)
            predictions.append((movie_id, pred_rating))
        
        # Sort by predicted rating and return top N
        predictions.sort(key=lambda x: x[1], reverse=True)
        return predictions[:n_recommendations]
    
    def is_model_loaded(self) -> bool:
        """Check if model is loaded and ready"""
        return self.model is not None and self.trainset is not None
