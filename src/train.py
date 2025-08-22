#!/usr/bin/env python3
"""
LatentLens Training Pipeline
===========================

Script principal para entrenar el sistema de recomendaciones híbrido.
Ejecuta todos los pasos en orden: carga, preprocesamiento, entrenamiento,
evaluación y guardado de artefactos.

Uso:
    python src/train.py [--config config.yaml] [--experiment-name nombre]

Autor: Gatoco
Fecha: 21 de Agosto, 2025
"""

import os
import sys
import json
import pickle
import argparse
import logging
from datetime import datetime
from pathlib import Path
from typing import Dict, Any, Tuple, List

import pandas as pd
import numpy as np
import mlflow
import mlflow.sklearn
from sklearn.model_selection import train_test_split
from sklearn.metrics import mean_squared_error
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
from sklearn.neighbors import NearestNeighbors
from surprise import SVD, Dataset, Reader
from surprise.model_selection import train_test_split as surprise_train_test_split
from surprise import accuracy

# Añadir el directorio src al path para importaciones
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# Importar módulos locales
from data_loader import DataLoader
from models.unified_recommender import UnifiedRecommender

# Configuración de logging
log_dir = Path("logs")
log_dir.mkdir(exist_ok=True)

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler(log_dir / 'training.log'),
        logging.StreamHandler(sys.stdout)
    ]
)
logger = logging.getLogger(__name__)


class TrainingPipeline:
    """Pipeline completo de entrenamiento para LatentLens."""
    
    def __init__(self, config: Dict[str, Any]):
        """
        Inicializa el pipeline con configuración.
        
        Args:
            config: Diccionario con parámetros de configuración
        """
        self.config = config
        self.data_loader = None
        self.models = {}
        self.metrics = {}
        self.artifacts_dir = Path("artifacts")
        self.artifacts_dir.mkdir(exist_ok=True)
        
        # Crear directorio de logs
        Path("logs").mkdir(exist_ok=True)
        
        logger.info("🚀 Inicializando LatentLens Training Pipeline")
        logger.info(f"📊 Configuración: {config}")
    
    def load_and_preprocess_data(self) -> Tuple[pd.DataFrame, pd.DataFrame, pd.DataFrame]:
        """
        Carga y preprocesa los datos.
        
        Returns:
            Tuple con (ratings, movies, processed_data)
        """
        logger.info("📂 Cargando datos...")
        
        # Cargar datos usando el data loader existente
        self.data_loader = DataLoader("data/ml-25m")
        ratings = self.data_loader.load_ratings()
        movies = self.data_loader.load_movies()
        
        logger.info(f"✅ Datos cargados: {len(ratings)} ratings, {len(movies)} movies")
        
        # Aplicar sampling si está configurado
        if self.config.get('sample_size'):
            sample_size = self.config['sample_size']
            logger.info(f"🎯 Aplicando sampling: {sample_size} usuarios")
            
            # Seleccionar usuarios más activos
            user_counts = ratings['userId'].value_counts()
            top_users = user_counts.head(sample_size).index
            ratings = ratings[ratings['userId'].isin(top_users)]
            
            logger.info(f"📊 Datos después del sampling: {len(ratings)} ratings")
        
        # Preprocesar datos para diferentes modelos
        processed_data = self._preprocess_for_models(ratings, movies)
        
        return ratings, movies, processed_data
    
    def _preprocess_for_models(self, ratings: pd.DataFrame, movies: pd.DataFrame) -> Dict[str, Any]:
        """
        Preprocesa datos para diferentes tipos de modelos.
        
        Args:
            ratings: DataFrame de ratings
            movies: DataFrame de movies
            
        Returns:
            Diccionario con datos procesados para cada modelo
        """
        logger.info("🔄 Preprocesando datos para modelos...")
        
        processed = {}
        
        # Datos para Collaborative Filtering (Surprise)
        reader = Reader(rating_scale=(0.5, 5.0))
        data = Dataset.load_from_df(ratings[['userId', 'movieId', 'rating']], reader)
        processed['surprise_data'] = data
        
        # Matriz user-item para modelos basados en similaridad
        user_item_matrix = ratings.pivot_table(
            index='userId', 
            columns='movieId', 
            values='rating',
            fill_value=0
        )
        processed['user_item_matrix'] = user_item_matrix
        
        # Features de contenido para Content-Based
        if 'genres' in movies.columns:
            # Crear features TF-IDF de géneros
            tfidf = TfidfVectorizer(stop_words='english', max_features=100)
            genre_features = tfidf.fit_transform(movies['genres'].fillna(''))
            processed['content_features'] = genre_features
            processed['tfidf_vectorizer'] = tfidf
        
        # Datos para popularidad
        movie_popularity = ratings.groupby('movieId').agg({
            'rating': ['count', 'mean']
        }).round(2)
        movie_popularity.columns = ['vote_count', 'vote_average']
        movie_popularity = movie_popularity.reset_index()
        processed['popularity_data'] = movie_popularity
        
        logger.info("✅ Preprocesamiento completado")
        return processed
    
    def train_models(self, ratings: pd.DataFrame, processed_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Entrena todos los modelos del sistema híbrido.
        
        Args:
            ratings: DataFrame de ratings
            processed_data: Datos preprocesados
            
        Returns:
            Diccionario con modelos entrenados
        """
        logger.info("🤖 Entrenando modelos...")
        
        models = {}
        
        # 1. Collaborative Filtering (SVD)
        logger.info("🎯 Entrenando Collaborative Filtering (SVD)...")
        trainset, testset = surprise_train_test_split(
            processed_data['surprise_data'], 
            test_size=self.config.get('test_size', 0.2)
        )
        
        svd_model = SVD(
            n_factors=self.config.get('n_factors', 100),
            n_epochs=self.config.get('n_epochs', 20),
            lr_all=self.config.get('learning_rate', 0.005),
            reg_all=self.config.get('regularization', 0.02)
        )
        svd_model.fit(trainset)
        models['collaborative'] = {
            'model': svd_model,
            'trainset': trainset,
            'testset': testset
        }
        logger.info("✅ SVD entrenado")
        
        # 2. Item-to-Item Similarity (KNN)
        if 'user_item_matrix' in processed_data:
            logger.info("🎯 Entrenando Item Similarity (KNN)...")
            knn_model = NearestNeighbors(
                n_neighbors=self.config.get('k_neighbors', 20),
                metric=self.config.get('similarity_metric', 'cosine')
            )
            # Transponer para item-item similarity
            item_features = processed_data['user_item_matrix'].T
            knn_model.fit(item_features)
            models['item_similarity'] = {
                'model': knn_model,
                'item_features': item_features
            }
            logger.info("✅ KNN entrenado")
        
        # 3. Content-Based (TF-IDF + Cosine Similarity)
        if 'content_features' in processed_data:
            logger.info("🎯 Calculando Content-Based Similarity...")
            content_sim_matrix = cosine_similarity(processed_data['content_features'])
            models['content_based'] = {
                'similarity_matrix': content_sim_matrix,
                'vectorizer': processed_data['tfidf_vectorizer']
            }
            logger.info("✅ Content-Based preparado")
        
        # 4. Popularity Baseline
        models['popularity'] = {
            'data': processed_data['popularity_data']
        }
        logger.info("✅ Popularity baseline preparado")
        
        self.models = models
        logger.info(f"🎉 Todos los modelos entrenados: {list(models.keys())}")
        return models
    
    def evaluate_models(self, ratings: pd.DataFrame) -> Dict[str, float]:
        """
        Evalúa todos los modelos con métricas estándar.
        
        Args:
            ratings: DataFrame de ratings para evaluación
            
        Returns:
            Diccionario con métricas de evaluación
        """
        logger.info("📊 Evaluando modelos...")
        
        metrics = {}
        
        # Evaluar Collaborative Filtering
        if 'collaborative' in self.models:
            logger.info("🎯 Evaluando Collaborative Filtering...")
            testset = self.models['collaborative']['testset']
            model = self.models['collaborative']['model']
            
            predictions = model.test(testset)
            rmse = accuracy.rmse(predictions, verbose=False)
            mae = accuracy.mae(predictions, verbose=False)
            
            metrics['collaborative'] = {
                'rmse': rmse,
                'mae': mae,
                'model_type': 'SVD'
            }
            logger.info(f"✅ Collaborative - RMSE: {rmse:.4f}, MAE: {mae:.4f}")
        
        # Evaluar sistema híbrido
        logger.info("🎯 Evaluando sistema híbrido...")
        sample_users = ratings['userId'].unique()[:self.config.get('eval_users', 10)]
        
        hybrid_scores = []
        for user_id in sample_users:
            try:
                # Simular recomendaciones híbridas
                user_ratings = ratings[ratings['userId'] == user_id]
                if len(user_ratings) > 5:  # Usuario con suficientes ratings
                    # Calcular score híbrido simple
                    avg_rating = user_ratings['rating'].mean()
                    rating_count = len(user_ratings)
                    hybrid_score = (avg_rating * np.log(rating_count + 1)) / 10
                    hybrid_scores.append(hybrid_score)
            except Exception as e:
                logger.warning(f"Error evaluando usuario {user_id}: {e}")
                continue
        
        if hybrid_scores:
            metrics['hybrid'] = {
                'mean_score': np.mean(hybrid_scores),
                'std_score': np.std(hybrid_scores),
                'users_evaluated': len(hybrid_scores)
            }
            logger.info(f"✅ Híbrido - Score promedio: {np.mean(hybrid_scores):.4f}")
        
        # Métricas de diversidad
        unique_movies = len(ratings['movieId'].unique())
        total_ratings = len(ratings)
        diversity_score = unique_movies / total_ratings if total_ratings > 0 else 0
        
        metrics['system'] = {
            'total_movies': unique_movies,
            'total_ratings': total_ratings,
            'diversity_score': diversity_score,
            'sparsity': 1 - (total_ratings / (len(ratings['userId'].unique()) * unique_movies))
        }
        
        self.metrics = metrics
        logger.info("📊 Evaluación completada")
        return metrics
    
    def save_artifacts(self) -> Dict[str, str]:
        """
        Guarda todos los artefactos del entrenamiento.
        
        Returns:
            Diccionario con rutas de artefactos guardados
        """
        logger.info("💾 Guardando artefactos...")
        
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        artifacts = {}
        
        # Guardar modelos
        models_dir = self.artifacts_dir / "models" / timestamp
        models_dir.mkdir(parents=True, exist_ok=True)
        
        for model_name, model_data in self.models.items():
            try:
                model_path = models_dir / f"{model_name}_model.pkl"
                with open(model_path, 'wb') as f:
                    pickle.dump(model_data, f)
                artifacts[f"{model_name}_model"] = str(model_path)
                logger.info(f"✅ Modelo {model_name} guardado en {model_path}")
            except Exception as e:
                logger.error(f"❌ Error guardando modelo {model_name}: {e}")
        
        # Guardar métricas
        metrics_path = self.artifacts_dir / f"metrics_{timestamp}.json"
        with open(metrics_path, 'w') as f:
            # Convertir numpy arrays a listas para JSON
            metrics_serializable = {}
            for key, value in self.metrics.items():
                if isinstance(value, dict):
                    metrics_serializable[key] = {
                        k: float(v) if isinstance(v, (np.floating, np.integer)) else v
                        for k, v in value.items()
                    }
                else:
                    metrics_serializable[key] = float(value) if isinstance(value, (np.floating, np.integer)) else value
            
            json.dump(metrics_serializable, f, indent=2)
        artifacts['metrics'] = str(metrics_path)
        logger.info(f"✅ Métricas guardadas en {metrics_path}")
        
        # Guardar configuración
        config_path = self.artifacts_dir / f"config_{timestamp}.json"
        with open(config_path, 'w') as f:
            json.dump(self.config, f, indent=2)
        artifacts['config'] = str(config_path)
        logger.info(f"✅ Configuración guardada en {config_path}")
        
        # Crear resumen del entrenamiento
        summary = {
            'timestamp': timestamp,
            'models_trained': list(self.models.keys()),
            'metrics_summary': self.metrics,
            'config': self.config,
            'artifacts': artifacts
        }
        
        summary_path = self.artifacts_dir / f"training_summary_{timestamp}.json"
        with open(summary_path, 'w') as f:
            json.dump(summary, f, indent=2, default=str)
        artifacts['summary'] = str(summary_path)
        
        logger.info(f"💾 Todos los artefactos guardados en {self.artifacts_dir}")
        return artifacts
    
    def run_mlflow_experiment(self, experiment_name: str) -> str:
        """
        Ejecuta el entrenamiento dentro de un experimento MLflow.
        
        Args:
            experiment_name: Nombre del experimento
            
        Returns:
            ID del run de MLflow
        """
        logger.info(f"🧪 Iniciando experimento MLflow: {experiment_name}")
        
        # Configurar MLflow
        mlflow.set_experiment(experiment_name)
        
        with mlflow.start_run() as run:
            # Log de parámetros
            mlflow.log_params(self.config)
            
            # Entrenar pipeline completo
            ratings, movies, processed_data = self.load_and_preprocess_data()
            models = self.train_models(ratings, processed_data)
            metrics = self.evaluate_models(ratings)
            artifacts = self.save_artifacts()
            
            # Log de métricas en MLflow
            for model_name, model_metrics in metrics.items():
                if isinstance(model_metrics, dict):
                    for metric_name, metric_value in model_metrics.items():
                        if isinstance(metric_value, (int, float)):
                            mlflow.log_metric(f"{model_name}_{metric_name}", metric_value)
            
            # Log de artefactos
            for artifact_name, artifact_path in artifacts.items():
                try:
                    mlflow.log_artifact(artifact_path)
                except Exception as e:
                    logger.warning(f"No se pudo logear artefacto {artifact_name}: {e}")
            
            # Log del modelo principal (si existe)
            if 'collaborative' in models:
                try:
                    mlflow.sklearn.log_model(
                        models['collaborative']['model'],
                        "collaborative_model"
                    )
                except Exception as e:
                    logger.warning(f"No se pudo logear modelo en MLflow: {e}")
            
            run_id = run.info.run_id
            logger.info(f"🎉 Experimento completado. Run ID: {run_id}")
            return run_id


def parse_arguments() -> argparse.Namespace:
    """Parsea argumentos de línea de comandos."""
    parser = argparse.ArgumentParser(
        description="LatentLens Training Pipeline",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Ejemplos:
    python src/train.py
    python src/train.py --experiment-name "hybrid_v2"
    python src/train.py --sample-size 1000 --n-factors 50
        """
    )
    
    parser.add_argument(
        '--experiment-name',
        type=str,
        default='latentlens_training',
        help='Nombre del experimento MLflow'
    )
    
    parser.add_argument(
        '--sample-size',
        type=int,
        default=None,
        help='Número de usuarios para sampling (None = todos)'
    )
    
    parser.add_argument(
        '--n-factors',
        type=int,
        default=100,
        help='Número de factores latentes para SVD'
    )
    
    parser.add_argument(
        '--n-epochs',
        type=int,
        default=20,
        help='Número de épocas para entrenamiento SVD'
    )
    
    parser.add_argument(
        '--test-size',
        type=float,
        default=0.2,
        help='Proporción de datos para test'
    )
    
    parser.add_argument(
        '--k-neighbors',
        type=int,
        default=20,
        help='Número de vecinos para KNN'
    )
    
    parser.add_argument(
        '--eval-users',
        type=int,
        default=100,
        help='Número de usuarios para evaluación híbrida'
    )
    
    parser.add_argument(
        '--config',
        type=str,
        help='Archivo YAML de configuración (opcional)'
    )
    
    return parser.parse_args()


def load_config_from_file(config_path: str) -> Dict[str, Any]:
    """Carga configuración desde archivo YAML."""
    try:
        import yaml
        with open(config_path, 'r') as f:
            return yaml.safe_load(f)
    except ImportError:
        logger.error("PyYAML no está instalado. Usa: pip install pyyaml")
        return {}
    except FileNotFoundError:
        logger.error(f"Archivo de configuración no encontrado: {config_path}")
        return {}


def main():
    """Función principal del pipeline."""
    print("🎬 LatentLens Training Pipeline")
    print("=" * 50)
    
    # Parsear argumentos
    args = parse_arguments()
    
    # Crear configuración
    config = {
        'sample_size': args.sample_size,
        'n_factors': args.n_factors,
        'n_epochs': args.n_epochs,
        'test_size': args.test_size,
        'k_neighbors': args.k_neighbors,
        'eval_users': args.eval_users,
        'learning_rate': 0.005,
        'regularization': 0.02,
        'similarity_metric': 'cosine'
    }
    
    # Cargar configuración desde archivo si se proporciona
    if args.config:
        file_config = load_config_from_file(args.config)
        config.update(file_config)
    
    try:
        # Inicializar y ejecutar pipeline
        pipeline = TrainingPipeline(config)
        run_id = pipeline.run_mlflow_experiment(args.experiment_name)
        
        print("\n🎉 ENTRENAMIENTO COMPLETADO")
        print("=" * 50)
        print(f"📊 Experimento: {args.experiment_name}")
        print(f"🔬 MLflow Run ID: {run_id}")
        print(f"💾 Artefactos guardados en: artifacts/")
        print(f"📈 Ver resultados: mlflow ui")
        print("\n✅ Pipeline ejecutado exitosamente")
        
    except Exception as e:
        logger.error(f"❌ Error en el pipeline: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    main()
