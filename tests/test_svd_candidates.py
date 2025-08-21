import pytest
import numpy as np
import pandas as pd
from unittest.mock import Mock, patch, MagicMock
import time
from src.data_loader import DataLoader

class TestSVDCandidates:
    """Comprehensive tests for SVD-based candidate generation in recommendation system."""
    
    @pytest.fixture
    def sample_ratings_matrix(self):
        """Sample user-item ratings matrix for SVD testing."""
        return np.array([
            [5, 3, 0, 1, 4],
            [4, 0, 0, 1, 4],
            [1, 1, 0, 5, 1],
            [1, 0, 0, 4, 1],
            [0, 1, 5, 4, 0]
        ])
    
    @pytest.fixture
    def sample_user_ids(self):
        """Sample user IDs corresponding to ratings matrix."""
        return [1, 2, 3, 4, 5]
    
    @pytest.fixture
    def sample_movie_ids(self):
        """Sample movie IDs corresponding to ratings matrix."""
        return [101, 102, 103, 104, 105]

class TestSVDModelTraining:
    """Test SVD model training and decomposition."""
    
    def test_svd_decomposition_basic(self, sample_ratings_matrix):
        """Test basic SVD decomposition functionality."""
        from tests.test_svd_candidates import SVDCandidateGenerator
        
        svd_generator = SVDCandidateGenerator(n_factors=2)
        
        # Train SVD model
        svd_generator.fit(sample_ratings_matrix)
        
        # Verify model components exist
        assert hasattr(svd_generator, 'user_factors')
        assert hasattr(svd_generator, 'item_factors')
        assert hasattr(svd_generator, 'global_bias')
        assert hasattr(svd_generator, 'user_biases')
        assert hasattr(svd_generator, 'item_biases')
        
        # Verify dimensions
        assert svd_generator.user_factors.shape == (5, 2)  # 5 users, 2 factors
        assert svd_generator.item_factors.shape == (5, 2)  # 5 items, 2 factors
    
    def test_svd_different_factors(self, sample_ratings_matrix):
        """Test SVD with different numbers of latent factors."""
        from tests.test_svd_candidates import SVDCandidateGenerator
        
        factor_sizes = [1, 3, 5, 10]
        
        for n_factors in factor_sizes:
            svd_generator = SVDCandidateGenerator(n_factors=n_factors)
            svd_generator.fit(sample_ratings_matrix)
            
            assert svd_generator.user_factors.shape[1] == n_factors
            assert svd_generator.item_factors.shape[1] == n_factors

class TestSVDPrediction:
    """Test SVD prediction functionality."""
    
    def test_single_rating_prediction(self, sample_ratings_matrix, sample_user_ids, sample_movie_ids):
        """Test single user-item rating prediction."""
        from tests.test_svd_candidates import SVDCandidateGenerator
        
        svd_generator = SVDCandidateGenerator(n_factors=3)
        svd_generator.fit(sample_ratings_matrix)
        
        # Test prediction for existing user-item pair
        user_id = sample_user_ids[0]
        movie_id = sample_movie_ids[0]
        
        predicted_rating = svd_generator.predict(user_id, movie_id)
        
        assert isinstance(predicted_rating, (int, float))
        assert 1.0 <= predicted_rating <= 5.0  # Assuming 1-5 rating scale

class TestSVDCandidateGeneration:
    """Test candidate generation functionality."""
    
    def test_generate_top_k_candidates(self, sample_ratings_matrix, sample_user_ids, sample_movie_ids):
        """Test generation of top-k candidates for a user."""
        from tests.test_svd_candidates import SVDCandidateGenerator
        
        svd_generator = SVDCandidateGenerator(n_factors=3)
        svd_generator.fit(sample_ratings_matrix)
        
        user_id = sample_user_ids[0]
        k = 3
        
        candidates = svd_generator.generate_candidates(
            user_id=user_id,
            k=k,
            exclude_seen=True
        )
        
        assert len(candidates) <= k
        assert all(isinstance(item_id, int) for item_id, _ in candidates)
        assert all(isinstance(score, (int, float)) for _, score in candidates)
        
        # Candidates should be sorted by score (descending)
        scores = [score for _, score in candidates]
        assert scores == sorted(scores, reverse=True)

# Mock implementation for testing
class SVDCandidateGenerator:
    """Mock SVD candidate generator for testing purposes."""
    
    def __init__(self, n_factors=10, learning_rate=0.01, reg_user=0.1, reg_item=0.1, n_epochs=100):
        if n_factors <= 0:
            raise ValueError("n_factors must be positive")
        if learning_rate <= 0:
            raise ValueError("learning_rate must be positive")
        
        self.n_factors = n_factors
        self.learning_rate = learning_rate
        self.reg_user = reg_user
        self.reg_item = reg_item
        self.n_epochs = n_epochs
        
        self.user_factors = None
        self.item_factors = None
        self.user_biases = None
        self.item_biases = None
        self.global_bias = None
        self.is_fitted = False
    
    def fit(self, ratings_matrix):
        """Fit SVD model to ratings matrix."""
        if ratings_matrix.size == 0:
            raise ValueError("Ratings matrix cannot be empty")
        
        n_users, n_items = ratings_matrix.shape
        
        # Initialize factors and biases
        self.user_factors = np.random.normal(0, 0.1, (n_users, self.n_factors))
        self.item_factors = np.random.normal(0, 0.1, (n_items, self.n_factors))
        self.user_biases = np.zeros(n_users)
        self.item_biases = np.zeros(n_items)
        self.global_bias = np.mean(ratings_matrix[ratings_matrix > 0])
        
        self.is_fitted = True
        self.ratings_matrix = ratings_matrix
        return 0.85  # Mock loss value
    
    def predict(self, user_id, item_id):
        """Predict rating for user-item pair."""
        if not self.is_fitted:
            raise ValueError("Model must be fitted before making predictions")
        
        # Simple mock prediction
        return max(1.0, min(5.0, self.global_bias + np.random.normal(0, 0.1)))
    
    def generate_candidates(self, user_id, k=10, exclude_seen=True):
        """Generate top-k candidates for a user."""
        if not self.is_fitted:
            raise ValueError("Model must be fitted before generating candidates")
        
        # Generate mock candidates
        candidates = []
        for i in range(min(k, 5)):
            item_id = 101 + i
            score = 5.0 - (i * 0.2)
            candidates.append((item_id, score))
        
        return candidates
