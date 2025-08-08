# LatentLens: Hybrid Movie Recommendation System

![Status](https://img.shields.io/badge/Status-Work%20In%20Progress-orange)
![Python](https://img.shields.io/badge/Python-3.11+-blue?logo=python)
![Scikit-learn](https://img.shields.io/badge/scikit--learn-%23F7931E.svg?logo=scikit-learn&logoColor=white)
![Pandas](https://img.shields.io/badge/pandas-%23150458.svg?logo=pandas&logoColor=white)

LatentLens is a scalable, modular hybrid movie recommendation system that combines advanced data analysis with machine learning to deliver personalized film suggestions. Designed for extensibility and production-readiness, LatentLens bridges the gap between simple popularity-based recommenders and sophisticated collaborative filtering models.

---

## Table of Contents

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

## Overview

With the overwhelming number of movies available on streaming platforms, users struggle to discover content that matches their tastes. LatentLens analyzes both user behavior and movie features to provide relevant, engaging recommendations—helping users find films they’ll love.

---

## Features

- End-to-end recommendation pipeline
- Baseline and collaborative filtering models (KNN, SVD)
- Scalable data processing for large datasets (25M+ ratings)
- Modular, extensible Python codebase
- Ready for API deployment and experiment tracking (MLflow)
- Jupyter notebooks for EDA and prototyping

---

## Dataset

LatentLens utilizes the [MovieLens 25M](https://grouplens.org/datasets/movielens/25m/) dataset:

- 25 million ratings
- 162,000+ users
- 62,000+ movies

**Key Insights:**
- High data sparsity (many movies with few ratings)
- Distinct rating patterns among "power users"
- Genre and popularity analysis included

---

## Methodology

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

## Demo

**Sample Recommendations**

If you liked _The Godfather (1972)_:
```
- The Godfather: Part II (1974)
- Pulp Fiction (1994)
- Goodfellas (1990)
- The Silence of the Lambs (1991)
- The Shawshank Redemption (1994)
```

If you liked _Goodfellas (1990)_:
```
- The Godfather (1972)
- Pulp Fiction (1994)
- The Godfather: Part II (1974)
- Reservoir Dogs (1992)
- Fargo (1996)
```

---

## Project Structure

```
/data         # MovieLens dataset (not included in repo)
/notebooks    # Jupyter Notebooks for EDA and prototyping
/src          # Modular Python source code
setup.py      # Project installer
requirements.txt # Dependencies
```

---

## Roadmap

- [x] Baseline model implementation
- [x] Collaborative Filtering (KNN, SVD)
- [x] Model evaluation (RMSE)
- [ ] REST API (FastAPI)
- [x] MLflow integration
- [ ] Dockerization

---

## Contributing

Contributions are welcome! Please open an issue or submit a pull request to get started.

---

## License

This project is licensed under the MIT License.
