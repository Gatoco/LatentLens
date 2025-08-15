# 🏛️ Guía Paso a Paso: Tu Tercera Tarea - Activar el Entorno e Instalar Librerías
[[First month]]

## Introducción: ¿Qué Significa "Activar" un Entorno?

En la tarea anterior, creamos una carpeta `venv`. Piensa en ella como una "cocina" separada y vacía, exclusiva para nuestro proyecto `LatentLens`.

**Activar el entorno** es el acto de **"entrar a esa cocina"**. Mientras el entorno esté activo, todo lo que instalemos se guardará dentro de esa "cocina" (`venv`) y no en la "cocina principal" de nuestra casa (nuestra instalación global de Python). Esto es lo que garantiza que nuestro proyecto sea autónomo y reproducible.

Una vez "dentro", instalaremos nuestro kit de herramientas inicial:
*   **`pandas`**: El "Excel" de Python. La herramienta fundamental para cargar, manipular y limpiar datos tabulares.
*   **`numpy`**: La calculadora científica. Proporciona la base para operaciones matemáticas y de álgebra lineal a alta velocidad.
*   **`jupyter`**: Nuestro laboratorio interactivo. Nos permite escribir y ejecutar código en bloques, visualizar resultados al instante y documentar nuestro proceso de pensamiento.
*   **`matplotlib` & `seaborn`**: Nuestros pinceles y lienzos. Son las librerías que usaremos para crear todo tipo de gráficos y visualizaciones para entender nuestros datos.

---

## ✅ Checklist de Ejecución: Equipando Nuestro Taller de Datos

Sigue estos pasos en orden.

### **Fase 1: Activar el Entorno Virtual**

Este es el paso más importante. El comando es diferente para Windows y para macOS/Linux.

*   [x] **1. Abre la Terminal:** Asegúrate de que estás en la raíz de tu proyecto `LatentLens`.
*   [x] **2. Ejecuta el Comando de Activación:**

    *   **Si estás en Windows (usando CMD o PowerShell):**
        ```bash
        .\venv\Scripts\activate
        ```
    *   **Si estás en macOS o Linux:**
        ```bash
        source venv/bin/activate
        ```
*   [x] **3. Verifica la Activación (¡El Momento Clave!):**
    *   Mira tu prompt en la terminal (la línea donde escribes los comandos). Debería haber cambiado y ahora tener un **`(venv)`** al principio.
    *   Se verá algo así: `(venv) C:\Users\Gat\Documents\GitHub\LatentLens>`
    *   **Si ves el prefijo `(venv)`, ¡lo has logrado!** Ahora estás trabajando dentro de tu entorno aislado.

### **Fase 2: Instalar las Librerías con `pip`**

`pip` es el gestor de paquetes de Python, nuestro "instalador de herramientas".

*   [x] **1. Ejecuta el Comando de Instalación:** Con el entorno aún activo, escribe el siguiente comando para instalar todas las librerías de una sola vez:
    ```bash
    pip install pandas numpy jupyter matplotlib seaborn
    ```
*   [x] **2. Observa la Salida:** Verás cómo la terminal empieza a descargar e instalar cada paquete y sus dependencias. Esto puede tardar unos minutos. ¡Ten paciencia! Es una señal de que está funcionando.

### **Fase 3: Crear el "Manifiesto" del Entorno (`requirements.txt`)**

Ahora que hemos instalado nuestras herramientas, debemos crear una lista exacta de lo que usamos para que otros (o nosotros en el futuro) puedan replicar este entorno perfectamente.

*   [x] **1. Genera la Lista:** Con el entorno todavía activo, ejecuta este comando:
    ```bash
    pip freeze > requirements.txt
    ```
    - **Análisis:** `pip freeze` es un comando que lista todos los paquetes instalados en el entorno actual junto con sus versiones exactas. El símbolo `>` le dice a la terminal que en lugar de mostrar esa lista en la pantalla, la guarde en un nuevo archivo llamado `requirements.txt`.
*   [x] **2. Inspecciona el Archivo:** Abre el nuevo archivo `requirements.txt` en tu editor. Verás la lista de librerías que acabamos de instalar (y sus dependencias) con sus números de versión. ¡Esta es la huella digital de tu entorno!

### **Fase 4: Sincronización con GitHub**

El `requirements.txt` es una pieza fundamental del código de tu proyecto, así que debe estar en GitHub.

*   [x] **1. Añade los Cambios:** Prepara el nuevo archivo para el "commit".
      ```bash
      git add requirements.txt
      ```
      *(También puedes usar `git add .` para añadir todos los archivos nuevos o modificados de una vez).*
*   [x] **2. Crea el "Commit":**
      ```bash
      git commit -m "feat: install initial dependencies and create requirements.txt"
      ```
*   [x] **3. Sube los Cambios a GitHub:**
      ```bash
      git push
      ```

---

## Verificación Final

1.  En tu terminal, asegúrate de que el prefijo `(venv)` sigue activo.
2.  Ve a tu repositorio en **GitHub.com** y actualiza la página.
3.  Busca y haz clic en el nuevo archivo `requirements.txt`.
4.  Dentro del archivo, deberías ver la lista de librerías como `pandas==2.1.4`, `numpy==1.26.2`, etc. (tus versiones pueden ser ligeramente diferentes).

¡Felicidades! Has activado con éxito tu entorno, lo has equipado con las herramientas esenciales de un científico de datos y, lo más importante, has creado un "manifiesto" que hace que tu proyecto sea profesional y reproducible. Ya estás listo para empezar a trabajar con los datos.