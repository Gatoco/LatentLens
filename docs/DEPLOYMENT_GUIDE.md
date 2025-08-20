# 🚀 LatentLens Deployment Guide

## 📋 Quick Start

### Local Development
```bash
# Install dependencies
pip install -r requirements.txt

# Run FastAPI server
python main.py
```

### Docker Deployment
```bash
# Build and run with Docker Compose
docker-compose up --build
```

## 🔧 Configuration

- **API Server**: http://localhost:8000
- **MLflow UI**: http://localhost:5000
- **Data**: Place in `data/ml-25m/`

## 📊 Available Endpoints

- `GET /recommend/{user_id}` - Get recommendations
- `GET /health` - Health check
- `GET /metrics` - Performance metrics

## 🎯 Model Performance

- **Hybrid Model**: Best coverage (0.28%) + diversity
- **Cold Start**: Handles new users automatically
- **Real-time**: Sub-second response times

Generated: 2025-08-20
