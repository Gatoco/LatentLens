# LatentLens: A Hybrid Movie Recommendation System

![Status](https://img.shields.io/badge/Status-Work%20In%20Progress-orange)
![Python](https://img.shields.io/badge/Python-3.11+-blue?logo=python)
![Scikit-learn](https://img.shields.io/badge/scikit--learn-%23F7931E.svg?logo=scikit-learn&logoColor=white)
![Pandas](https://img.shields.io/badge/pandas-%23150458.svg?logo=pandas&logoColor=white)

This project is an end-to-end movie recommendation system, designed to go beyond basic algorithms and build a robust, deployable solution.

---

### Table of Contents
1. [The Problem: The Paradox of Choice](#-the-problem-the-paradox-of-choice)
2. [The Dataset: MovieLens 25M](#-the-dataset-movielens-25m)
3. [Implemented Methodology](#-implemented-methodology)
4. [✨ Demo: Preliminary Results](#-demo-preliminary-results)
5. [Project Structure](#-project-structure)
6. [Roadmap and Next Steps](#-roadmap-and-next-steps)

---

## 🎯 The Problem: The Paradox of Choice

In the age of streaming, we face catalogs with tens of thousands of movies. This abundance, rather than being an advantage, often leads to "analysis paralysis." The goal of `LatentLens` is to analyze user behavior and movie features to deliver personalized, relevant recommendations that feel like they're coming from a film-savvy friend.

## 📊 The Dataset: MovieLens 25M

We use the renowned **MovieLens 25M** dataset, which contains **25 million ratings** from over 162,000 users for 62,000 movies. An initial Exploratory Data Analysis (EDA) was crucial for guiding the model's design, revealing high data sparsity (42% of movies with fewer than 5 ratings) and the distinct behavior of "power users."

## 🛠️ Implemented Methodology

So far, two main models have been implemented and compared:

### Baseline Model: Weighted Popularity
This first, simple model serves as a baseline. It's not personalized. It recommends the highest-rated movies in the catalog, but only considers those that have surpassed a minimum threshold of votes. This avoids the "cult classic trap" (movies with a perfect rating but very few votes) and ensures the recommendations are both popular and of high overall quality.

### Main Model: Collaborative Filtering (K-Nearest Neighbors)
This is our first Machine Learning model. It operates on the principle: *"users who liked the same things you did will likely share other tastes with you."*
1.  **User-Item Matrix:** A matrix is built where rows represent movies and columns represent users.
2.  **Memory Management:** Due to the initial `MemoryError` when attempting to create a 71GB matrix, the dataset was strategically filtered to prototype with the 40,000 most active users and the 20,000 most popular movies. This reduced the problem to a manageable size without losing informational density.
3.  **Algorithm:** Scikit-learn's `NearestNeighbors` is used with cosine similarity to find the movies that are "closest" to each other on the user "taste map."

## ✨ Demo: Preliminary Results
The results from the Collaborative Filtering (KNN) model demonstrate a deep understanding of cinematic connections, recommending not just by genre, but by "prestige," director, and style.

**Recommendations if you liked 'The Godfather (1972)':**
```text
- Godfather: Part II, The (1974)
- Pulp Fiction (1994)
- Goodfellas (1990)
- Silence of the Lambs, The (1991)
- Shawshank Redemption, The (1994)
Use code with caution.
Markdown
Recommendations if you liked 'Goodfellas (1990)':
Generated text
- Godfather, The (1972)
- Pulp Fiction (1994)
- Godfather: Part II, The (1974)
- Reservoir Dogs (1992)
- Fargo (1996)
Use code with caution.
Text
📁 Project Structure
The project follows a professional structure to ensure modularity and reproducibility:
/data: Contains the dataset (ignored by Git).
/notebooks: Stores Jupyter Notebooks for exploration and prototyping.
/src: Contains the modularized Python source code (e.g., data_loader.py).
setup.py: Makes the project installable and allows the modules in /src to be imported across the project.
🚀 Roadmap and Next Steps
Implement a Baseline model.
Implement a Collaborative Filtering (KNN) model.
Metrics: Calculate the model's RMSE to quantitatively evaluate its accuracy.
API: Expose the trained model via a REST API with FastAPI.
MLflow: Integrate MLflow to log experiments and model artifacts.
Docker: Dockerize the entire application for simple, reproducible deployment.