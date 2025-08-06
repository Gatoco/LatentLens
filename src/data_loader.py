import pandas as pd
import os
import sys

# --- Configuración de Rutas a Prueba de Balas ---
# Este bloque asegura que el script pueda encontrar la carpeta de datos
# sin importar si lo corremos desde el notebook (en /notebooks) o desde la terminal.

# Obtenemos la ruta absoluta del directorio donde se encuentra este archivo (`src/`)
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))

# Subimos un nivel para llegar a la raíz del proyecto (`LatentLens/`)
PROJECT_ROOT = os.path.dirname(SCRIPT_DIR)

# Construimos la ruta completa a la carpeta de datos
DATASET_FOLDER = os.path.join(PROJECT_ROOT, 'data', 'ml-25m')
# -----------------------------------------------

def load_and_prepare_data():
    """
    Carga los datasets de movies y ratings del dataset MovieLens 25M, 
    los une en un solo DataFrame y realiza un preprocesamiento básico.
    
    Returns:
        pd.DataFrame: DataFrame combinado con datos limpios.
    """
    print("Cargando los datasets...")
    
    # Usamos os.path.join para construir las rutas de los archivos CSV de forma segura
    movies_df = pd.read_csv(os.path.join(DATASET_FOLDER, 'movies.csv'))
    ratings_df = pd.read_csv(os.path.join(DATASET_FOLDER, 'ratings.csv'))
    
    print(f"Datos de películas cargados: {len(movies_df)} filas.")
    print(f"Datos de calificaciones cargados: {len(ratings_df)} filas.")
    
    # --- PREPROCESAMIENTO BÁSICO ---
    
    # Unimos los DataFrames de ratings y películas para tener el título de la película en la misma tabla
    df = pd.merge(ratings_df, movies_df, on='movieId', how='left')
    
    # Omitimos el timestamp y los géneros por ahora (los usaremos en meses posteriores)
    df = df.drop(columns=['timestamp', 'genres'], errors='ignore')

    print("Preprocesamiento completado. DataFrame final listo.")
    
    return df

# --- Bloque de Prueba para la Ejecución Aislada ---
if __name__ == '__main__':
    # Este código solo se ejecuta si corremos este script directamente desde la terminal.
    # Es una buena práctica para asegurarnos de que la función funciona fuera del notebook.
    
    main_df = load_and_prepare_data()
    
    print("\nVista previa del DataFrame final:")
    print(main_df.head())