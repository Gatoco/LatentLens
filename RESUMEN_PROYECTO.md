# 🎬 Resumen del Proyecto LatentLens

## 📋 Descripción General

**LatentLens** es un sistema híbrido de recomendación de películas que combina análisis de datos avanzado y aprendizaje automático para ofrecer sugerencias personalizadas e inteligentes. El proyecto está diseñado para ser escalable, modular y listo para producción, cerrando la brecha entre sistemas de recomendación simples basados en popularidad y modelos sofisticados de filtrado colaborativo.

## 🎯 Objetivo del Proyecto

Desarrollar un sistema de recomendación de películas que ayude a los usuarios a descubrir contenido que coincida con sus gustos, utilizando tanto el comportamiento del usuario como las características de las películas para proporcionar recomendaciones relevantes y atractivas.

## 🛠️ Stack Tecnológico

### Tecnologías Principales
- **Python 3.10** - Lenguaje de programación principal
- **FastAPI 0.116.1** - Framework para API REST
- **scikit-learn 1.3.2** - Algoritmos de machine learning
- **pandas 2.3.1** - Manipulación y análisis de datos
- **scikit-surprise 1.1.4** - Algoritmos de sistemas de recomendación
- **MLflow 3.2.0** - Seguimiento de experimentos y gestión de modelos
- **Uvicorn 0.35.0** - Servidor ASGI para FastAPI

### Herramientas de Desarrollo
- **Jupyter Notebooks** - Prototipado y análisis exploratorio
- **Docker** - Contenedorización y despliegue
- **Docker Compose** - Orquestación de servicios

## 📊 Dataset

El proyecto utiliza el dataset **MovieLens 25M**, que incluye:
- **25 millones de calificaciones**
- **162,000+ usuarios**
- **62,000+ películas**

### Características del Dataset
- Alta dispersión de datos (muchas películas con pocas calificaciones)
- Patrones de calificación distintos entre "usuarios activos"
- Análisis por género y popularidad incluido

## 🔬 Metodología y Algoritmos

### 1. Modelo Baseline: Popularidad Ponderada
- Recomienda películas mejor calificadas
- Filtrado por umbral mínimo de votos para evitar sesgo hacia títulos de nicho
- Implementado en `notebooks/02-Baseline-Model.ipynb`

### 2. Filtrado Colaborativo
#### Técnicas Implementadas:
- **Matriz Usuario-Elemento**: Matriz dispersa de calificaciones de usuarios
- **Optimización de Memoria**: Enfoque en usuarios más activos y películas populares
- **KNN (K-Nearest Neighbors)**: 
  - Similitud coseno
  - Búsqueda por fuerza bruta
- **SVD (Singular Value Decomposition)**:
  - Factorización de matrices
  - Implementado con la librería Surprise

### 3. Seguimiento de Experimentos
- **MLflow** para reproducibilidad y comparación de modelos
- Registro de métricas (RMSE)
- Gestión de artefactos de modelos
- Interfaz web para visualización de experimentos

## 📁 Estructura del Proyecto

```
LatentLens/
├── data/                   # Dataset MovieLens (no incluido en repo)
├── notebooks/             # Jupyter Notebooks para EDA y prototipado
│   ├── 01-EDA.ipynb                    # Análisis Exploratorio de Datos
│   ├── 02-Baseline-Model.ipynb         # Modelo Baseline
│   ├── 03-Collaborative-Filtering.ipynb # Filtrado Colaborativo
│   └── 05-MLflow-Experiment-Tracking.ipynb # Seguimiento con MLflow
├── src/                   # Código fuente modular
│   ├── data_loader.py              # Carga y preprocesamiento de datos
│   └── main.py                     # API FastAPI
├── tests/                 # Tests unitarios
├── Dockerfile            # Configuración de contenedor
├── docker-compose.yml    # Orquestación de servicios
├── requirements.txt      # Dependencias Python
├── setup.py             # Instalador del proyecto
└── README.md            # Documentación principal
```

## 🚀 Funcionalidades Implementadas

### ✅ Completadas
- **Pipeline de recomendación end-to-end**
- **Modelos baseline y de filtrado colaborativo** (KNN, SVD)
- **Procesamiento escalable de datos** para datasets grandes (25M+ calificaciones)
- **Base de código modular y extensible** en Python
- **Integración con MLflow** para seguimiento de experimentos
- **Notebooks de Jupyter** para EDA y prototipado
- **Evaluación de modelos** (métricas RMSE)

### 🔄 En Desarrollo
- **API REST completa** (FastAPI)
- **Dockerización completa**

## 📈 Resultados y Demo

### Ejemplos de Recomendaciones

**Si te gustó "The Godfather (1972)":**
- The Godfather: Part II (1974)
- Pulp Fiction (1994)
- Goodfellas (1990)
- The Silence of the Lambs (1991)
- The Shawshank Redemption (1994)

**Si te gustó "Goodfellas (1990)":**
- The Godfather (1972)
- Pulp Fiction (1994)
- The Godfather: Part II (1974)
- Reservoir Dogs (1992)
- Fargo (1996)

## 🎛️ Componentes Técnicos Clave

### 1. Carga de Datos (`src/data_loader.py`)
- Función robusta para cargar datasets MovieLens
- Preprocesamiento básico y limpieza de datos
- Configuración de rutas independiente del entorno de ejecución

### 2. API REST (`src/main.py`)
- Framework FastAPI para endpoints de recomendación
- Health check endpoint implementado
- Preparado para escalabilidad y producción

### 3. Notebooks de Análisis
- **EDA**: Análisis exploratorio completo del dataset
- **Baseline**: Implementación y evaluación del modelo baseline
- **Collaborative Filtering**: Algoritmos KNN y SVD optimizados para memoria
- **MLflow**: Seguimiento de experimentos y gestión de modelos

### 4. Infraestructura
- **Docker**: Imagen multi-etapa optimizada para producción
- **Docker Compose**: Orquestación de API y interfaz MLflow
- **MLflow UI**: Dashboard web para visualización de experimentos

## 📊 Métricas y Evaluación

- **RMSE (Root Mean Square Error)** como métrica principal
- **Validación cruzada** para robustez del modelo
- **Análisis de sparsity** del dataset
- **Optimización de memoria** para datasets grandes

## 🗺️ Estado Actual y Roadmap

### Estado Actual: **Trabajo en Progreso** 🟠

#### ✅ Completado:
- [x] Implementación del modelo baseline
- [x] Filtrado colaborativo (KNN, SVD)
- [x] Evaluación de modelos (RMSE)
- [x] Integración con MLflow
- [x] Análisis exploratorio de datos
- [x] Estructura modular del código

#### 🔄 En Desarrollo:
- [ ] API REST completa (FastAPI)
- [ ] Dockerización completa
- [ ] Sistema de recomendación híbrido
- [ ] Optimizaciones de rendimiento

#### 🎯 Futuras Mejoras:
- [ ] Content-based filtering
- [ ] Deep learning models
- [ ] A/B testing framework
- [ ] Recomendaciones en tiempo real
- [ ] Sistema de feedback de usuarios

## 💡 Características Técnicas Destacadas

1. **Escalabilidad**: Optimizado para manejar datasets de 25M+ registros
2. **Modularidad**: Código organizado en módulos reutilizables
3. **Reproducibilidad**: Integración completa con MLflow
4. **Flexibilidad**: Arquitectura extensible para nuevos algoritmos
5. **Producción-Ready**: API REST y contenedorización Docker

## 🎓 Aprendizajes y Metodología

El proyecto demuestra:
- **Ingeniería de datos** para datasets grandes
- **Algoritmos de machine learning** para sistemas de recomendación
- **MLOps** con seguimiento de experimentos
- **Desarrollo de APIs** con FastAPI
- **Contenerización** y despliegue con Docker
- **Análisis exploratorio** de datos con Jupyter

## 📄 Licencia

Proyecto bajo **Licencia MIT** - Código abierto y libre para uso comercial y no comercial.

---

*Este resumen proporciona una visión completa del proyecto LatentLens, desde su conceptualización hasta su implementación técnica actual.*