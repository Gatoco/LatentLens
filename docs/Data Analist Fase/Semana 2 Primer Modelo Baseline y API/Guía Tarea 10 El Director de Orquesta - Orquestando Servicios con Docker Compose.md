# 🏛️ Guía Tarea 10: El Director de Orquesta - Orquestando Servicios con Docker Compose

[[First month]]

## Introducción: De Músicos Solistas a una Orquesta Sinfónica

Hemos empaquetado nuestra API en una caja mágica (un contenedor). Pero una aplicación real raramente vive sola. A menudo, depende de bases de datos, herramientas de monitoreo, y más. Docker Compose es la herramienta que nos permite definir y ejecutar aplicaciones compuestas por múltiples servicios, como un director de orquesta que guía a todos sus músicos.

Escribiremos una "partitura" (`docker-compose.yml`) que le dirá al director (Docker) cómo levantar a nuestros dos músicos —la API de FastAPI y la UI de MLflow— para que toquen juntos en perfecta armonía y compartan la misma información.

---

## 🚦 Pre-vuelo: Checklist de Requisitos

- [x] **1. Dockerfile Funcional:** Confirma que completaste la Tarea 9 [[Guía Tarea 9 El Blueprint de la Inmortalidad  Tu Primer Dockerfile]] y tienes un `Dockerfile` en la raíz de tu proyecto que construye tu API sin errores.
- [x] **2. Docker Desktop Activo:** Asegúrate de que Docker Desktop está abierto y funcionando. El icono de la ballena debe estar visible y estable en tu barra de tareas.
- [x] **3. Carpeta `mlruns` Existente:** Confirma que tienes la carpeta `mlruns` en la raíz de tu proyecto, que contiene los resultados de tus experimentos con el modelo SVD. Esto es crucial para que la UI de MLflow tenga algo que mostrar.

---

## ✅ Checklist de Ejecución: Escribiendo la Partitura

### **Fase 1: Crear el Archivo de Orquestación**

- [x] **1. Crea el Archivo:** En la **raíz de tu proyecto `LatentLens/`**, crea un nuevo archivo llamado exactamente `docker-compose.yml`.

### **Fase 2: Redactar la Partitura, Servicio por Servicio**

- [x] **1. Abre tu `docker-compose.yml` y pega el siguiente código completo:** Este es el contenido íntegro de tu partitura. Lo analizaremos después.

    ```yaml
    # Versión del formato de Docker Compose. Es una buena práctica definirla.
    version: '3.8'

    # La sección donde definimos a todos nuestros "músicos" (servicios).
    services:

      # --- Primer Músico: Nuestra API de FastAPI ---
      api:
        # Instrucción para construir este servicio.
        # Usa el Dockerfile que se encuentra en el directorio actual (.).
        build: .
        # Mapea el puerto 8000 de tu máquina al puerto 8000 del contenedor.
        ports:
          - "8000:8000"
        # Crea un "portal" entre la carpeta ./mlruns de tu PC y una carpeta
        # /app/mlruns dentro del contenedor. Así la API puede acceder a los modelos.
        volumes:
          - ./mlruns:/app/mlruns
        # Le da un nombre de host predecible al contenedor dentro de la red de Docker.
        hostname: latentlens-api

      # --- Segundo Músico: La UI de MLflow ---
      mlflow-ui:
        # No construimos esto. Usamos una imagen pre-fabricada y oficial de MLflow.
        image: ghcr.io/mlflow/mlflow:v2.12.1
        # Mapea el puerto 5000 de tu máquina al puerto 5000 del contenedor.
        ports:
          - "5000:5000"
        # Crea un portal a la MISMA carpeta ./mlruns, pero la monta
        # dentro de este contenedor en /mlruns.
        volumes:
          - ./mlruns:/mlruns
        # El comando que se ejecuta al arrancar para que la UI se inicie
        # y sepa dónde buscar los datos.
        command: mlflow ui --host 0.0.0.0 --backend-store-uri /mlruns
    ```

### **Fase 3: El Gran Concierto**

- [x] **1. Detén cualquier contenedor anterior:** Si tienes la API o cualquier otro contenedor corriendo desde `docker run`, ve a la terminal donde se ejecuta y presiona `Ctrl + C`. Docker Compose gestionará todo a partir de ahora.

- [x] **2. Ejecuta la Orquesta:** En tu terminal, asegúrate de estar en la **raíz de tu proyecto `LatentLens/`**. Ejecuta el único comando que necesitas:
      ```bash
      docker-compose up --build
      ```
      - **Análisis del Comando:**
        - `docker-compose up`: El comando del director para que empiece el concierto.
        - `--build`: Le dice "Si el `Dockerfile` ha cambiado, asegúrate de reconstruir la imagen de la API antes de empezar". Es una buena práctica incluirlo.

- [ ] **3. Observa la Salida:** Verás en tu terminal los logs de **ambos** servicios, mezclados y con colores diferentes (ej: `api_1        |` y `mlflow-ui_1  |`). Es la prueba de que ambos "músicos" están tocando a la vez y en perfecta sincronía.

---

## Verificación Final

- [ ] **1. Verifica al Primer Violín (La API):**
    - [x] Abre tu navegador y ve a `http://127.0.0.1:8000/health`.
    - [x] **Resultado Esperado:** Deberías ver `{"status":"ok"}`.

- [x] **2. Verifica a los Chelos (La UI de MLflow):**
    - [x] Abre una nueva pestaña y ve a `http://127.0.0.1:5000`.
    - [x] **Resultado Esperado:** Deberías ver la interfaz web de MLflow, mostrando tus experimentos `LatentLens-SVD-Evaluation`.

- [x] **3. Detener la Orquesta (Cuando termines):**
    - [x] Vuelve a la terminal donde ejecutaste `docker-compose up`.
    - [x] Presiona `Ctrl + C`. Docker Compose detendrá ambos contenedores de forma limpia.

¡Felicidades, Director! Has orquestado tu primer sistema multi-servicio. Has desplegado no solo tu aplicación, sino también su infraestructura de soporte, todo definido en un solo archivo y reproducible con un solo comando. Este es el flujo de trabajo de los profesionales y un hito gigantesco para tu portafolio.