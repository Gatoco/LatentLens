
# 🎬 LatentLens: Hybrid Movie Recommendation System

<p align="center">
  <img src="https://img.shields.io/badge/Status-Work%20In%20Progress-orange" alt="Status">
  <img src="https://img.shields.io/badge/Python-3.10-blue?logo=python" alt="Python">
  <img src="https://img.shields.io/badge/scikit--learn-%23F7931E.svg?logo=scikit-learn&logoColor=white" alt="Scikit-learn">
  <img src="https://img.shields.io/badge/pandas-%23150458.svg?logo=pandas&logoColor=white" alt="Pandas">
  <img src="https://img.shields.io/badge/FastAPI-0.116.1-green?logo=fastapi" alt="FastAPI">
  <img src="https://img.shields.io/badge/MLflow-3.2.0-blueviolet?logo=mlflow" alt="MLflow">
  <img src="https://img.shields.io/badge/Surprise-1.1.4-yellow?logo=python" alt="Surprise">
---

## 🧩 Main Frameworks & Dependencies

- Python 3.10
- [FastAPI](https://fastapi.tiangolo.com/) (0.116.1)
- [scikit-learn](https://scikit-learn.org/) (1.3.2)
- [pandas](https://pandas.pydata.org/) (2.3.1)
- [scikit-surprise](https://surpriselib.com/) (1.1.4)
- [MLflow](https://mlflow.org/) (3.2.0)
- [Uvicorn](https://www.uvicorn.org/) (0.35.0)
- [Jupyter](https://jupyter.org/) (for notebooks)

</p>

> **LatentLens** is a modern, scalable movie recommendation system that blends advanced data analysis and machine learning to deliver smart, personalized suggestions. Built for extensibility and production, LatentLens bridges the gap between simple popularity-based recommenders and sophisticated collaborative filtering models.

---

## 📚 Table of Contents

- [Overview](#overview)
- [Features](#features)
- [Dataset](#dataset)
- [Methodology](#methodology)
- [Demo](#demo)
- [Project Structure](#project-structure)
- [Roadmap](#roadmap)
- [Contributing](#contributing)
- [License](#license)

---

## 📝 Overview

With thousands of movies available, users often struggle to find content that matches their tastes. LatentLens analyzes both user behavior and movie features to provide relevant, engaging recommendations—helping users discover films they’ll love.

---

## 🚀 Features

- End-to-end recommendation pipeline
- Baseline and collaborative filtering models (KNN, SVD)
- Scalable data processing for large datasets (25M+ ratings)
- Modular, extensible Python codebase
- Ready for API deployment and experiment tracking (MLflow)
- Jupyter notebooks for EDA and prototyping

---

## 📊 Dataset

LatentLens leverages the [MovieLens 25M](https://grouplens.org/datasets/movielens/25m/) dataset:

- **25 million ratings**
- **162,000+ users**
- **62,000+ movies**

**Key Insights:**
- High data sparsity (many movies with few ratings)
- Distinct rating patterns among "power users"
- Genre and popularity analysis included

---

## 🛠️ Methodology

### Baseline: Weighted Popularity

Recommends top-rated movies, filtered by a minimum vote threshold to avoid bias toward niche titles.

### Collaborative Filtering

- **User-Item Matrix:** Sparse matrix of user ratings
- **Memory Optimization:** Focus on most active users and popular movies
- **Algorithms:**
  - KNN (cosine similarity, brute-force)
  - SVD (matrix factorization, Surprise library)
- **Experiment Tracking:** MLflow for reproducibility and comparison

---

## ✨ Demo

**Sample Recommendations**

> If you liked _The Godfather (1972)_:
> - The Godfather: Part II (1974)
> - Pulp Fiction (1994)
> - Goodfellas (1990)
> - The Silence of the Lambs (1991)
> - The Shawshank Redemption (1994)

> If you liked _Goodfellas (1990)_:
> - The Godfather (1972)
> - Pulp Fiction (1994)
> - The Godfather: Part II (1974)
> - Reservoir Dogs (1992)
> - Fargo (1996)

---

## 📁 Project Structure

```text
/data         # MovieLens dataset (not included in repo)
/notebooks    # Jupyter Notebooks for EDA and prototyping
/src          # Modular Python source code
setup.py      # Project installer
requirements.txt # Dependencies
```

---

## 🗺️ Roadmap

- [x] Baseline model implementation
- [x] Collaborative Filtering (KNN, SVD)
- [x] Model evaluation (RMSE)
- [ ] REST API (FastAPI)
- [x] MLflow integration
- [ ] Dockerization

---

## 🤝 Contributing

Contributions are welcome! Please open an issue or submit a pull request to get started.

---

## 📄 License

This project is licensed under the MIT License.
