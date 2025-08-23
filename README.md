# LatentLens - Hybrid Movie Recommendation System

![Python 3.10+](https://img.shields.io/badge/python-3.10+-blue.svg)
![FastAPI](https://img.shields.io/badge/FastAPI-0.116.1-teal.svg)
![MLflow](https://img.shields.io/badge/MLflow-3.2.0-green.svg)
![Jupyter](https://img.shields.io/badge/jupyter-notebook-orange.svg)
![Scikit-learn](https://img.shields.io/badge/scikit--learn-1.3.2-red.svg)
![Pandas](https://img.shields.io/badge/pandas-2.3.1-yellow.svg)
![Docker](https://img.shields.io/badge/docker-containerized-blue.svg)
![License](https://img.shields.io/badge/license-MIT-green.svg)

A professional-grade hybrid movie recommendation system that combines collaborative filtering and content-based approaches, featuring advanced ranking metrics and MLOps integration with MLflow.

## Overview

LatentLens is an advanced recommendation system designed to deliver personalized movie recommendations using sophisticated machine learning algorithms. The system combines multiple recommendation approaches to overcome individual algorithm limitations and provides comprehensive evaluation metrics for production deployment.

### Key Features

- **Hybrid Architecture**: Combines SVD, K-Nearest Neighbors, and Content-based filtering
- **Advanced Metrics**: Precision@K, Recall@K, NDCG, MAP, and MRR evaluation
- **Cold-Start Handling**: Robust strategies for new users and items
- **MLOps Integration**: Complete MLflow integration for experiment tracking and model management
- **Production Ready**: RESTful API with FastAPI and Docker containerization
- **Comprehensive Testing**: 75+ test coverage with automated validation

## System Architecture

The system follows a modular, microservices-inspired architecture:

```
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   FastAPI       │    │  Recommendation │    │    MLflow       │
│   REST API      │◄──►│    Engine       │◄──►│   Tracking      │
└─────────────────┘    └─────────────────┘    └─────────────────┘
         │                        │                        │
         ▼                        ▼                        ▼
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   Data Layer    │    │   Algorithm     │    │   Evaluation    │
│   MovieLens     │    │   Components    │    │   Framework     │
└─────────────────┘    └─────────────────┘    └─────────────────┘
```

### Algorithm Components

- **SVD (Singular Value Decomposition)**: Matrix factorization for collaborative filtering
- **KNN (K-Nearest Neighbors)**: User and item-based similarity recommendations
- **Content-Based**: TF-IDF genre and metadata analysis
- **Hybrid Weighting**: Intelligent combination of multiple algorithms

## Requirements

### System Requirements

- **Python**: 3.10 or higher
- **Memory**: Minimum 4GB RAM (8GB recommended)
- **Storage**: 2GB free space for dataset and models
- **Docker**: For containerized deployment

### Core Dependencies

```
fastapi==0.116.1
uvicorn==0.35.0
mlflow==3.2.0
scikit-surprise==1.1.4
scikit-learn==1.3.2
scipy==1.11.4
pandas==2.3.1
numpy==1.26.4
```

## Quick Start

### 1. Clone and Setup

```bash
git clone https://github.com/Gatoco/LatentLens.git
cd LatentLens
make setup
```

### 2. Activate Environment

**Windows:**
```powershell
.\venv\Scripts\Activate.ps1
```

**Unix/Linux/macOS:**
```bash
source venv/bin/activate
```

### 3. Run Locally

```bash
make run-local
```

### 4. Access API

Open your browser to `http://localhost:8000/docs` for interactive API documentation.

## Docker Deployment

### Build and Run

```bash
# Build Docker image
make build

# Run container
make run-docker
```

### Docker Compose

```bash
docker-compose up -d
```

## Usage Examples

### Basic Recommendation Request

```python
import requests

# Get recommendations for user ID 123
response = requests.get("http://localhost:8000/recommend/123")
recommendations = response.json()

print(f"Top recommendations: {recommendations[:5]}")
```

### Cold-Start Recommendations

```python
# Recommendations for new users
response = requests.get(
    "http://localhost:8000/recommend/cold-start/999",
    params={"strategy": "popular", "limit": 10}
)
```

### Movie Similarity

```python
# Find similar movies
response = requests.get("http://localhost:8000/movies/1/similar")
similar_movies = response.json()
```

## API Reference

### Core Endpoints

| Endpoint | Method | Description |
|----------|--------|--------------| 
| `/recommend/{user_id}` | GET | Get personalized recommendations |
| `/recommend/cold-start/{user_id}` | GET | Cold-start recommendations |
| `/movies/{movie_id}/similar` | GET | Find similar movies |
| `/movies/popular` | GET | Get popular movies |
| `/health` | GET | Health check |
| `/system/status` | GET | System status and metrics |

### Request Parameters

- `limit`: Number of recommendations (default: 10)
- `genre_filter`: Filter by specific genres
- `min_rating`: Minimum rating threshold
- `strategy`: Cold-start strategy (popular, trending, diverse)

## Model Training and Evaluation

### Training Models

```bash
# Train all models
python src/train.py

# Train specific algorithm
python src/train.py --algorithm svd
```

### Running Evaluations

```bash
# Comprehensive evaluation
python scripts/evaluation/evaluate_hybrid_model.py

# Quick evaluation
python scripts/evaluation/quick_hybrid_evaluation.py

# MLflow integrated evaluation
python scripts/evaluation/mlflow_hybrid_evaluation.py
```

### Validation Scripts

```bash
# Cold-start validation
python scripts/validation/validate_cold_start.py

# Production deployment validation
python scripts/validation/validate_production_deployment.py

# Success criteria validation
python scripts/validation/validate_success_criteria.py
```

## MLflow Integration

### Starting MLflow UI

```bash
mlflow ui
```

Access the MLflow interface at `http://localhost:5000`

### Experiment Tracking

The system automatically logs:
- Model parameters and hyperparameters
- Training and validation metrics
- Model artifacts and serialized objects
- Evaluation results and performance metrics

## Testing

### Run Test Suite

```bash
# Run all tests
make test

# Run with coverage
pytest --cov=src --cov-report=html

# Run specific test categories
pytest -m unit
pytest -m integration
```

### Test Categories

- **Unit Tests**: Individual component testing
- **Integration Tests**: End-to-end workflow testing
- **API Tests**: REST endpoint validation
- **Performance Tests**: Load and response time testing

## Performance Metrics

### Accuracy Metrics

- **MAE (Mean Absolute Error)**: Average prediction error
- **RMSE (Root Mean Square Error)**: Prediction accuracy measure
- **Precision@K**: Relevant recommendations in top K
- **Recall@K**: Coverage of user's relevant items
- **NDCG@K**: Normalized Discounted Cumulative Gain
- **MAP (Mean Average Precision)**: Average precision across users

### System Metrics

- **Response Time**: Average API response latency
- **Throughput**: Requests per second capacity
- **Coverage**: Catalog coverage percentage
- **Diversity**: Recommendation variety metrics
- **Novelty**: Serendipity and discovery metrics

## Project Structure

```
LatentLens/
├── src/                          # Core source code
│   ├── main.py                   # FastAPI application
│   ├── recommendation_service.py # Main recommendation logic
│   ├── hybrid_recommendation_service.py # Hybrid algorithms
│   ├── item_similarity_service.py # Item-to-item similarity
│   └── evaluation.py             # Evaluation framework
├── tests/                        # Test suite
│   ├── test_hybrid_simple.py     # Basic hybrid tests
│   ├── test_recommendation_service.py # Service tests
│   └── test_candidate_weighting.py # Algorithm tests
├── scripts/                      # Automation scripts
│   ├── evaluation/               # Model evaluation scripts
│   ├── validation/               # Production validation
│   └── mlflow/                   # MLflow utilities
├── notebooks/                    # Jupyter analysis notebooks
│   ├── 01-EDA.ipynb             # Exploratory data analysis
│   ├── 02-Baseline-Model.ipynb  # Baseline implementations
│   └── 03-Collaborative-Filtering.ipynb # CF analysis
├── reports/                      # Technical documentation
│   ├── FINAL_PROJECT_STATUS.md  # Project overview
│   ├── TEST_COVERAGE_REPORT.md  # Testing documentation
│   └── evaluation/               # Evaluation reports
├── examples/                     # Usage examples
├── Dockerfile                    # Container configuration
├── docker-compose.yml           # Multi-service deployment
├── Makefile                      # Build automation
└── requirements.txt              # Python dependencies
```

## Configuration

### Environment Variables

```bash
# MLflow configuration
export MLFLOW_TRACKING_URI=http://localhost:5000
export MLFLOW_EXPERIMENT_NAME=LatentLens

# API configuration
export API_HOST=0.0.0.0
export API_PORT=8000

# Model configuration
export MODEL_PATH=./models
export DATA_PATH=./data
```

### Config File (config.yaml)

```yaml
model:
  svd:
    n_factors: 100
    n_epochs: 20
    lr_all: 0.005
  knn:
    k: 40
    sim_options:
      name: cosine
      user_based: false
  
api:
  host: 0.0.0.0
  port: 8000
  debug: false

evaluation:
  test_size: 0.25
  cv_folds: 5
  metrics: ["rmse", "mae", "precision_at_k", "recall_at_k"]
```

## Makefile Commands

| Command | Description |
|---------|-------------|
| `make setup` | Install dependencies and setup environment |
| `make build` | Build Docker image |
| `make run-local` | Run development server locally |
| `make run-docker` | Run application in Docker container |
| `make test` | Execute test suite |
| `make clean` | Clean temporary files and caches |
| `make push` | Push Docker image to registry |

## Monitoring and Logging

### Health Checks

```bash
# Basic health check
curl http://localhost:8000/health

# System status
curl http://localhost:8000/system/status
```

### Log Levels

- **DEBUG**: Detailed debugging information
- **INFO**: General system information
- **WARNING**: Warning messages
- **ERROR**: Error conditions
- **CRITICAL**: Critical system failures

## Production Deployment

### Deployment Checklist

- [ ] Environment variables configured
- [ ] Database connections validated
- [ ] Model artifacts available
- [ ] Health checks passing
- [ ] Performance benchmarks met
- [ ] Security configurations applied
- [ ] Monitoring and alerting setup

### Scaling Considerations

- **Horizontal Scaling**: Multiple container instances
- **Load Balancing**: Distribute requests across instances
- **Caching**: Redis for frequent recommendations
- **Database**: Optimize for read-heavy workloads

## Technical Documentation

### Available Reports

- [Final Project Status](reports/FINAL_PROJECT_STATUS.md)
- [Test Coverage Report](reports/TEST_COVERAGE_REPORT.md)
- [Implementation Guide](reports/FINAL_TESTS_IMPLEMENTATION_REPORT.md)
- [Cleanup Summary](reports/PROJECT_CLEANUP_SUMMARY.md)
- [Item Similarity Documentation](reports/ITEM_SIMILARITY_SUMMARY.md)

### Architecture Documents

- System architecture and design patterns
- API specification and endpoint documentation
- Algorithm implementation details
- Performance optimization guidelines

## Troubleshooting

### Common Issues

**Issue**: Import errors with scikit-surprise
**Solution**: Ensure proper compilation environment or use Docker

**Issue**: MLflow tracking URI connection failed
**Solution**: Verify MLflow server is running and accessible

**Issue**: Out of memory during training
**Solution**: Reduce dataset size or increase system memory

**Issue**: API requests timeout
**Solution**: Check model loading and increase timeout values

### Debug Mode

```bash
# Enable debug logging
export LOG_LEVEL=DEBUG
python src/main.py
```

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## Technical Stack Summary

- **Backend Framework**: FastAPI with Uvicorn ASGI server
- **Machine Learning**: Scikit-learn, Scikit-surprise, Scipy
- **Data Processing**: Pandas, NumPy
- **MLOps**: MLflow for experiment tracking and model management
- **API Documentation**: Automatic OpenAPI/Swagger generation
- **Containerization**: Docker with multi-stage builds
- **Testing**: Pytest with comprehensive test coverage
- **Build Automation**: Makefile for development workflows
- **Configuration**: YAML-based configuration management
- **Development**: Jupyter notebooks for analysis and experimentation

---

**LatentLens** - Professional movie recommendation system for production environments.