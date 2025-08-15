# 📚 Base de Conocimiento Detallada: El Kit de Herramientas para el EDA

Este documento es tu guía de referencia y material de apoyo principal para completar la **Tarea 5: Análisis Exploratorio de Datos (EDA)**. Cada sección se corresponde con una de las subtareas, explicándote las herramientas de `pandas` que necesitas y la lógica detrás de ellas.

---

### **El Corazón de Pandas: El DataFrame**

Antes de empezar, recuerda qué son las estructuras con las que trabajamos:

*   **`DataFrame`**: Piensa en él como una tabla completa, similar a una hoja de cálculo de Excel pero con superpoderes. Contiene filas y columnas. (`movies_df`, `ratings_df`).
*   **`Series`**: Piensa en ella como una sola columna de esa tabla. Cuando seleccionas una columna de un DataFrame (ej: `movies_df['title']`), obtienes una Serie.

---

### **Tarea 5.1: Cargar los Datasets (`.read_csv`)**

Esta es la puerta de entrada. Debemos traer nuestros archivos de datos al entorno de Python para poder manipularlos.

*   **La Herramienta:** `pandas.read_csv()`
*   **¿Qué hace?** Lee un archivo de valores separados por comas (CSV) y lo convierte en un DataFrame de pandas.
*   **¿Cómo se usa?**
    ```python
    import pandas as pd

    # La ruta le dice a Python dónde encontrar el archivo.
    # '..' significa "subir un nivel de carpeta" desde la ubicación del notebook.
    ruta_a_movies = '../data/ml-25m/movies.csv'
    
    # Creamos un DataFrame llamado 'movies_df' a partir del archivo.
    movies_df = pd.read_csv(ruta_a_movies)
    ```

---

### **Tarea 5.2: El Chequeo Médico (Análisis Inicial)**

Una vez cargados los datos, actuamos como médicos: realizamos un chequeo general para entender la "salud" de nuestro dataset.

#### **A. La Radiografía Completa (`.info()`)**
*   **La Herramienta:** `tu_dataframe.info()`
*   **¿Qué hace?** Te da un resumen técnico completo del DataFrame.
*   **¿Cómo se interpreta el resultado?**
    *   **`RangeIndex`**: Te dice el número total de filas (entradas).
    *   **`Data columns`**: Te dice el número total de columnas.
    *   **La tabla de columnas**: Te muestra:
        *   **`Non-Null Count`**: Cuántas celdas en esa columna **no** están vacías.
        *   **`Dtype`**: El "tipo de dato" que pandas asignó. Los más comunes que verás:
            *   `int64`: Números enteros.
            *   `float64`: Números con decimales.
            *   `object`: Generalmente, texto (o "strings").
    *   **`memory usage`**: Cuánta memoria RAM está ocupando tu DataFrame. ¡Importante para datasets grandes!

#### **B. El Resumen Estadístico (`.describe()`)**
*   **La Herramienta:** `tu_dataframe.describe()`
*   **¿Qué hace?** Calcula estadísticas descriptivas básicas para todas las **columnas numéricas**.
*   **¿Cómo se interpreta el resultado?**
    *   `count`: El número de valores no nulos.
    *   `mean`: La media o promedio.
    *   `std`: La desviación estándar (mide la dispersión de los datos).
    *   `min`: El valor más pequeño.
    *   `25%`, `50%`, `75%`: Los percentiles. El 50% es la **mediana**.
    *   `max`: El valor más grande.

#### **C. El Detective de Datos Faltantes (`.isnull().sum()`)**
*   **La Herramienta:** Una combinación de `tu_dataframe.isnull().sum()`
*   **¿Cómo funciona?**
    1.  `.isnull()`: Escanea toda la tabla y crea una nueva tabla (invisible para ti) con `True` si una celda está vacía y `False` si no lo está.
    2.  `.sum()`: Suma los valores de cada columna. En Python, `True` cuenta como `1` y `False` como `0`. El resultado final es una cuenta de cuántos `True` (celdas vacías) hay en cada columna.
*   **¿Cómo se interpreta el resultado?** Es el chequeo más rápido y claro para saber si tienes datos faltantes y dónde. Un `0` significa que la columna está perfectamente completa.

---

### **Tarea 5.3: Visualizar la Distribución (Histograma)**

Los números están bien, pero una imagen cuenta una historia más rápida.

*   **Las Herramientas:** `matplotlib.pyplot` y `seaborn`.
*   **¿Cómo funcionan juntas?** `matplotlib` es el motor de gráficos fundamental de Python. `seaborn` es una librería construida sobre matplotlib que hace que los gráficos se vean más bonitos y atractivos con menos código.
*   **La Función Clave para esta Tarea: `seaborn.countplot()`**
    *   **¿Qué hace?** Cuenta automáticamente cuántas veces aparece cada valor único en una columna y crea un gráfico de barras a partir de esa cuenta. Es perfecto para visualizar la distribución de una variable categórica como `rating`.
    *   **¿Cómo se usa?**
      ```python
      import matplotlib.pyplot as plt
      import seaborn as sns
      
      # Crea el espacio para el gráfico y define su tamaño
      plt.figure(figsize=(12, 7))
      
      # Crea el gráfico de barras usando seaborn
      sns.countplot(x='rating', data=ratings_df)
      
      # Añade títulos para que el gráfico sea fácil de entender
      plt.title('Distribución de las Calificaciones')
      plt.xlabel('Calificación (Rating)')
      plt.ylabel('Número Total de Votos')
      
      # Muestra el gráfico
      plt.show()
      ```

---

### **Tarea 5.4 y 5.5: Identificar a los Más Activos y Populares**

Aquí necesitamos contar, ordenar y mostrar los "top 10".

*   **La Herramienta Principal:** `tu_serie.value_counts()`
*   **¿Qué hace?** Esta es una de las funciones más útiles. Cuando se aplica a una Serie (una columna), cuenta la frecuencia de cada valor único y **devuelve una nueva Serie ordenada de la más frecuente a la menos frecuente**.
*   **¿Cómo se usa para encontrar los usuarios más activos?**
    ```python
    # 1. Selecciona la columna 'userId'
    # 2. Cuenta cuántas veces aparece cada ID de usuario
    # 3. .head(10) nos da solo los 10 primeros de la lista ya ordenada
    top_10_users = ratings_df['userId'].value_counts().head(10)
    
    print(top_10_users)
    ```
*   **¿Cómo se usa para encontrar las películas más populares?**
    *   Este caso es un poco más complejo porque `value_counts()` nos dará el `movieId` (un número), pero nosotros queremos ver el **título** de la película. Esto requiere una combinación de herramientas:
      ```python
      # Paso 1: Contar las calificaciones para cada movieId como antes
      movie_rating_counts = ratings_df['movieId'].value_counts().head(10)
      
      # El resultado es una Serie con movieId como índice. Para unirla, la convertimos en un DataFrame
      top_10_movies_df = movie_rating_counts.to_frame().reset_index()
      top_10_movies_df.columns = ['movieId', 'count']

      # Paso 2: Usar pd.merge() para unir esta información con el DataFrame de películas
      # Es como un VLOOKUP en Excel o un JOIN en SQL
      # Buscamos las filas en movies_df cuyo 'movieId' esté en nuestra lista del top 10
      top_10_with_titles = pd.merge(top_10_movies_df, movies_df, on='movieId')

      print(top_10_with_titles)
      ```