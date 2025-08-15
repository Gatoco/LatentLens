# 🏛️ Guía Paso a Paso: Tu Quinta Tarea - Análisis Exploratorio de Datos (EDA)

[[First month]]

## Introducción: Conviértete en un Detective de Datos

Hasta ahora, hemos construido el edificio y traído los materiales. Ahora, abrimos la puerta del laboratorio para examinar esos materiales bajo el microscopio. Esto es el Análisis Exploratorio de Datos (EDA).

Nuestro objetivo no es construir un modelo todavía. Es hacer preguntas y encontrar respuestas preliminares:
*   ¿Cómo son nuestros datos? ¿Están completos?
*   ¿Cuál es el comportamiento de los usuarios?
*   ¿Qué características tienen las películas?

Usaremos un **Jupyter Notebook** para esto. Piensa en él como un cuaderno de laboratorio interactivo donde puedes escribir código, ejecutarlo, ver los resultados (tablas, gráficos) y escribir notas, todo en un mismo lugar.

---

## 🚦 Pre-vuelo: Checklist de Requisitos

*   [x] **1. Entorno Virtual Activo:** Asegúrate de tener tu entorno `(venv)` activo en la terminal. Si no ves el prefijo, actívalo ahora.
*   [x] **2. Librerías Instaladas:** Confirma que completaste la tarea anterior y tienes `pandas`, `matplotlib`, `seaborn` y `jupyter` instalados en tu `venv`.

---

## ✅ Checklist de Ejecución: La Primera Interrogación a los Datos

Sigue estos pasos en orden.

### **Fase 1: Iniciar Nuestro Laboratorio (Jupyter Notebook)**

*   [x] **1. Lanza Jupyter:** En tu terminal (con el entorno activo), ejecuta el siguiente comando:
      ```bash
      jupyter notebook
      ```
*   [x] **2. Navega y Crea:** Se abrirá una pestaña en tu navegador web mostrando la estructura de tu proyecto.
    *   Haz clic en la carpeta `notebooks/`.
    *   Una vez dentro, haz clic en el botón `New` (arriba a la derecha) y selecciona `Python 3 (ipykernel)`.
*   [x] **3. Renombra tu Notebook:** Se abrirá una nueva pestaña con tu notebook. Haz clic en "Untitled" en la parte superior y renómbralo a algo descriptivo, como `01-EDA`.
*   [x] **4. Escribe tu Primera Línea (Importar Librerías):** En la primera celda del notebook, escribe el siguiente código para importar las herramientas que necesitaremos.
      ```python
      import pandas as pd
      import numpy as np
      import matplotlib.pyplot as plt
      import seaborn as sns

      # Configuración para que los gráficos se muestren en el notebook
      %matplotlib inline
      ```
*   [x] **5. Ejecuta la Celda:** Presiona `Shift + Enter` para ejecutar el código de la celda.

### **Fase 2: Cargar los Datasets**

*   [x] **1. Define las Rutas:** En la siguiente celda, escribe el código para definir dónde están tus archivos. Usar rutas relativas es una buena práctica.
      ```python
      # Define la ruta a la carpeta de datos
      DATA_PATH = '../data/ml-25m/'

      # Carga los datasets en DataFrames de pandas
      movies_df = pd.read_csv(f'{DATA_PATH}movies.csv')
      ratings_df = pd.read_csv(f'{DATA_PATH}ratings.csv')
      ```
      - **Análisis:** Un **DataFrame de pandas** es la estructura de datos fundamental para el análisis en Python. Imagínalo como una tabla de Excel con superpoderes.
*   [x] **2. Ejecuta la Celda:** Presiona `Shift + Enter`. Pandas cargará los archivos CSV en la memoria.

### **Fase 3: El "Chequeo Médico" de los Datos**

Ahora vamos a realizar una revisión rápida de la "salud" de nuestros DataFrames.

*   [x] **1. Revisa `movies_df`:** En una nueva celda, explora el DataFrame de películas.
      ```python
      print("Información de movies_df:")
      movies_df.info()

      print("\nPrimeras 5 filas de movies_df:")
      movies_df.head()
      ```
*   [x] **2. Revisa `ratings_df`:** Haz lo mismo para el DataFrame de calificaciones.
      ```python
      print("Información de ratings_df:")
      ratings_df.info()

      print("\nEstadísticas descriptivas de ratings_df:")
      ratings_df.describe()
      
      print("\nChequeo de valores nulos en ratings_df:")
      ratings_df.isnull().sum()
      ```
      - **Análisis de Resultados:**
          - `info()`: Te dice cuántas filas hay, los nombres de las columnas, y si hay valores faltantes. Muy útil para ver los tipos de datos (ej: `int64`, `object`).
          - `describe()`: Te da estadísticas básicas (media, desviación estándar, mínimo, máximo) para las columnas numéricas.
          - `isnull().sum()`: Te dice exactamente cuántos valores nulos (vacíos) hay en cada columna.
          - `head()`: Te muestra una vista previa de las primeras filas de la tabla.

### **Fase 4: Visualización y Primeros Insights**

Es hora de hacer preguntas más interesantes.

*   [x] **1. ¿Cómo se Distribuyen las Calificaciones?** En una nueva celda, crea un histograma para visualizar la frecuencia de cada calificación.
      ```python
      plt.figure(figsize=(10, 6))
      sns.countplot(x='rating', data=ratings_df)
      plt.title('Distribución de las Calificaciones de Películas')
      plt.xlabel('Calificación')
      plt.ylabel('Número de Votos')
      plt.show()
      ```
      - **Análisis:** Este gráfico te mostrará qué calificaciones son más comunes. Probablemente veas que los usuarios tienden a dar más calificaciones altas (3, 4, 5 estrellas) que bajas.

*   [x] **2. ¿Cuáles son las Películas Más Populares?** (con más calificaciones).
      ```python
      # Contar cuántas calificaciones tiene cada película
      movie_counts = ratings_df['movieId'].value_counts()

      # Unir esta información con los títulos de las películas
      top_movies = movie_counts.to_frame().reset_index()
      top_movies.columns = ['movieId', 'rating_count']
      top_movies = pd.merge(top_movies, movies_df, on='movieId')

      print("Top 10 películas con más calificaciones:")
      top_movies.head(10)
      ```
*   [x] **3. ¿Quiénes son los Usuarios Más Activos?**
      ```python
      # Contar cuántas películas ha calificado cada usuario
      user_counts = ratings_df['userId'].value_counts()

      print("\nTop 10 usuarios más activos:")
      print(user_counts.head(10))
      ```
*   [x] **4. Guarda tu Notebook:** No olvides guardar tu trabajo. Haz clic en el ícono del disquete en la parte superior izquierda o presiona `Ctrl + S`.

---

## Verificación Final

1.  Tu notebook `01-EDA.ipynb` debería estar guardado en la carpeta `/notebooks`.
2.  Al ejecutar todas las celdas de arriba a abajo (`Kernel > Restart & Run All`), el notebook debería funcionar sin errores.
3.  Deberías poder ver las tablas de salida y el gráfico de barras directamente en tu notebook.
4.  **Pregúntate:** ¿Qué he aprendido de los datos hasta ahora? Escribe una pequeña nota en una celda de Markdown en tu notebook con tu primer insight. Por ejemplo: *"Insight: La película más popular por número de votos es Pulp Fiction, y los usuarios tienden a dar calificaciones enteras (como 4.0) más a menudo que medias estrellas (como 3.5)."*

¡Felicidades! Has realizado tu primer análisis exploratorio. Has "conversado" con los datos por primera vez y has extraído información valiosa que guiará los siguientes pasos en la construcción de tu modelo.



# 🧠 Análisis Exploratorio Profundo: Interrogando al Dataset LatentLens



**Objetivo:** Ir más allá de las estadísticas superficiales para descubrir los patrones y sesgos ocultos en los datos. Cada respuesta debe estar respaldada por evidencia generada con código.

---

### **1. Comportamiento del Usuario**

**Pregunta 1.1:** ¿Cuál es el número medio y mediano de calificaciones por usuario? ¿Qué nos dice la diferencia (o similitud) entre estos dos valores sobre la distribución del comportamiento de los usuarios?
*   **Tu Respuesta:** El número medio de calificaciones por usuario es de **153.81**, mientras que el número mediano es de **71.0**.

La diferencia tan significativa entre la media y la mediana revela que la distribución de la actividad de los usuarios está **fuertemente sesgada a la derecha (right-skewed)**. Esto significa que no es una distribución normal.

La **mediana (71)** es un mejor representante del "usuario típico", indicando que la mitad de los usuarios han calificado 71 películas o menos. La **media (153.81)**, en cambio, está inflada por un pequeño grupo de usuarios extremadamente activos ("power users") que han calificado miles de películas. Estos usuarios actúan como valores atípicos (outliers) que tiran del promedio hacia arriba.

**Conclusión:** La actividad en la plataforma no es uniforme. La mayoría de los usuarios son ocasionales, mientras que un nicho muy activo es responsable de una gran proporción de las calificaciones totales. Esto será importante al diseñar el modelo, ya que no podemos depender únicamente del comportamiento de los "super-usuarios".


**Pregunta 1.2:** ¿Son los usuarios más activos (top 1% por número de calificaciones) más o menos críticos que el usuario promedio?
*   **Tu Respuesta:** **Sí, existe una diferencia clara.** La calificación media de todos los usuarios en el dataset es de **3.53**. Sin embargo, la calificación media para el top 1% de usuarios más activos es notablemente más baja, situándose en **3.21**.

Esta diferencia demuestra que los usuarios más activos tienden a ser **significativamente más críticos y exigentes** que el usuario promedio.

**Implicación para el proyecto:** Este hallazgo es importante. Un modelo de recomendación entrenado con todos los datos podría estar sesgado por las opiniones menos críticas de la mayoría. Debemos ser conscientes de que nuestros "expertos" o "power users" tienen un estándar de calidad más alto.

---

### **2. Características de las Películas**

**Pregunta 2.1:** ¿Existe una superposición significativa entre las 10 películas más populares (por número de votos) y las 10 películas mejor calificadas (por calificación media)? ¿Por qué podría ser peligroso recomendar solo basándose en la calificación media?
*   **Tu Respuesta:** **No, no existe una superposición significativa.** Al analizar las dos listas, se observa que son casi completamente diferentes. Las películas más populares (como Forrest Gump o Pulp Fiction) son éxitos masivos con decenas de miles de votos, pero sus calificaciones medias no son las más altas del dataset.

Por otro lado, las películas mejor calificadas (como The Shawshank Redemption) son obras maestras aclamadas por la crítica, pero no necesariamente las más vistas.

Esto revela por qué **es muy peligroso recomendar basándose únicamente en la calificación media**. Un producto podría tener una calificación perfecta de 5.0, pero basada en una sola opinión. Este promedio no es estadísticamente significativo y no representa la opinión general. Para evitar la "trampa de la película de culto", se debe implementar un sistema que pondere la calificación media con el número de votos recibidos, dando más peso a los promedios que están respaldados por una gran cantidad de opiniones.

**Pregunta 2.2:** ¿Cuáles son los 5 géneros más comunes en el dataset? (Considerando que una película puede tener múltiples géneros).
*   **Tu Respuesta:** 
1. Drama: 25.606
2. Comedy: 16.870
3. Thriller: 8.654
4. Romance: 7.719
5. Action: 7.348


**Pregunta 2.3:** Al analizar las calificaciones promedio por género, se observa una clara y fascinante tendencia:

- **Géneros Mejor Calificados:** Los géneros con las notas medias más altas son consistentemente aquellos considerados "de prestigio" o de nicho, como **Film-Noir (3.93), War (3.79) y Documentary (3.71)**.
    
- **Géneros Peor Calificados:** Por otro lado, los géneros con las notas medias más bajas tienden a ser los más masivos o aquellos con una audiencia muy amplia, como **Horror (3.29), Comedy (3.42) y Children (3.43)**.
    

**Hipótesis:**  
Mi hipótesis se basa en el **tipo de audiencia y la naturaleza del género**:

1. **Para los géneros mejor calificados:** Estos géneros (Documental, Film-Noir, War) a menudo atraen a una **audiencia autoseleccionada** que ya tiene interés en el tema o aprecia el valor artístico. Este público está predispuesto a valorar positivamente la película, llevando a promedios más altos.
    
2. **Para los géneros peor calificados:** Géneros como el Terror o la Comedia son de **consumo masivo y a menudo divisivos**. Una persona puede ver una película de terror por la adrenalina y no por su calidad, o una comedia puede simplemente no "conectar" con su humor. Esto genera una gama de opiniones mucho más amplia y, en consecuencia, una calificación promedio más baja.


---

### **3. Interacciones y Patrones Ocultos**

**Pregunta 3.1:** ¿Qué porcentaje de películas en el dataset tiene menos de 5 calificaciones? ¿Qué implicaciones tiene esto para un modelo de filtrado colaborativo?
*   **Tu Respuesta:** Un 42.18% de las películas en el catálogo tienen menos de 5 calificaciones. Esto representa un número significativo de 26.327 películas.

Esto tiene **implicaciones muy serias** para un modelo de filtrado colaborativo:

1. **Falta de Señal Suficiente:** El filtrado colaborativo funciona encontrando patrones en cómo los usuarios califican las películas. Si una película tiene muy pocas calificaciones, no hay un "patrón" estadísticamente significativo que el modelo pueda aprender. Las pocas calificaciones existentes son básicamente "ruido".
    
2. **Imposibilidad de Recomendar:** El modelo tendrá muy difícil (o imposible) recomendar estas películas de forma precisa, ya que no tiene "prueba social" de si son buenas o malas para un tipo de usuario u otro.
    
3. **Riesgo de Sobreajuste (Overfitting):** El modelo podría darle demasiada importancia a las pocas calificaciones que existen. Por ejemplo, si una película tiene una sola calificación de 5 estrellas, el modelo podría pensar erróneamente que es una obra maestra universal.
    

**Conclusión Práctica:** Para entrenar nuestro primer modelo, probablemente deberíamos considerar **excluir estas películas** o tratarlas de una manera especial, ya que no proporcionan suficiente información fiable para el algoritmo.

**Pregunta 3.2:** ¿Qué porcentaje de usuarios ha calificado menos de 5 películas? ¿Cómo se relaciona esto con el problema del "arranque en frío" (cold start)?
*   **Tu Respuesta:**  Sorprendentemente, el análisis revela que **el 0.00% de los usuarios** ha calificado menos de 5 películas. De hecho, tras una investigación más profunda, se descubre que todos los usuarios en este dataset han calificado al menos 20 películas.

Este resultado no indica la ausencia del problema del "arranque en frío" en el mundo real, sino que revela una característica clave de este dataset: **es un conjunto de datos pre-filtrado y curado para la investigación.** Los creadores ya eliminaron a los usuarios con muy poca actividad para proporcionar un dataset más "denso" y de mayor calidad.

**Implicaciones para el proyecto:**

1. **Ventaja a Corto Plazo:** Nuestro primer modelo de filtrado colaborativo se beneficiará de estos datos limpios y probablemente logrará una alta precisión predictiva para los usuarios existentes en el dataset.
    
2. **Desafío a Largo Plazo:** Debemos ser muy conscientes de que nuestro modelo, por defecto, **no sabrá cómo manejar a un usuario verdaderamente nuevo**. Por lo tanto, es absolutamente crítico que nuestro sistema híbrido (que planeamos construir más adelante) tenga una estrategia robusta para el "arranque en frío", como recomendar las películas más populares, ya que no podremos depender de los datos de este dataset para simular ese escenario de forma natural.

---

### **4. Análisis Temporal (Bonus)**

**Pregunta 4.1:** Al convertir la columna `timestamp`, ¿cuál es el rango de fechas cubierto por el dataset (desde la primera calificación hasta la última)? ¿Hubo algún año con un pico notable de actividad?
*   **Tu Respuesta:** El análisis de la columna timestamp revela que el dataset cubre un rango temporal significativo.

- La **primera calificación** registrada es del 1995-01-09.
    
- La **última calificación** es del 2019-11-21.
    

Al visualizar la distribución de la actividad por año, se observa un **pico muy notable** de calificaciones. El año con la mayor actividad fue 2016**, durante el cual se registraron más de 1.757.440 calificaciones.

**Hipótesis/Implicación:** Este pico podría corresponder a un período de máxima popularidad de la plataforma MovieLens o a una campaña específica de recolección de datos. La existencia de estos "picos y valles" temporales es importante porque los gustos cinematográficos y el comportamiento de los usuarios pueden cambiar con el tiempo. Un modelo de recomendación avanzado podría beneficiarse de darle más peso a las calificaciones más recientes.

---
