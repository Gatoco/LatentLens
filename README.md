
# 🎬 LatentLens — Hybrid Movie Recommender

<p align="center">
  <img src="https://img.shields.io/badge/Status-Work%20In%20Progress-orange" alt="Status">
  <img src="https://img.shields.io/badge/Python-3.10-blue?logo=python" alt="Python">
  <img src="https://img.shields.io/badge/FastAPI-0.116.1-009688?logo=fastapi&logoColor=white" alt="FastAPI">
  <img src="https://img.shields.io/badge/MLflow-3.2.0-9457EB?logo=mlflow&logoColor=white" alt="MLflow">
  <img src="https://img.shields.io/badge/scikit--learn-1.3.2-F7931E?logo=scikit-learn&logoColor=white" alt="scikit-learn">
  <img src="https://img.shields.io/badge/pandas-2.3.1-150458?logo=pandas&logoColor=white" alt="pandas">
  <img src="https://img.shields.io/badge/Surprise-1.1.4-yellow?logo=python" alt="Surprise">
  <img src="https://img.shields.io/badge/License-MIT-black" alt="License">
</p>

> LatentLens blends popularity baselines with collaborative filtering (KNN, SVD) to deliver movie recommendations at scale. Built with a clean src-layout, MLflow tracking, and a FastAPI service layer.

---

## 🚦 Current Status & Context

- API: minimal FastAPI app exposed at `/health` for liveness checks; recommendation endpoints planned.
- Experiments: MLflow runs stored locally under `./mlruns/` (ignored by git).
- Docker: multi-stage build updated; builder includes `git` so pip can install git-based deps.
- Tests: green locally via `pytest` (src-layout fixed with `src/__init__.py`).
- Repo hygiene: history cleanup in progress to remove large MLflow artifacts previously committed before pushing to GitHub.

---

## ⚡ Quickstart (Local)

Requirements: Python 3.10, Git. On Windows PowerShell:

```powershell
python -m venv venv
./venv/Scripts/Activate.ps1
pip install -r requirements.txt
python -m pytest -q   # optional: run tests

# Run the API (dev)
python -m uvicorn src.main:app --reload --host 127.0.0.1 --port 8000
# Health check
# http://127.0.0.1:8000/health
```

---

## � Docker

Multi-stage image (builder builds wheels; runtime uses slim). Build and run:

```powershell
docker build -t latentlens:local .
docker run --rm -p 8000:8000 latentlens:local
```

Notes:
- `mlruns/` and large artifacts are ignored; mount volumes if you want to persist runs.
- The builder stage installs `git` to support git-based requirements during pip install.

---

## 🧩 Tech Stack

- Python 3.10 • FastAPI • Uvicorn
- scikit-learn • pandas • scikit-surprise (SVD, KNN)
- MLflow for experiment tracking
- Jupyter for exploration (see `notebooks/`)

---

## 📊 Dataset

Uses [MovieLens 25M](https://grouplens.org/datasets/movielens/25m/).

- Expected path (local): `./data/ml-25m/` with `ratings.csv`, `movies.csv`, etc.
- Data and artifacts are ignored by git to keep the repo lean.

Key characteristics: high sparsity, long-tail items, power users, genre overlap.

---

## 🛠️ Methods (Concise)

- Baseline: weighted popularity with minimum votes to reduce small-sample bias.
- Collaborative filtering:
  - User–item sparse matrix with activity/popularity filtering.
  - KNN (cosine, brute force) and SVD (Surprise) with RMSE evaluation.
- Tracking: MLflow metrics/params/artifacts for reproducibility.

---

## 📁 Project Structure

```text
data/            # MovieLens dataset (local only, gitignored)
notebooks/       # EDA and MLflow experiments
src/             # FastAPI app and utilities (src-layout)
  ├─ main.py     # API app with /health
  └─ ...
requirements.txt
setup.py
```

---

## 🗺️ Roadmap

- [x] Baseline model (popularity)
- [x] Collaborative filtering (KNN, SVD) + RMSE
- [x] MLflow local tracking
- [x] Docker multi-stage build (builder + slim)
- [ ] REST endpoints for recommendations
- [ ] CI and publishing (after history cleanup)
- [ ] Hyperparameter sweeps and model registry

---

## 🤝 Contributing

PRs are welcome. Please avoid committing data or MLflow artifacts. For experiments, keep runs under local `mlruns/`.

---

## 📄 License

MIT License.
