#!/usr/bin/env python3
"""
Test Environment Setup Script for LatentLens

This script sets up a complete testing environment for the LatentLens
recommendation system, including test data, mock services, and fixtures.

Author: LatentLens Team
License: MIT
"""

import os
import sys
import json
import shutil
import logging
import argparse
import subprocess
import tempfile
from pathlib import Path
from datetime import datetime

# Add src to path for imports
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "src"))

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


class TestEnvironmentSetup:
    """Setup and configure testing environment for LatentLens."""
    
    def __init__(self, project_root=None, test_data_size="small"):
        """
        Initialize test environment setup.
        
        Args:
            project_root (str): Root directory of the project
            test_data_size (str): Size of test data ('small', 'medium', 'large')
        """
        self.project_root = Path(project_root) if project_root else Path.cwd()
        self.test_data_size = test_data_size
        self.test_dir = self.project_root / "tests"
        self.data_dir = self.project_root / "data"
        self.test_data_dir = self.test_dir / "test_data"
        self.fixtures_dir = self.test_dir / "fixtures"
        
    def setup_test_directories(self):
        """Create necessary test directories."""
        logger.info("Setting up test directories...")
        
        directories = [
            self.test_dir,
            self.test_data_dir,
            self.fixtures_dir,
            self.test_dir / "unit",
            self.test_dir / "integration",
            self.test_dir / "performance",
            self.test_dir / "reports",
            self.test_dir / "mocks"
        ]
        
        for directory in directories:
            directory.mkdir(parents=True, exist_ok=True)
            logger.info(f"Created directory: {directory}")
            
            # Create __init__.py files for Python packages
            if directory.name in ["unit", "integration", "performance", "mocks"]:
                init_file = directory / "__init__.py"
                if not init_file.exists():
                    init_file.write_text("# Test package")
    
    def create_test_data(self):
        """Create test datasets for different scenarios."""
        logger.info(f"Creating {self.test_data_size} test dataset...")
        
        # Define data sizes
        data_sizes = {
            "small": {"users": 100, "movies": 500, "ratings": 5000},
            "medium": {"users": 1000, "movies": 2000, "ratings": 50000},
            "large": {"users": 5000, "movies": 10000, "ratings": 200000}
        }
        
        size_config = data_sizes.get(self.test_data_size, data_sizes["small"])
        
        # Generate mock ratings data
        import pandas as pd
        import numpy as np
        
        np.random.seed(42)  # For reproducible tests
        
        # Generate users
        users_data = []
        for user_id in range(1, size_config["users"] + 1):
            users_data.append({
                "userId": user_id,
                "age": np.random.randint(18, 65),
                "gender": np.random.choice(["M", "F"]),
                "occupation": np.random.choice([
                    "student", "engineer", "teacher", "doctor", "artist"
                ])
            })
        
        users_df = pd.DataFrame(users_data)
        users_df.to_csv(self.test_data_dir / "users.csv", index=False)
        
        # Generate movies
        genres = ["Action", "Comedy", "Drama", "Horror", "Romance", "Sci-Fi"]
        movies_data = []
        for movie_id in range(1, size_config["movies"] + 1):
            year = np.random.randint(1990, 2024)
            movie_genres = np.random.choice(genres, size=np.random.randint(1, 4), replace=False)
            movies_data.append({
                "movieId": movie_id,
                "title": f"Test Movie {movie_id} ({year})",
                "genres": "|".join(movie_genres),
                "year": year
            })
        
        movies_df = pd.DataFrame(movies_data)
        movies_df.to_csv(self.test_data_dir / "movies.csv", index=False)
        
        # Generate ratings
        ratings_data = []
        for _ in range(size_config["ratings"]):
            user_id = np.random.randint(1, size_config["users"] + 1)
            movie_id = np.random.randint(1, size_config["movies"] + 1)
            rating = np.random.choice([1, 2, 3, 4, 5], p=[0.1, 0.1, 0.2, 0.3, 0.3])
            timestamp = np.random.randint(1000000000, 1700000000)
            
            ratings_data.append({
                "userId": user_id,
                "movieId": movie_id,
                "rating": rating,
                "timestamp": timestamp
            })
        
        ratings_df = pd.DataFrame(ratings_data)
        # Remove duplicates (user-movie pairs)
        ratings_df = ratings_df.drop_duplicates(subset=["userId", "movieId"])
        ratings_df.to_csv(self.test_data_dir / "ratings.csv", index=False)
        
        logger.info(f"Created test data:")
        logger.info(f"  Users: {len(users_df)}")
        logger.info(f"  Movies: {len(movies_df)}")
        logger.info(f"  Ratings: {len(ratings_df)}")
    
    def create_test_fixtures(self):
        """Create test fixtures and mock data."""
        logger.info("Creating test fixtures...")
        
        # Sample user profiles
        user_profiles = {
            "test_user_123": {
                "user_id": 123,
                "age": 25,
                "gender": "M",
                "occupation": "engineer",
                "favorite_genres": ["Action", "Sci-Fi"],
                "avg_rating": 3.8,
                "rating_count": 45
            },
            "test_user_456": {
                "user_id": 456,
                "age": 32,
                "gender": "F",
                "occupation": "teacher",
                "favorite_genres": ["Drama", "Romance"],
                "avg_rating": 4.2,
                "rating_count": 67
            },
            "cold_start_user": {
                "user_id": 999999,
                "age": 28,
                "gender": "F",
                "occupation": "student",
                "favorite_genres": [],
                "avg_rating": 0.0,
                "rating_count": 0
            }
        }
        
        with open(self.fixtures_dir / "user_profiles.json", "w") as f:
            json.dump(user_profiles, f, indent=2)
        
        # Sample movie data
        movie_fixtures = {
            "popular_movies": [
                {
                    "movie_id": 1,
                    "title": "Toy Story (1995)",
                    "genres": ["Animation", "Children", "Comedy"],
                    "avg_rating": 3.9,
                    "rating_count": 215
                },
                {
                    "movie_id": 2,
                    "title": "Jumanji (1995)",
                    "genres": ["Adventure", "Children", "Fantasy"],
                    "avg_rating": 3.2,
                    "rating_count": 110
                }
            ],
            "test_recommendations": {
                "user_123": [
                    {"movie_id": 1, "predicted_rating": 4.5, "confidence": 0.8},
                    {"movie_id": 3, "predicted_rating": 4.2, "confidence": 0.7},
                    {"movie_id": 7, "predicted_rating": 4.0, "confidence": 0.6}
                ]
            }
        }
        
        with open(self.fixtures_dir / "movie_fixtures.json", "w") as f:
            json.dump(movie_fixtures, f, indent=2)
        
        # Test configuration
        test_config = {
            "algorithms": {
                "svd": {"n_factors": 50, "n_epochs": 20, "lr_all": 0.005},
                "knn": {"k": 40, "sim_options": {"name": "cosine", "user_based": False}}
            },
            "evaluation": {
                "test_size": 0.25,
                "cv_folds": 3,
                "metrics": ["rmse", "mae", "precision_at_k", "recall_at_k"]
            },
            "api": {
                "base_url": "http://localhost:8000",
                "timeout": 30
            }
        }
        
        with open(self.fixtures_dir / "test_config.json", "w") as f:
            json.dump(test_config, f, indent=2)
    
    def setup_pytest_config(self):
        """Setup pytest configuration files."""
        logger.info("Setting up pytest configuration...")
        
        # pytest.ini
        pytest_ini_content = """
[tool:pytest]
testpaths = tests
python_files = test_*.py
python_classes = Test*
python_functions = test_*
addopts = 
    --verbose
    --tb=short
    --strict-markers
    --disable-warnings
    --cov=src
    --cov-report=html
    --cov-report=term-missing
markers =
    unit: Unit tests
    integration: Integration tests
    performance: Performance tests
    slow: Slow running tests
    api: API tests
    mlflow: MLflow related tests
"""
        
        with open(self.project_root / "pytest.ini", "w") as f:
            f.write(pytest_ini_content)
        
        # conftest.py for shared fixtures
        conftest_content = """
"""Shared pytest fixtures for LatentLens tests."""

import pytest
import json
import pandas as pd
from pathlib import Path


@pytest.fixture(scope="session")
def test_data_dir():
    """Path to test data directory."""
    return Path(__file__).parent / "test_data"


@pytest.fixture(scope="session")
def fixtures_dir():
    """Path to fixtures directory."""
    return Path(__file__).parent / "fixtures"


@pytest.fixture
def user_profiles(fixtures_dir):
    """Load user profile fixtures."""
    with open(fixtures_dir / "user_profiles.json") as f:
        return json.load(f)


@pytest.fixture
def movie_fixtures(fixtures_dir):
    """Load movie fixtures."""
    with open(fixtures_dir / "movie_fixtures.json") as f:
        return json.load(f)


@pytest.fixture
def test_config(fixtures_dir):
    """Load test configuration."""
    with open(fixtures_dir / "test_config.json") as f:
        return json.load(f)


@pytest.fixture
def sample_ratings_df(test_data_dir):
    """Load sample ratings dataframe."""
    return pd.read_csv(test_data_dir / "ratings.csv")


@pytest.fixture
def sample_movies_df(test_data_dir):
    """Load sample movies dataframe."""
    return pd.read_csv(test_data_dir / "movies.csv")


@pytest.fixture
def sample_users_df(test_data_dir):
    """Load sample users dataframe."""
    return pd.read_csv(test_data_dir / "users.csv")


@pytest.fixture
def sample_user_id():
    """Sample user ID for testing."""
    return 123


@pytest.fixture
def cold_start_user_id():
    """Cold start user ID for testing."""
    return 999999
"""
        
        with open(self.test_dir / "conftest.py", "w") as f:
            f.write(conftest_content)
    
    def install_test_dependencies(self):
        """Install required testing dependencies."""
        logger.info("Installing test dependencies...")
        
        test_requirements = [
            "pytest>=7.0.0",
            "pytest-cov>=4.0.0",
            "pytest-mock>=3.10.0",
            "pytest-xdist>=3.0.0",  # For parallel testing
            "pytest-html>=3.0.0",  # For HTML reports
            "factory-boy>=3.2.0",  # For test data factories
            "faker>=18.0.0",  # For generating fake data
            "responses>=0.23.0",  # For mocking HTTP requests
        ]
        
        try:
            for requirement in test_requirements:
                logger.info(f"Installing {requirement}...")
                subprocess.run(
                    [sys.executable, "-m", "pip", "install", requirement],
                    check=True,
                    capture_output=True,
                    text=True
                )
            logger.info("Test dependencies installed successfully")
        except subprocess.CalledProcessError as e:
            logger.warning(f"Could not install some dependencies: {e}")
    
    def create_sample_tests(self):
        """Create sample test files to demonstrate structure."""
        logger.info("Creating sample test files...")
        
        # Sample unit test
        unit_test_content = """
"""Sample unit test for LatentLens."""

import pytest
import numpy as np
from unittest.mock import Mock, patch


class TestSampleFunctionality:
    """Sample unit tests."""
    
    def test_basic_functionality(self):
        """Test basic functionality."""
        assert True
    
    def test_with_fixtures(self, sample_user_id, user_profiles):
        """Test using fixtures."""
        assert sample_user_id == 123
        assert "test_user_123" in user_profiles
    
    @pytest.mark.parametrize("rating,expected", [
        (1, "poor"),
        (3, "average"),
        (5, "excellent")
    ])
    def test_rating_categories(self, rating, expected):
        """Test rating categorization."""
        # This is just a sample test
        categories = {1: "poor", 2: "poor", 3: "average", 4: "good", 5: "excellent"}
        assert categories[rating] == expected
"""
        
        with open(self.test_dir / "unit" / "test_sample.py", "w") as f:
            f.write(unit_test_content)
        
        # Sample integration test
        integration_test_content = """
"""Sample integration test for LatentLens."""

import pytest
import requests
from unittest.mock import patch


@pytest.mark.integration
class TestAPIIntegration:
    """Sample API integration tests."""
    
    def test_api_health_check(self, test_config):
        """Test API health endpoint."""
        # This would test actual API if running
        base_url = test_config["api"]["base_url"]
        # Mock response for demonstration
        with patch('requests.get') as mock_get:
            mock_get.return_value.status_code = 200
            mock_get.return_value.json.return_value = {"status": "ok"}
            
            response = requests.get(f"{base_url}/health")
            assert response.status_code == 200
"""
        
        with open(self.test_dir / "integration" / "test_api_integration.py", "w") as f:
            f.write(integration_test_content)
    
    def validate_setup(self):
        """Validate that the test environment is set up correctly."""
        logger.info("Validating test environment setup...")
        
        validation_results = {
            "directories_created": True,
            "test_data_available": False,
            "fixtures_created": False,
            "pytest_config": False,
            "dependencies_installed": False
        }
        
        # Check test data
        test_files = ["users.csv", "movies.csv", "ratings.csv"]
        validation_results["test_data_available"] = all(
            (self.test_data_dir / file).exists() for file in test_files
        )
        
        # Check fixtures
        fixture_files = ["user_profiles.json", "movie_fixtures.json", "test_config.json"]
        validation_results["fixtures_created"] = all(
            (self.fixtures_dir / file).exists() for file in fixture_files
        )
        
        # Check pytest config
        validation_results["pytest_config"] = (
            (self.project_root / "pytest.ini").exists() and
            (self.test_dir / "conftest.py").exists()
        )
        
        # Check if pytest is available
        try:
            import pytest
            validation_results["dependencies_installed"] = True
        except ImportError:
            validation_results["dependencies_installed"] = False
        
        # Report results
        for check, passed in validation_results.items():
            status = "✓" if passed else "✗"
            logger.info(f"  {status} {check.replace('_', ' ').title()}")
        
        all_passed = all(validation_results.values())
        
        if all_passed:
            logger.info("Test environment setup completed successfully!")
        else:
            logger.warning("Some setup checks failed. Please review the output above.")
        
        return validation_results
    
    def run_sample_tests(self):
        """Run sample tests to verify setup."""
        logger.info("Running sample tests...")
        
        try:
            # Run pytest on sample tests
            result = subprocess.run(
                [sys.executable, "-m", "pytest", str(self.test_dir / "unit" / "test_sample.py"), "-v"],
                cwd=self.project_root,
                capture_output=True,
                text=True
            )
            
            if result.returncode == 0:
                logger.info("Sample tests passed successfully!")
                logger.info(result.stdout)
            else:
                logger.warning("Sample tests failed:")
                logger.warning(result.stderr)
                
        except Exception as e:
            logger.warning(f"Could not run sample tests: {e}")


def main():
    """Main setup function."""
    parser = argparse.ArgumentParser(
        description="Setup test environment for LatentLens"
    )
    parser.add_argument(
        "--project-root",
        type=str,
        help="Root directory of the project (default: current directory)"
    )
    parser.add_argument(
        "--data-size",
        choices=["small", "medium", "large"],
        default="small",
        help="Size of test data to generate"
    )
    parser.add_argument(
        "--skip-deps",
        action="store_true",
        help="Skip installing test dependencies"
    )
    parser.add_argument(
        "--run-tests",
        action="store_true",
        help="Run sample tests after setup"
    )
    
    args = parser.parse_args()
    
    try:
        # Initialize setup
        setup = TestEnvironmentSetup(
            project_root=args.project_root,
            test_data_size=args.data_size
        )
        
        # Run setup steps
        setup.setup_test_directories()
        setup.create_test_data()
        setup.create_test_fixtures()
        setup.setup_pytest_config()
        setup.create_sample_tests()
        
        if not args.skip_deps:
            setup.install_test_dependencies()
        
        # Validate setup
        validation_results = setup.validate_setup()
        
        if args.run_tests:
            setup.run_sample_tests()
        
        if all(validation_results.values()):
            logger.info("Test environment setup completed successfully!")
            print("\nNext steps:")
            print("1. Run tests with: pytest")
            print("2. Run tests with coverage: pytest --cov=src")
            print("3. Generate HTML coverage report: pytest --cov=src --cov-report=html")
        else:
            logger.warning("Setup completed with some issues. Check the logs above.")
            
    except Exception as e:
        logger.error(f"Setup failed: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
