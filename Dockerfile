# ===================================================================
# FASE 1: "EL TALLER DE MAQUINADO" (Builder Stage)
# Aquí instalamos TODAS las herramientas pesadas.
# Usamos una imagen de Python completa (no slim) que incluye gcc.
# ===================================================================
FROM python:3.10 as builder

# Creamos nuestro espacio de trabajo
WORKDIR /app

# Actualizamos el sistema e instalamos las herramientas de construcción
# como una buena práctica, por si algo más las necesitara.
RUN apt-get update \
    && apt-get install -y --no-install-recommends build-essential git \
    && rm -rf /var/lib/apt/lists/*

# Copiamos solo el manifiesto de dependencias
COPY requirements.txt .

# Instalamos TODAS las dependencias. Aquí sí se compilará scikit-surprise
# y se generarán los "wheels" (ruedas) o paquetes pre-compilados.
RUN pip install --no-cache-dir -r requirements.txt


# ===================================================================
# FASE 2: "LA SALA DE ENSAMBLAJE LIMPIA" (Final Stage)
# Aquí volvemos a empezar desde una base limpia y minimalista.
# ===================================================================
FROM python:3.10-slim

WORKDIR /app

# --- LA MAGIA ESTÁ AQUÍ ---
# En lugar de RE-INSTALAR todo, COPIAMOS los paquetes ya instalados
# desde nuestro "taller de maquinado" (el stage 'builder').
COPY --from=builder /usr/local/lib/python3.10/site-packages /usr/local/lib/python3.10/site-packages
COPY --from=builder /usr/local/bin /usr/local/bin

# Ahora copiamos nuestro código fuente, tests, datos y configuración.
COPY ./src /app/src
COPY ./tests /app/tests
COPY ./data /app/data
COPY setup.py /app/

# Descargar dataset MovieLens (ml-latest-small ~1MB) para demo self-contained
# Si el dataset completo (ml-25m vía DVC) está presente, se usa ese en su lugar
RUN python -c "import os, zipfile, urllib.request; dst='/app/data/ml-25m'; \
os.makedirs(dst, exist_ok=True) if not os.path.exists(os.path.join(dst, 'ratings.csv')) else None; \
(urllib.request.urlretrieve('https://files.grouplens.org/datasets/movielens/ml-latest-small.zip', '/tmp/ml.zip') if not os.path.exists(os.path.join(dst, 'ratings.csv')) else None); \
zipfile.ZipFile('/tmp/ml.zip').extractall('/tmp/ml') if os.path.exists('/tmp/ml.zip') else None; \
[open(os.path.join(dst, f), 'wb').write(open(f'/tmp/ml/ml-latest-small/{f}', 'rb').read()) for f in ('ratings.csv', 'movies.csv', 'tags.csv') if os.path.exists('/tmp/ml.zip')]; \
os.remove('/tmp/ml.zip') if os.path.exists('/tmp/ml.zip') else None"

# Instalamos el paquete en modo editable para que pytest funcione
RUN pip install -e .

# Directorios runtime (logs, datos de MLflow)
RUN mkdir -p /app/logs /app/mlruns && chmod -R 777 /app/logs /app/mlruns

# Exponemos el puerto y definimos el comando de inicio, como antes.
EXPOSE 8000
CMD ["uvicorn", "src.main:app", "--host", "0.0.0.0", "--port", "8000"]