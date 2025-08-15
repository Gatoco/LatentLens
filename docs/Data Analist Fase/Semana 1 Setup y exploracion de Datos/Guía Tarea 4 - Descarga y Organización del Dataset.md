# 🏛️ Guía Paso a Paso: Tu Cuarta Tarea - Descargar y Organizar el Dataset

[[First month]]

## Introducción: Consiguiendo Nuestros Datos

Todo proyecto de ciencia de datos comienza con datos. Para nuestro sistema de recomendación, usaremos **MovieLens 25M**, un dataset clásico y respetado en la comunidad académica y de la industria. Fue creado por el laboratorio de investigación **GroupLens** de la Universidad de Minnesota.

Contiene 25 millones de calificaciones de películas, dadas por 162,000 usuarios a 62,000 películas. Es lo suficientemente grande y complejo como para construir un sistema robusto y significativo.

Nuestro objetivo en esta tarea es simple: descargar estos datos de su fuente oficial y colocarlos de forma ordenada dentro de la carpeta `/data` que preparamos, asegurándonos de que Git los ignore correctamente.

---

## 🚦 Pre-vuelo: Checklist de Requisitos

Antes de empezar, asegúrate de tener esto listo:
*   [x] **1. La Carpeta `/data` Existe:** Confirma que tienes una carpeta llamada `data` en la raíz de tu proyecto `LatentLens`.
*   [x] **2. `.gitignore` está Configurado:** Verifica que tu archivo `.gitignore` contiene la línea `data/`. Esto es **CRUCIAL**.

---

## ✅ Checklist de Ejecución: De la Web a tu Proyecto

Sigue estos pasos en orden.

### **Fase 1: Descargar el Dataset**

*   [x] **1. Navega a la Fuente Oficial:** Abre tu navegador y ve a la página de GroupLens para el dataset.
    *   **Enlace directo:** [https://grouplens.org/datasets/movielens/25m/](https://grouplens.org/datasets/movielens/25m/)
*   [x] **2. Inicia la Descarga:**
    *   Busca el archivo de descarga, que se llama `ml-25m.zip`.
    *   Haz clic en él para comenzar a descargar.
    *   **Aviso:** Es un archivo grande (alrededor de 240 MB comprimido), así que dale tiempo para que se complete la descarga. Generalmente se guardará en tu carpeta de "Descargas".

### **Fase 2: Descomprimir y Organizar los Archivos**

El archivo que descargaste está comprimido en un `.zip`. Necesitamos extraer su contenido.

*   [x] **1. Encuentra el Archivo Descargado:** Ve a tu carpeta de "Descargas" y localiza el archivo `ml-25m.zip`.
*   [x] **2. Descomprime el Archivo:**
    *   **En Windows:** Haz clic derecho sobre `ml-25m.zip` y selecciona `Extraer todo...` (o `Extract All...`). Te preguntará dónde guardarlo, puedes dejar la ubicación por defecto por ahora.
    *   **En macOS:** Simplemente haz doble clic en el archivo `ml-25m.zip`.
    *   Una vez descomprimido, tendrás una nueva carpeta llamada `ml-25m`.
*   [x] **3. Coloca los Datos en tu Proyecto (El Paso Clave):**
    *   Ahora, **corta** o **mueve** la carpeta `ml-25m` que acabas de extraer.
    *   Navega a la carpeta de tu proyecto `LatentLens`.
    *   Entra en la carpeta `/data`.
    *   **Pega** la carpeta `ml-25m` aquí dentro.
    *   La estructura final debe ser: `LatentLens/data/ml-25m/`.

---

## Verificación Final

Esta es la parte más importante. Vamos a asegurarnos de que todo esté en su lugar y de que Git esté ignorando los datos como le pedimos.

*   [x] **1. Verificación Visual de la Estructura:**
    *   Dentro de la carpeta `LatentLens/data/`, ahora deberías ver una sola carpeta: `ml-25m`.
    *   Dentro de `LatentLens/data/ml-25m/`, deberías ver varios archivos, incluyendo `movies.csv`, `ratings.csv`, y `tags.csv`. ¡Estos son nuestros datos!
*   [x] **2. Verificación de Git (La Prueba de Fuego):**
    *   Abre tu terminal y asegúrate de estar en la raíz de tu proyecto `LatentLens`.
    *   Ejecuta el siguiente comando:
      ```bash
      git status
      ```
    *   **El resultado esperado es:**
      ```
      On branch main
      Your branch is up to date with 'origin/main'.

      nothing to commit, working tree clean
      ```
    *   **Análisis:** Si la terminal te dice "nothing to commit, working tree clean", significa que Git **NO** está viendo los nuevos archivos de datos. **¡Esto es un ÉXITO TOTAL!** Significa que tu archivo `.gitignore` está funcionando a la perfección, manteniendo tu repositorio limpio y ligero.

## Conclusión

¡Felicidades! Has completado una tarea fundamental. Ya no solo tienes la estructura de un proyecto, sino que ahora tienes los datos, las materias primas con las que empezarás a construir. Tu taller está listo y los materiales están en su sitio.

El siguiente paso es la parte más emocionante: abrir nuestro laboratorio (`Jupyter Notebook`) y empezar a explorar estos 25 millones de calificaciones.