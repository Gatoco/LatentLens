# LatentLens: Un Sistema Híbrido de Recomendación de Películas

![Status](https://img.shields.io/badge/Status-Work%20In%20Progress-orange)
![Python](https://img.shields.io/badge/Python-3.11+-blue?logo=python)
![Scikit-learn](https://img.shields.io/badge/scikit--learn-%23F7931E.svg?logo=scikit-learn&logoColor=white)
![Pandas](https://img.shields.io/badge/pandas-%23150458.svg?logo=pandas&logoColor=white)

Este proyecto es un sistema de recomendación de películas de punta a punta, diseñado para ir más allá de los algoritmos básicos y construir una solución robusta y desplegable.

---

### Índice
1. [El Problema](#-el-problema-la-paradoja-de-la-elección)
2. [El Dataset](#-el-dataset-movielens-25m)
3. [Metodología Implementada](#-metodología-implementada)
4. [✨ Demo: Resultados Preliminares](#-demo-resultados-preliminares)
5. [Estructura del Proyecto](#-estructura-del-proyecto)
6. [Roadmap y Próximos Pasos](#-roadmap-y-próximos-pasos)

---

## 🎯 El Problema: La Paradoja de la Elección

En la era del streaming, nos enfrentamos a catálogos con decenas de miles de películas. Esta abundancia, en lugar de ser una ventaja, a menudo conduce a la "parálisis por análisis". El objetivo de `LatentLens` es analizar el comportamiento del usuario y las características de las películas para ofrecer recomendaciones personalizadas y relevantes que se sientan como si vinieran de un amigo experto en cine.

## 📊 El Dataset: MovieLens 25M

Utilizamos el prestigioso dataset **MovieLens 25M**, que contiene **25 millones de calificaciones** de más de 162,000 usuarios sobre 62,000 películas. Un Análisis Exploratorio de Datos (EDA) inicial fue crucial para guiar el diseño del modelo, revelando una alta escasez de datos (42% de las películas con menos de 5 votos) y el comportamiento distinto de los "power users".

## 🛠️ Metodología Implementada

Hasta ahora, se han implementado y comparado dos modelos principales:

### Modelo Baseline: Popularidad Ponderada
Este primer modelo simple sirve como un punto de referencia. No es personalizado. Recomienda las películas mejor calificadas del catálogo, pero solo considera aquellas que han superado un umbral mínimo de votos. Esto evita la "trampa de la película de culto" (películas con una calificación perfecta pero muy pocos votos) y asegura que las recomendaciones sean populares y de alta calidad general.

### Modelo Principal: Filtrado Colaborativo (K-Nearest Neighbors)
Este es nuestro primer modelo de Machine Learning. Funciona bajo el principio de "los usuarios a los que les gustaron las mismas cosas que a ti, probablemente compartirán otros gustos contigo".
1.  **Matriz Usuario-Película:** Se construye una matriz donde las filas son películas y las columnas son usuarios.
2.  **Manejo de Memoria:** Debido al `MemoryError` inicial al intentar crear una matriz de 71GB, el dataset fue filtrado estratégicamente para prototipar con los 40,000 usuarios más activos y las 20,000 películas más populares. Esto redujo el problema a un tamaño manejable sin perder la densidad de la información.
3.  **Algoritmo:** Se utiliza `NearestNeighbors` de `scikit-learn` con la similitud del coseno para encontrar las películas que se encuentran "más cerca" unas de otras en el "mapa de gustos" de los usuarios.

## ✨ Demo: Resultados Preliminares
Los resultados del modelo de Filtrado Colaborativo (KNN) demuestran una comprensión profunda de las conexiones cinematográficas, recomendando no solo por género, sino por "prestigio", director y estilo.

**Recomendaciones si te gustó 'The Godfather (1972)':**
```text
- Godfather: Part II, The (1974)
- Pulp Fiction (1994)
- Goodfellas (1990)
- Silence of the Lambs, The (1991)
- Shawshank Redemption, The (1994)```

**Recomendaciones si te gustó 'Goodfellas (1990)':**
```text
- Godfather, The (1972)
- Pulp Fiction (1994)
- Godfather: Part II, The (1974)
- Reservoir Dogs (1992)
- Fargo (1996)
```

## 📁 Estructura del Proyecto
El proyecto sigue una estructura profesional para asegurar la modularidad y la reproducibilidad:
- ``/data``: Contiene el dataset (ignorado por Git).
- ``/notebooks``: Almacena los Jupyter Notebooks para la exploración y el prototipado.
- ``/src``: Contiene el código fuente modularizado de Python (ej: `data_loader.py`).
- `setup.py`: Hace que el proyecto sea instalable y que los módulos en `/src` sean accesibles.

## 🚀 Roadmap y Próximos Pasos
- [x] Implementar un modelo Baseline.
- [x] Implementar un modelo de Filtrado Colaborativo (KNN).
- [ ] **Métrica:** Calcular el RMSE del modelo para evaluar su precisión de forma cuantitativa.
- [ ] **API:** Exponer el modelo entrenado a través de una API REST con FastAPI.
- [ ] **MLflow:** Integrar MLflow para registrar experimentos y artefactos del modelo.
- [ ] **Docker:** Dockerizar la aplicación completa para un despliegue sencillo.