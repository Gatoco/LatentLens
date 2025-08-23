import pytest
import numpy as np
import pandas as pd
from unittest.mock import Mock, patch, MagicMock
from data_loader import DataLoader

class TestKNNCandidates:
    """Comprehensive tests for KNN-based candidate generation."""
    
    @pytest.fixture
    def sample_user_item_matrix(self):
        """Sample user-item interaction matrix."""
        return np.array([
            [5, 3, 0, 1, 4, 0],
            [4, 0, 0, 1, 4, 2],
            [1, 1, 0, 5, 1, 3],
            [1, 0, 0, 4, 1, 5],
            [0, 1, 5, 4, 0, 4],
            [2, 3, 4, 0, 2, 1]
        ])
    
    def test_user_based_knn_similarity(self, sample_user_item_matrix):
        """Test user-based KNN similarity calculation."""
        from tests.test_knn_candidates import KNNCandidateGenerator
        
        knn_generator = KNNCandidateGenerator(
            algorithm='user_based',
            similarity_metric='cosine',
            k_neighbors=3
        )
        
        similarity_matrix = knn_generator.compute_user_similarity(sample_user_item_matrix)
        
        assert similarity_matrix.shape == (6, 6)
        assert np.allclose(np.diag(similarity_matrix), 1.0)  # Self-similarity should be 1
        assert np.allclose(similarity_matrix, similarity_matrix.T)  # Should be symmetric

class KNNCandidateGenerator:
    """Mock KNN implementation for testing."""
    
    def __init__(self, algorithm='user_based', similarity_metric='cosine', k_neighbors=5):
        self.algorithm = algorithm
        self.similarity_metric = similarity_metric
        self.k_neighbors = k_neighbors
        self.is_fitted = False
    
    def compute_user_similarity(self, user_item_matrix):
        """Compute user similarity matrix."""
        n_users = user_item_matrix.shape[0]
        similarity_matrix = np.eye(n_users)
        
        for i in range(n_users):
            for j in range(i+1, n_users):
                if self.similarity_metric == 'cosine':
                    # Simple cosine similarity
                    dot_product = np.dot(user_item_matrix[i], user_item_matrix[j])
                    norm_i = np.linalg.norm(user_item_matrix[i])
                    norm_j = np.linalg.norm(user_item_matrix[j])
                    
                    if norm_i > 0 and norm_j > 0:
                        similarity = dot_product / (norm_i * norm_j)
                    else:
                        similarity = 0.0
                    
                    similarity_matrix[i, j] = similarity
                    similarity_matrix[j, i] = similarity
        
        return similarity_matrix
