# 🏛️ Guía Paso a Paso: Tu Primera Tarea - Estructura de Proyecto Profesional
[[First month]]

## Introducción: ¿Por Qué es Tan Importante Esta Tarea?

Antes de escribir una sola línea de código de análisis, debemos construir los **cimientos** de nuestro proyecto. Crear una estructura de carpetas profesional no es una formalidad, es una necesidad estratégica por cuatro razones clave:

1.  **Claridad Mental:** Separa las distintas partes de tu proyecto (datos, experimentos, código fuente, tests) para que siempre sepas dónde encontrar y guardar las cosas.
2.  **Reproducibilidad:** Facilita que otras personas (¡o tu "yo" del futuro!) entiendan tu trabajo y puedan ejecutarlo sin problemas.
3.  **Profesionalismo:** Es lo primero que un reclutador verá en tu GitHub. Una estructura organizada demuestra disciplina y que entiendes las convenciones de la industria.
4.  **Escalabilidad:** Esta estructura está diseñada para crecer. A medida que tu proyecto se vuelva más complejo, no se convertirá en un desorden.

Piensa que estás construyendo una casa. No empezarías a poner los muebles sin tener los planos y los cimientos bien definidos. Esto es exactamente lo que haremos ahora.

---

## El Significado de Cada Carpeta

Esta es la anatomía de un proyecto de ciencia de datos estándar:

*   `/data`: Aquí vivirán tus datos. Archivos CSV, JSON, etc. **Importante:** Esta carpeta casi nunca se sube a GitHub porque los datos suelen ser pesados o privados. Usaremos un truco para ignorarla. (.gitignore)
*   `/notebooks`: Tu laboratorio de experimentación. Aquí guardarás tus Jupyter Notebooks para el Análisis Exploratorio de Datos (EDA) y pruebas rápidas de modelos. Son tu "borrador" o "cuaderno de apuntes".
*   `/src` (source): El corazón de tu proyecto. Contiene el código Python "limpio" y reutilizable. Scripts, funciones y clases que hacen el trabajo pesado. Nada de experimentación aquí, solo código de calidad de producción.
*   `/tests`: Aquí se guardan los tests automáticos que verifican que tu código en `/src` funciona como se espera. Es tu red de seguridad.

---

## ✅ Checklist de Ejecución: De Cero a un Repositorio Profesional

Sigue estos pasos en orden.

### **Fase 1: Creación del Repositorio en GitHub**

El primer paso es crear el "hogar" de nuestro proyecto en la nube.

*   [x] **1. Ve a GitHub.com:** Inicia sesión y haz clic en el botón `New` (Nuevo) para crear un repositorio.
*   [x] **2. Nombra tu Repositorio:** Elige un nombre descriptivo y profesional. Por ejemplo: `movie-recommendation-system`.
*   [x] **3. Configuración Inicial (¡Muy Importante!):** Antes de hacer clic en "Create repository", asegúrate de marcar estas tres casillas:
    *   [x] **`Add a README file`:** Esto crea la "portada" de tu proyecto.
    *   [x] **`Add .gitignore`:** Haz clic en el menú desplegable y busca y selecciona **`Python`**. Esto le dirá a Git que ignore archivos temporales de Python.
    *   [x] **`Choose a license`:** Haz clic en el menú y elige una licencia. La **`MIT License`** es una excelente opción estándar para proyectos de portafolio, ya que es muy permisiva.
*   [x] **4. Crea el Repositorio:** Haz clic en el gran botón verde `Create repository`.

¡Felicidades! Ya tienes un repositorio profesional en la nube.

### **Fase 2: Clonación y Creación de la Estructura Local**

Ahora vamos a traer ese repositorio a tu computadora y a construir la estructura de carpetas.

*   [x] **1. Clona el Repositorio:**
    *   En la página de tu repositorio en GitHub, haz clic en el botón verde `<> Code`.
    *   Asegúrate de que la pestaña `HTTPS` esté seleccionada y copia la URL (termina en `.git`).
    *   Abre tu terminal (o Git Bash en Windows).
    *   Navega a la carpeta donde guardas tus proyectos (ej: `cd Desktop/Proyectos`).
    *   Escribe `git clone` y pega la URL que copiaste. Se verá así:
      ```bash
      git clone https://github.com/tu-usuario/movie-recommendation-system.git
      ```
*   [x] **2. Entra en la Carpeta del Proyecto:** Una vez que se complete la clonación, escribe en la terminal:
      ```bash
      cd movie-recommendation-system
      ```
*   [x] **3. Crea las Carpetas Profesionales:** Con un solo comando, podemos crear toda la estructura:
      ```bash
      mkdir data notebooks src tests
      ```
*   [x] **4. Crea Marcadores de Posición (Placeholder):** Git no rastrea carpetas vacías, así que crearemos un archivo oculto llamado `.gitkeep` dentro de cada una para forzar a Git a reconocerlas.
      ```bash
      touch data/.gitkeep notebooks/.gitkeep src/.gitkeep tests/.gitkeep
      ```

¡Perfecto! Ahora tienes la estructura de carpetas correcta en tu computadora.

### **Fase 3: Sincronización con GitHub**

El último paso es subir esta nueva estructura a tu repositorio en la nube para que todo esté sincronizado.

*   [x] **1. Añade los Cambios:** Este comando le dice a Git que prepare todos los nuevos archivos y carpetas para ser guardados en el historial.
      ```bash
      git add .
      ```
*   [x] **2. Crea un "Commit":** Un commit es una "foto" o un punto de guardado en el historial de tu proyecto. Siempre debe ir acompañado de un mensaje descriptivo.
      ```bash
      git commit -m "feat: setup initial project structure"
      ```
      *(Nota: `feat:` es una convención para indicar que estás añadiendo una nueva "feature" o característica. Es una excelente práctica.)*
*   [x] **3. Sube los Cambios a GitHub:** Este comando envía tu "commit" a la nube.
      ```bash
      git push
      ```

---

## Verificación Final

Ve a tu página del repositorio en GitHub y actualízala. Ahora deberías ver las carpetas `/data`, `/notebooks`, `/src` y `/tests` junto a tus archivos `README.md`, `.gitignore` y `LICENSE`.

**¡Felicidades!** Acabas de completar tu primera tarea. Has creado un esqueleto de proyecto robusto y profesional. Ahora tienes una base limpia y organizada sobre la cual empezar a construir tu sistema de recomendación.