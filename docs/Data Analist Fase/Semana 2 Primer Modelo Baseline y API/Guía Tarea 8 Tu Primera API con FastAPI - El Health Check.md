# 🏛️ Guía Tarea 8: Tu Primera API con FastAPI - El "Health Check"

[[First month]]

## Introducción: Abriendo la Tienda al Mundo

Hemos creado un cerebro de recomendación increíble con SVD y hemos medido su inteligencia con MLflow. Ahora, ese cerebro vive aislado en nuestros notebooks. El siguiente paso es darle una voz, una forma de comunicarse con el mundo exterior. Construiremos una API, que actuará como el "mostrador" de nuestra tienda, permitiendo que otras aplicaciones le hagan preguntas a nuestro modelo.

**FastAPI** es nuestra herramienta de elección. Es un framework de Python moderno, increíblemente rápido y, lo más importante, fácil de usar para principiantes pero infinitamente potente para expertos.

Nuestro primer objetivo es crear un endpoint de "chequeo de salud" (`/health`). Es una simple señal de "estamos vivos y funcionando" que es una práctica estándar en cualquier sistema de producción.

---

## 🚦 Pre-vuelo: Checklist de Requisitos

- [x] **1. Entorno Virtual Activo:** Confirma que tu terminal muestra el prefijo `(venv)`.
- [x] **2. Instalar Nuevas Herramientas:** En tu terminal activa, instala `fastapi` y `uvicorn`, que es el servidor que ejecutará nuestra aplicación.
      ```bash
      pip install fastapi "uvicorn[standard]"
      ```
      - **Análisis:** `fastapi` es la librería para construir la API. `uvicorn` es el servidor ASGI (Asynchronous Server Gateway Interface) que "sirve" la aplicación para que sea accesible a través de la web.

---

## ✅ Checklist de Ejecución: La Construcción de la Tienda

### **Fase 1: Crear el Archivo Principal de la Aplicación**

- [x] **1. Navega al Lugar Correcto:** Tu API es parte del "código fuente" de tu aplicación, no un notebook de exploración.
- [x] **2. Crea el Archivo:** Dentro de la carpeta `/src`, crea un nuevo archivo llamado `main.py`.

### **Fase 2: Escribir el Código de la "Puerta de Entrada"**

- [x] **1. Copia y Pega el Siguiente Código en tu Archivo `/src/main.py`:**

    ```python
    # 1. Importar la clase FastAPI desde la librería fastapi
    from fastapi import FastAPI

    # 2. Crear una instancia de la aplicación FastAPI
    # Esta variable 'app' es el punto central de toda nuestra API.
    app = FastAPI(
        title="LatentLens API",
        description="El sistema de recomendación de películas de LatentLens.",
        version="0.1.0",
    )

    # 3. Definir nuestro primer "endpoint" usando un decorador
    # Un decorador (@) añade funcionalidad a la función que viene después.
    # '@app.get("/health")' significa:
    # "Cuando alguien haga una petición GET a la URL '/health', ejecuta la siguiente función."
    @app.get("/health")
    def health_check():
        """
        Endpoint de chequeo de salud. Devuelve un estado 'ok' si la API está viva.
        Este es un endpoint fundamental para monitoreo y pruebas de despliegue.
        """
        return {"status": "ok"}

    ```

### **Fase 3: La Gran Inauguración - Levantar el Servidor**

- [x] **1. Abre tu Terminal en la Raíz del Proyecto:** Es crucial. Asegúrate de que tu terminal está en el directorio `LatentLens/`, NO dentro de `/src`.
- [x] **2. Ejecuta el Servidor con Uvicorn:** Escribe el siguiente comando y presiona Enter.

      ```bash
      uvicorn src.main:app --reload
      ```
      - **Análisis del Comando:**
          - `uvicorn`: El programa servidor que estamos ejecutando.
          - `src.main:app`: La ubicación de nuestra aplicación. Significa: "Dentro del paquete `src`, busca el archivo `main`, y dentro de ese archivo, encuentra la instancia llamada `app`".
          - `--reload`: ¡Esto es magia para el desarrollo! Le dice a Uvicorn que reinicie automáticamente el servidor cada vez que guardes un cambio en el archivo `main.py`.

- [x] **3. Observa la Salida:** La terminal debería mostrarte algo como esto, indicando que el servidor está funcionando:
      ```
      INFO:     Uvicorn running on http://127.0.0.1:8000 (Press CTRL+C to quit)
      INFO:     Started reloader process [...]
      INFO:     Started server process [...]
      INFO:     Waiting for application startup.
      INFO:     Application startup complete.
      ```

---

## Verificación Final

1.  **Prueba el Endpoint de Salud:**
    - [x] Abre tu navegador web.
    - [x] Ve a la siguiente URL: `http://127.0.0.1:8000/health`
    - [x] **Resultado Esperado:** Deberías ver en la página el texto en formato JSON: `{"status":"ok"}`.

2.  **Descubre la Superpotencia de FastAPI:**
    - [x] Ahora, ve a esta otra URL en tu navegador: `http://127.0.0.1:8000/docs`
    - [x] **Resultado Esperado:** FastAPI ha generado automáticamente una **página de documentación interactiva** para tu API. Verás tu endpoint `/health` listado. ¡Puedes incluso probarlo desde ahí!

¡Felicidades! Has construido y desplegado localmente tu primera API. Tu modelo ahora tiene una puerta de entrada al mundo. El siguiente paso será conectar nuestro modelo SVD a un nuevo endpoint para que pueda empezar a recibir pedidos.