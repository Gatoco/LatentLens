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
RUN apt-get update && apt-get install -y build-essential

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

# Ahora copiamos nuestro código fuente, como antes.
COPY ./src /app/src

# Exponemos el puerto y definimos el comando de inicio, como antes.
EXPOSE 8000
CMD ["uvicorn", "src.main:app", "--host", "0.0.0.0", "--port", "8000"]