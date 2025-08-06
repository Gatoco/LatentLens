# LatentLens: Un Sistema Híbrido de Recomendación de Películas

Este proyecto es un sistema de recomendación de películas de punta a punta, diseñado para ir más allá de los algoritmos básicos y construir una solución robusta y desplegable. El objetivo es explorar técnicas de filtrado colaborativo y basado en contenido, empaquetar el sistema en una API y prepararlo para producción.

---

## 🎯 El Problema: La Paradoja de la Elección

En la era del streaming, nos enfrentamos a catálogos con decenas de miles de películas. Esta abundancia, en lugar de ser una ventaja, a menudo conduce a la "parálisis por análisis", donde un usuario pasa más tiempo buscando qué ver que disfrutando del contenido.

Un sistema de recomendación genérico que solo sugiere las películas más populares falla en capturar los gustos únicos de cada individuo. El verdadero desafío es construir un sistema que se sienta personal, como un amigo experto en cine que te conoce perfectamente y te recomienda esa joya oculta que te encantará.

El objetivo de `LatentLens` es precisamente ese: analizar el comportamiento del usuario y las características de las películas para ofrecer recomendaciones personalizadas, relevantes y que fomenten el descubrimiento.

## 📊 El Dataset: MovieLens 25M

Para entrenar nuestro sistema, utilizamos el prestigioso dataset **MovieLens 25M**, una fuente de datos estándar en la investigación de sistemas de recomendación, curada por el laboratorio GroupLens de la Universidad de Minnesota.

Este dataset es ideal para nuestro propósito debido a su escala y riqueza. Contiene:

*   **25,000,095** calificaciones.
*   **162,541** usuarios.
*   **62,423** películas.
*   Un rango temporal que abarca desde **Enero de 1995** hasta **Noviembre de 2019**.

Los datos principales se encuentran en dos archivos:

1.  **`ratings.csv`**: Contiene la información central de las interacciones, con las columnas `userId`, `movieId`, `rating` y `timestamp`.
2.  **`movies.csv`**: Actúa como nuestro diccionario de películas, mapeando cada `movieId` a su `title` y `genres`.

El Análisis Exploratorio de Datos (EDA) inicial reveló hallazgos clave que guiarán nuestro diseño, como la fuerte escasez de datos para un 42% del catálogo y el comportamiento distinto entre usuarios casuales y "power users".

---

## 🚀 Arquitectura del Sistema (En Desarrollo)
*Próximamente se detallará la arquitectura técnica del proyecto.*

## ⚙️ Cómo Ejecutarlo Localmente (En Desarrollo)
*Próximamente se añadirán las instrucciones para levantar el sistema usando Docker.*