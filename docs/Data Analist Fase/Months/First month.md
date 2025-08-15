# 🎯 Q1-M1: Sistema de Recomendación - Sprint Inicial (Mes 1)

**Objetivo del Mes:** Construir la base del proyecto, desde la configuración del entorno hasta un primer modelo funcional, y sentar las bases de MLOps.

---

## 📌 Semana 1: Setup y Exploración de Datos (EDA) 


*   [x] **Entorno:** Configurar el repositorio en GitHub con una estructura de carpetas profesional (`/data`, `/notebooks`, `/src`, `/tests`). [[Guía Tarea 1 - Estructura del Repositorio]]
*   [x] **Entorno:** Crear el archivo `.gitignore` para Python y los archivos de entorno. [[Guía Tarea 2 - Configuración de .gitignore]]
*   [x] **Entorno:** Configurar un entorno virtual (`venv` o `conda`) e instalar librerías iniciales (pandas, numpy, jupyter, matplotlib, seaborn). [[Guía Tarea 3 - Activación e Instalación de Librerías]]
*   [x] **Datos:** Descargar el dataset MovieLens 25M y colocarlo en la carpeta `/data` (o un subdirectorio). [[Guía Tarea 4 - Descarga y Organización del Dataset]]
*   [x] **Análisis:** Crear un notebook en `/notebooks` para el Análisis Exploratorio de Datos (EDA).
* [[Guía Tarea 5 - Análisis Exploratorio de Datos (EDA)]]
    *   [x] Cargar los datasets (`movies.csv`, `ratings.csv`).
    *   [x] Realizar un análisis inicial: `df.info()`, `df.describe()`, `df.isnull().sum()`.
    *   [x] Visualizar la distribución de las calificaciones (histograma).
    *   [x] Identificar las 10 películas con más calificaciones.
    *   [x] Identificar los 10 usuarios más activos.
*   [x] **Documentación:** Crear el archivo `README.md` y escribir las secciones "Problema" y "Dataset".
*   [x] **Retrospectiva Semanal:** Anotar 3 cosas que aprendí y 1 obstáculo encontrado.

---

## 📌 Semana 2: Primer Modelo Baseline y API

*   [x] **Preprocesamiento:** Escribir un script en `/src` para limpiar y preparar los datos. No lo hagas en el notebook, empieza a modularizar tu código.
*   [x] **Modelo (Baseline):** Implementar un primer modelo de recomendación simple.
    *   **Opción A (Más Simple):** Un recomendador basado en popularidad (las películas mejor calificadas por más usuarios).
    *   **Opción B (Recomendado):** Un primer modelo de **filtrado colaborativo** usando Scikit-learn (`NearestNeighbors`) o Surprise.
*   [x] **Métrica:** Calcular una métrica inicial, como el Error Cuadrático Medio (RMSE), para este modelo baseline.
*   [x] **MLflow:** Instalar MLflow. Encapsular el entrenamiento del modelo en una función y usar `mlflow.start_run()` para registrar los parámetros y el RMSE. [[Guía Tarea 7 Tu Primer Paso en MLOps - Seguimiento con MLflow]]
*   [x] **API:** Instalar FastAPI. Crear un archivo `main.py` en `/src` con un endpoint de prueba `/health` que devuelva `{"status": "ok"}`.[[Guía Tarea 8 Tu Primera API con FastAPI - El Health Check]]
*   [x] **Retrospectiva Semanal:** Anotar 3 cosas que aprendí y 1 obstáculo encontrado.

---

## 📌 Semana 3: Dockerización y Modelo Avanzado

*   [x] **Docker:** Escribir un `Dockerfile` para la API de FastAPI.
    *   [x] Debe usar una imagen base de Python.
    *   [x] Debe copiar el código fuente de `/src`.
    *   [x] Debe instalar las dependencias desde un archivo `requirements.txt`.
    *   [x] Debe exponer el puerto correcto y ejecutar la aplicación con `uvicorn`.
*   [x] **Docker-Compose:** Crear un `docker-compose.yml` para levantar la API y (opcionalmente) la UI de MLflow.
*   [x] **Pruebas:** Construir y ejecutar el contenedor localmente. Probar que el endpoint `/health` funciona desde fuera del contenedor.
*   [x] **Modelo (Avanzado):** Implementar un modelo más robusto, como la **Descomposición en Valores Singulares (SVD)** usando Scikit-learn (`TruncatedSVD`) o la librería Surprise.
*   [x] **API (Integración):** Crear un nuevo endpoint en la API, `/recommend/{user_id}`, que cargue el modelo entrenado (guárdalo con `pickle` o `joblib`) y devuelva una lista de 10 películas recomendadas.
*   [x] **MLflow:** Registrar el nuevo experimento con SVD en MLflow. Compara su RMSE con el del modelo baseline.
*   [x] **Retrospectiva Semanal:** Anotar 3 cosas que aprendí y 1 obstáculo encontrado.

---

## 📌 Semana 4: CI/CD Básico y Refinamiento

*   [ ] **Testing:** Escribir al menos un test unitario simple con `pytest` para alguna función de preprocesamiento en `/src`. Colocarlo en la carpeta `/tests`.[[Guía Tarea 12 La Cámara Hiperbárica - Tu Primer Test Unitario con Pytest]]
*   [ ] **CI/CD (GitHub Actions):** Crear un workflow en `.github/workflows/main.yml`.
    *   [ ] Debe activarse en cada `push` a la rama `main` o en Pull Requests.
    *   [ ] **Paso 1:** Hacer checkout del código.
    *   [ ] **Paso 2:** Construir la imagen de Docker.
    *   [ ] **Paso 3:** Ejecutar los tests con `pytest` dentro del contenedor de Docker.
*   [ ] **Documentación:** Actualizar el `README.md` con las secciones "Cómo Ejecutarlo" (usando Docker) y una primera versión de "Arquitectura Técnica".
*   [ ] **Código:** Refactorizar el código: asegurarse de que las funciones estén bien documentadas con docstrings y que las variables tengan nombres claros.
*   [ ] **Retrospectiva Mensual:** Revisar el progreso del mes. ¿Cumpliste las metas? ¿Qué ajuste necesitas para el Mes 2? Planifica las tareas del siguiente mes.


