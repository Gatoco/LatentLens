# 🏛️ Guía Tarea 9: El Blueprint de la Inmortalidad - Tu Primer Dockerfile

[[First month]]

## Introducción: Del Código Mortal al Contenedor Inmortal

Hasta ahora, nuestra aplicación vive y muere con nuestro ordenador. Docker nos permite capturar su esencia en un "blueprint" (el `Dockerfile`) para que pueda ser resucitada, idéntica y perfecta, en cualquier máquina del universo. Este es el momento en que pasas de ser un "desarrollador de aplicaciones" a un "ingeniero de sistemas".

Vamos a escribir, instrucción por instrucción, el manual para construir nuestra aplicación `LatentLens` dentro de un contenedor.

---

## 🚦 Pre-vuelo: Checklist de Requisitos

- [x] **1. Docker Desktop Activo:** Confirma que la aplicación Docker Desktop está abierta y funcionando en tu máquina. El icono de la ballena debe estar visible y estable.
- [x] **2. Manifiesto de Dependencias (`requirements.txt`) Listo:**
    - [x] Confirma que tienes un archivo `requirements.txt` en la raíz de tu proyecto.
    - [x] **Auditoría Crucial:** Ábrelo y asegúrate de que **no contiene** una línea que empiece con `-e git+...`. Esta línea es solo para desarrollo local y romperá el proceso de construcción. Si está, bórrala y guarda el archivo.

---

## ✅ Checklist de Ejecución: Escribiendo el Manual, Paso a Paso

### **Fase 1: Crear el Archivo del Blueprint**

- [x] **1. Crea el Archivo:** En la **raíz de tu proyecto `LatentLens/`**, crea un nuevo archivo llamado exactamente `Dockerfile` (sin extensión de archivo como `.txt`).

### **Fase 2: Redactar las Instrucciones de Ensamblaje**

Ahora, abre tu `Dockerfile` vacío y empieza a añadir las siguientes instrucciones, una por una, marcando la casilla al completar cada paso.

- **1. Instrucción `FROM`: La Fundación.**
    - **Propósito:** Este es el Paso 1 del manual. Define la "tabla" base sobre la que construiremos todo. Le dice a Docker que empiece con un sistema operativo Linux que ya tiene una versión específica de Python pre-instalada.
    - [x] **Tu Tarea:** Escribe la siguiente línea en tu `Dockerfile`:
      ```dockerfile
      FROM python:3.10-slim
      ```

- **2. Instrucción `WORKDIR`: El Espacio de Trabajo.**
    - **Propósito:** Esto es como decir "despeja una mesa para trabajar". Crea una carpeta específica dentro del contenedor y establece que todos los siguientes pasos del manual se ejecutarán desde ahí. Es una práctica de limpieza fundamental.
    - [x] **Tu Tarea:** Añade esta línea a continuación:
      ```dockerfile
      WORKDIR /app
      ```

- **3. Instrucción `COPY` y `RUN`: La Instalación de Herramientas.**
    - **Propósito:** Este es un combo de dos pasos, y es una técnica de profesional. En lugar de copiar todo tu proyecto y luego instalar las dependencias, lo hacemos en dos fases para aprovechar el sistema de caché de Docker. Si las dependencias no cambian, Docker no las reinstalará cada vez, haciendo las futuras construcciones mucho más rápidas.
    - [x] **Tu Tarea (Paso 3a):** Añade la instrucción para copiar solo el manifiesto:
      ```dockerfile
      COPY requirements.txt .
      ```
    - [x] **Tu Tarea (Paso 3b):** Ahora, añade la instrucción para instalar las dependencias:
      ```dockerfile
      RUN pip install --no-cache-dir -r requirements.txt
      ```

- **4. Instrucción `COPY`: Traer Tu Proyecto.**
    - **Propósito:** Ahora que todas las herramientas (librerías) están instaladas en el contenedor, es el momento de traer tu propio código fuente.
    - [x] **Tu Tarea:** Copia el código fuente de tu aplicación:
      ```dockerfile
      COPY ./src /app/src
      ```

- **5. Instrucción `EXPOSE`: La Señalización del Puerto.**
    - **Propósito:** Esta instrucción es como poner una pegatina en el exterior del contenedor que dice: "Oye, mundo de Docker, la aplicación que vive aquí dentro tiene la intención de escuchar peticiones en el puerto 8000". No abre el puerto, solo lo documenta.
    - [x] **Tu Tarea:** Expón el puerto que usará `uvicorn`:
      ```dockerfile
      EXPOSE 8000
      ```

- **6. Instrucción `CMD`: El Botón de "Encendido".**
    - **Propósito:** Este es el último paso del manual. Le dice a Docker qué comando ejecutar por defecto cuando alguien inicie un contenedor a partir de esta imagen. Es el comando que enciende tu API.
    - [x] **Tu Tarea:** Define el comando de inicio final y crucial:
      ```dockerfile
      CMD ["uvicorn", "src.main:app", "--host", "0.0.0.0", "--port", "8000"]
      ```

### **Fase 3: Revisión Final del Código Completo**

- [x] **1. Compara tu archivo:** Antes de terminar, asegúrate de que tu `Dockerfile` se vea exactamente así. Este bloque es para tu referencia y verificación.

    ```dockerfile
    # FASE 1: La Base
    FROM python:3.10-slim

    # FASE 2: Configurar el Entorno de Trabajo
    WORKDIR /app

    # FASE 3: Instalar Dependencias (Cache-friendly)
    COPY requirements.txt .
    RUN pip install --no-cache-dir -r requirements.txt

    # FASE 4: Copiar el Código de la Aplicación
    COPY ./src /app/src

    # FASE 5: Exponer el Puerto
    EXPOSE 8000

    # FASE 6: El Comando de Ejecución
    CMD ["uvicorn", "src.main:app", "--host", "0.0.0.0", "--port", "8000"]
    ```

---

## Verificación Final

1.  **Revisa tu `Dockerfile`:** Lee tu archivo de arriba a abajo. Debería contar una historia lógica: empezamos con Python, creamos un espacio de trabajo, instalamos las herramientas, copiamos el código, declaramos un puerto y finalmente, definimos cómo encender la aplicación.
2.  **Confirma que Cumpliste los Requisitos:**
    - [x] ¿Usa una imagen base de Python?
    - [x] ¿Copia el código de `/src`?
    - [x] ¿Instala desde `requirements.txt`?
    - [x] ¿Expone el puerto y ejecuta `uvicorn`?

¡Felicidades! Has escrito tu primer "manual de infraestructura como código". Este simple archivo de texto es uno de los artefactos más potentes en la ingeniería de software moderna. Ahora, estás listo para usarlo para construir tu primera imagen de Docker.