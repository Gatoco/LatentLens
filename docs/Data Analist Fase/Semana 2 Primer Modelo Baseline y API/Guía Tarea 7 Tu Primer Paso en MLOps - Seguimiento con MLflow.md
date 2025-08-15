# 🏛️ Guía Tarea 7: Tu Primer Paso en MLOps - Seguimiento con MLflow

[[First month]]

## Introducción: Del Caos a la Claridad - El Cuaderno del Ingeniero

Hasta ahora, has sido un explorador. Has encontrado tesoros en el EDA y has construido un primer mapa con el modelo KNN. Pero cada vez que cambiabas algo, el mapa anterior se borraba. ¿El modelo de ayer era mejor? ¿Qué parámetros usaste? Sin un registro, estás navegando a ciegas.

**MLflow es el cuaderno de bitácora de nuestro barco.** Es el sistema que registra cada decisión, cada rumbo y cada resultado. No es opcional; es la disciplina fundamental que separa los proyectos de "juguete" de los sistemas de Machine Learning listos para producción. Con MLflow, cada experimento se vuelve un activo, no un recuerdo.

---

## 🚦 Pre-vuelo: Checklist de Requisitos

- [x] **1. Entorno Virtual Activo:** Verifica que tu terminal muestra el prefijo `(venv)`. Si no, actívalo. La consistencia del entorno no es negociable.
- [x] **2. Instalar MLflow:** En tu terminal activa, ejecuta el comando para instalar la librería que será el pilar de nuestra gobernanza de modelos.
    ```bash
    pip install mlflow
    ```

---

## ✅ Checklist de Ejecución: Forjando la Primera Entrada en Nuestro Libro de Registro

### **Fase 1: Desplegar el Centro de Mando (La UI de MLflow)**

Vamos a levantar la interfaz web donde vivirá toda la historia de nuestros modelos.

- [x] **1. Navega a la Raíz del Proyecto:** Abre tu terminal y asegúrate de que estás en el directorio principal de `LatentLens/`. Es crucial, porque `mlflow` buscará la carpeta de registros (`mlruns`) desde donde lo ejecutes.
      ```bash
      # Si estás en la carpeta /notebooks, por ejemplo, ejecuta:
      cd .. 
      ```
- [x] **2. Lanza el Servidor de la UI:** Ejecuta el siguiente comando. Esto iniciará un servidor web local que sirve la interfaz de MLflow.
      ```bash
      mlflow ui
      ```
- [x] **3. Abre la Interfaz en tu Navegador:**
    - [x] Ve a la dirección: `http://127.0.0.1:5000`.
    - [x] Deberías ver una interfaz limpia, con un "Default experiment". No te preocupes, ahora la poblaremos. Mantén esta pestaña abierta.

### **Fase 2: Instrumentar Nuestro Código para que "Reporte" a MLflow**

Ahora, le enseñaremos a nuestro código a comunicarse con MLflow.

- [x] **1. Crea el Notebook para el Experimento:**
    - [x] Dentro de tu carpeta `/notebooks`, crea un nuevo archivo llamado `05-MLflow-Experiment-Tracking.ipynb`.
- [x] **2. Copia y Pega el Siguiente Código en la Primera Celda del Notebook:**
    - [x] Este es nuestro script de evaluación de la Tarea 6, pero "instrumentado". Lee atentamente los comentarios que empiezan con `# MLflow:` para entender cada nueva pieza.

      ```python
      # --- Importaciones (Añadimos mlflow) ---
      import pandas as pd
      from surprise import Reader, Dataset, KNNBasic
      from surprise.model_selection import train_test_split
      from surprise import accuracy
      import os
      import mlflow
      import mlflow.sklearn # Importante para el logging del modelo

      print("Librerías listas, incluyendo MLflow.")

      # --- Carga de Datos (Sin cambios) ---
      try:
          BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
      except NameError:
          BASE_DIR = os.path.abspath(os.path.join(os.getcwd(), '..'))

      DATA_DIR = os.path.join(BASE_DIR, 'data', 'ml-25m')
      RATINGS_PATH = os.path.join(DATA_DIR, 'ratings.csv')
      ratings_df = pd.read_csv(RATINGS_PATH)

      n_users = 40000
      n_movies = 20000
      user_ids = ratings_df['userId'].value_counts().nlargest(n_users).index
      movie_ids = ratings_df['movieId'].value_counts().nlargest(n_movies).index
      sampled_df = ratings_df[(ratings_df['userId'].isin(user_ids)) & (ratings_df['movieId'].isin(movie_ids))]

      reader = Reader(rating_scale=(0.5, 5.0))
      data = Dataset.load_from_df(sampled_df[['userId', 'movieId', 'rating']], reader)
      trainset, testset = train_test_split(data, test_size=0.2, random_state=42)

      # MLflow: 1. Definir el nombre de nuestro "cajón" de experimentos.
      mlflow.set_experiment("LatentLens-KNN-Evaluation")

      # MLflow: 2. Iniciar una "ejecución" (un run). Todo dentro de este bloque `with` será registrado.
      with mlflow.start_run() as run:
          print(f"MLflow Run ID: {run.info.run_id}")
          
          # --- Parámetros del Experimento ---
          k_neighbors = 40
          similarity_metric = 'cosine'
          
          # MLflow: 3. Registrar los parámetros que definen este experimento.
          mlflow.log_param("model_type", "KNNBasic")
          mlflow.log_param("k_neighbors", k_neighbors)
          mlflow.log_param("similarity_metric", similarity_metric)
          mlflow.log_param("user_sample_size", n_users)
          mlflow.log_param("movie_sample_size", n_movies)
          
          # --- Entrenamiento ---
          sim_options = {'name': similarity_metric, 'user_based': False}
          model = KNNBasic(k=k_neighbors, sim_options=sim_options)
          model.fit(trainset)
          
          # --- Evaluación ---
          predictions = model.test(testset)
          rmse = accuracy.rmse(predictions)
          
          # MLflow: 4. Registrar la métrica de resultado.
          mlflow.log_metric("rmse", rmse)

          # MLflow: 5. Registrar el modelo como un "artefacto".
          mlflow.sklearn.log_model(model, "surprise_knn_model")

      print("\n¡Ejecución de MLflow finalizada! Revisa la UI en http://127.0.0.1:5000")
      ```

- [x] **3. Ejecuta el Notebook Completo:**
    - [x] En Jupyter, ve al menú `Kernel > Restart & Run All`.
    - [x] Observa la salida en el notebook. Deberías ver los mensajes de MLflow confirmando el registro.

### **Fase 3: Analizar los Resultados en el Centro de Mando**

- [x] **1. Refresca la UI de MLflow:** Vuelve a la pestaña de tu navegador (`http://127.0.0.1:5000`) y presiona `F5`.
- [x] **2. Explora el Experimento:**
    - [x] Haz clic en el nombre del experimento `LatentLens-KNN-Evaluation` en el panel izquierdo.
- [x] **3. Inspecciona la Ejecución:**
    - [x] Haz clic en la nueva línea que ha aparecido, que representa tu "run".
    - [x] **Verifica los Parámetros:** Confirma que ves los valores de `k_neighbors`, `similarity_metric`, etc.
    - [x] **Verifica las Métricas:** Confirma que ves el valor de `rmse`.
    - [x] **Verifica los Artefactos:** Haz clic en la carpeta `surprise_knn_model`. ¡Ahí está tu modelo, guardado y versionado!

---

## Verificación Final y El Reto del Ingeniero

- [x] **1. Realiza un Segundo Experimento:**
    - [x] Vuelve a tu notebook `05-MLflow-Experiment-Tracking.ipynb`.
    - [x] Cambia un parámetro clave en la celda de código. Por ejemplo, cambia `k_neighbors = 40` a `k_neighbors = 20`.
    - [x] **Ejecuta únicamente esa celda de nuevo** (la que contiene el bloque `with mlflow.start_run():`). No necesitas volver a cargar los datos.
- [x] **2. Compara los Resultados:**
    - [x] Refresca la UI de MLflow otra vez.
    - [x] Ahora verás **dos "runs"** en tu experimento.
    - [x] Puedes seleccionarlos ambos y hacer clic en el botón `Compare`. MLflow te mostrará una tabla destacando las diferencias en los parámetros y las métricas.

¡Felicidades! Acabas de realizar tu primer ciclo de experimentación de forma reproducible. Has probado una hipótesis (¿un `k` más bajo es mejor o peor?) y tienes la prueba registrada para siempre. Este es el verdadero núcleo de MLOps.