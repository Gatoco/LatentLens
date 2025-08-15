# 🎯 Q1-M2: Sistema de Recomendación - Sprint de Profundización (Mes 2)

**Objetivo del Mes:** Evolucionar de un modelo simple a un sistema híbrido, mejorar significativamente las métricas de evaluación y enriquecer la API para manejar escenarios del mundo real.

---

## 📌 Semana 5: Métricas de Ranking y Contenido

*   [ ] **Métricas:** Dejar de usar solo RMSE. Investigar e implementar métricas de ranking que son más apropiadas para la recomendación.
    *   [ ] Escribir una función para calcular **Precision@k** y **Recall@k**.
    *   [ ] (Bonus) Investigar y tratar de implementar **MAP@k** (Mean Average Precision at k).
*   [ ] **MLflow:** Registrar las nuevas métricas de ranking para tus modelos existentes (Baseline y SVD) en MLflow. Ahora podrás comparar no solo el error, sino la calidad del ranking.
*   [ ] **Modelo (Basado en Contenido):** Iniciar la parte de contenido del sistema.
    *   [ ] Usar los datos de `movies.csv`. Combinar el `title` y los `genres`.
    *   [ ] Crear una matriz de características de texto usando **TF-IDF Vectorizer** de Scikit-learn sobre los géneros/títulos.
    *   [ ] Calcular la similitud del coseno entre todas las películas para encontrar las más parecidas.
*   [ ] **API:** Crear un nuevo endpoint `/similar/{movie_id}` que devuelva las 10 películas más similares basadas en contenido (usando la matriz de similitud del coseno).
*   [ ] **Retrospectiva Semanal:** Anotar: ¿Por qué las métricas de ranking son más útiles aquí? ¿Qué limitaciones tiene el enfoque basado en contenido?

---

## 📌 Semana 6: Modelo Híbrido y el Problema del "Cold Start"

*   [ ] **Modelo (Híbrido):** Diseñar e implementar una estrategia para combinar tu modelo de filtrado colaborativo (SVD) con tu modelo basado en contenido.
    *   **Estrategia simple:** Para un usuario dado, genera 20 recomendaciones con SVD y 20 con contenido (basado en las películas que le han gustado). Combina y re-rankea los resultados.
*   [ ] **"Cold Start":** Manejar explícitamente el problema del "arranque en frío".
    *   [ ] **Nuevos Usuarios:** ¿Qué le recomiendas a un usuario sin calificaciones? Implementa una lógica en la API que, si el usuario es nuevo, le devuelva las películas más populares o mejor calificadas.
    *   [ ] **Nuevas Películas:** Asegúrate de que tu sistema no ignore películas que aún no han recibido calificaciones (el modelo basado en contenido ayuda aquí).
*   [ ] **Código:** Refactorizar la lógica de recomendación en `/src` para que sea más limpia. Crea una clase `Recommender` que encapsule los diferentes modelos.
*   [ ] **MLflow:** Registrar el rendimiento (con todas las métricas) de tu nuevo modelo híbrido. ¿Supera a los modelos individuales?
*   [ ] **Retrospectiva Semanal:** Anotar: ¿Qué estrategia de hibridación usaste y por qué? ¿Qué otras estrategias existen?

---

## 📌 Semana 7: Configuración, Pruebas y API Avanzada

*   [ ] **Configuración:** Externalizar las configuraciones "mágicas" de tu código.
    *   [ ] Crear un archivo `config.py` o un `.yaml` donde definas parámetros como el `k` de las recomendaciones, las rutas a los modelos guardados, etc. Esto evita tener números hardcodeados en el código.
*   [ ] **Pruebas (Testing):** Ampliar la cobertura de tests en `/tests`.
    *   [ ] Escribir tests para la API: simula llamadas a tus endpoints (`/recommend`, `/similar`) y verifica que devuelven un código de estado 200 y un JSON con el formato esperado. Usa `pytest` con `FastAPI.TestClient`.
    *   [ ] Escribir un test para el caso de "cold start" (un usuario que no existe).
*   [ ] **CI/CD:** Asegurarte de que tus nuevos tests se ejecutan automáticamente en el workflow de GitHub Actions.
*   [ ] **API (Mejora):** Hacer que la respuesta de la API sea más útil. En lugar de solo devolver `movie_id`, haz que devuelva también el `title` y los `genres` de la película, realizando un "join" con el dataframe de películas.
*   [ ] **Retrospectiva Semanal:** Anotar: ¿Por qué es importante separar la configuración del código? ¿Qué fue lo más difícil de testear?

---

## 📌 Semana 8: Limpieza Final y Documentación del Proyecto

*   [ ] **Documentación (README):** Realizar una actualización masiva del `README.md`.
    *   [ ] Añadir una sección detallada de "Metodología", explicando los diferentes modelos que probaste (colaborativo, contenido, híbrido).
    *   [ ] Incluir una tabla con los resultados finales de cada modelo según tus métricas (RMSE, Precision@k, etc.), sacados de MLflow.
    *   [ ] Añadir una sección de "Uso de la API" con ejemplos de cómo llamar a cada endpoint.
    *   [ ] (Bonus) Crear un GIF o un video corto mostrando cómo funciona la API (puedes usar la documentación interactiva de FastAPI en el navegador) e incrústalo en el README.
*   [ ] **Código:** Realizar una limpieza final del código.
    *   [ ] Eliminar todos los notebooks "de prueba" o limpiarlos para que solo quede el de EDA final.
    *   [ ] Revisar todo el código de `/src` para asegurar que sigue los estándares de estilo (puedes usar un linter como `flake8`).
    *   [ ] Asegurarse de que el `requirements.txt` esté actualizado y no contenga librerías innecesarias.
*   [ ] **Presentación:** Preparar un borrador de la presentación del proyecto (como se discutió en las recomendaciones). ¿Cómo le explicarías este proyecto a un reclutador en 5 minutos?
*   [ ] **Retrospectiva Mensual:** Evaluar el proyecto finalizado. ¿Alcanzaste la métrica de `Precisión > 85%` (o la métrica que hayas definido como principal)? ¿Qué harías diferente si empezaras de nuevo?