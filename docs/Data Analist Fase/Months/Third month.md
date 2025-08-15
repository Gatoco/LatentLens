# 🎯 Q1-M3: Sistema de Recomendación - Sprint de Producción y Cierre (Mes 3)

**Objetivo del Mes:** Finalizar el proyecto con un enfoque en la automatización del despliegue (CD), la reproducibilidad total y la creación de una presentación de alto impacto que demuestre el valor de negocio y técnico.

---

## 📌 Semana 9: Automatización del Entrenamiento (Pipeline)

*   [ ] **Refactorización a Pipeline:** Convertir tu código de entrenamiento en un pipeline cohesivo.
    *   [ ] Crear un script principal, por ejemplo `train.py`, en la carpeta `/src`.
    *   [ ] Este script debe ejecutar todos los pasos en orden: cargar datos, preprocesar, entrenar el modelo (o modelos), evaluarlo con todas las métricas y guardar los artefactos resultantes (modelo serializado, métricas en un `.json`, etc.).
    *   [ ] El objetivo es que puedas re-entrenar todo tu sistema ejecutando un solo comando: `python src/train.py`.
*   [ ] **MLflow (Mejora):** Integrar el pipeline con MLflow para que el script `train.py` cree una nueva "run" y registre automáticamente todos los artefactos y métricas.
*   [ ] **DVC (Data Version Control - Opcional Avanzado):** Investigar DVC. Si te sientes con confianza, úsalo para versionar tu dataset y el output del modelo. Esto lleva la reproducibilidad a otro nivel. Si no, asegúrate de que tu README explique claramente de dónde vienen los datos.
*   [ ] **CI/CD (Pipeline de Entrenamiento):** Crear un **segundo** workflow de GitHub Actions que se pueda disparar manualmente (usando `workflow_dispatch`). Este workflow ejecutará el script `train.py` para demostrar que el entrenamiento es automatizable.
*   [ ] **Retrospectiva Semanal:** Anotar: ¿Cuál es la ventaja de tener un único script `train.py`? ¿Qué desafíos encontraste al automatizar el entrenamiento?

---

## 📌 Semana 10: Despliegue Continuo (CD) y Monitoreo

*   [ ] **Registro de Contenedores:** Aprender a subir tu imagen de Docker a un registro.
    *   [ ] Crear una cuenta en Docker Hub (gratuito).
    *   [ ] Aprender los comandos `docker tag` y `docker push` para subir tu imagen finalizada.
*   [ ] **CI/CD (Despliegue Continuo):** Mejorar tu workflow principal de GitHub Actions.
    *   [ ] Añadir un `job` que, solo si los tests pasan en la rama `main`, automáticamente suba la nueva versión de la imagen a Docker Hub. Esto es **Despliegue Continuo (CD)**.
*   [ ] **Monitoreo (Básico):** Simular un sistema de monitoreo simple.
    *   [ ] Añadir logging a tu API FastAPI. Registra cada vez que se llama al endpoint `/recommend`, incluyendo el `user_id` y el tiempo que tardó en responder.
    *   [ ] Escribe estos logs a la salida estándar (`stdout`), para que puedas verlos con `docker logs <container_id>`.
*   [ ] **Seguridad (Variables de Entorno):** Si tuvieras claves de API o contraseñas, no las dejes en el código. Aprende a usar **GitHub Secrets** para pasarlas de forma segura a tu workflow de CI/CD y como variables de entorno a tu contenedor Docker.
*   [ ] **Retrospectiva Semanal:** Anotar: ¿Qué es la diferencia entre CI y CD? ¿Por qué es importante el logging en una aplicación?

---

## 📌 Semana 11: Presentación y Comunicación del Proyecto

*   [ ] **Documentación Final:** Hacer la revisión final y pulido del `README.md`. Debe ser tan claro que otro desarrollador pueda entender y ejecutar tu proyecto en menos de 15 minutos.
*   [ ] **Crear Presentación:** Desarrollar una presentación corta (5-7 diapositivas) sobre tu proyecto.
    *   **Diapo 1: Título y Resumen:** ¿Qué es y qué hace? (Ej: "Sistema Híbrido de Recomendación de Películas con CI/CD").
    *   **Diapo 2: El Problema de Negocio:** ¿Por qué es importante la recomendación? (Mejorar engagement, etc.).
    *   **Diapo 3: Arquitectura y Tecnología:** Un diagrama simple mostrando (Datos -> Pipeline de Entrenamiento -> Modelo Guardado -> API Dockerizada -> Usuario Final) y las tecnologías usadas.
    *   **Diapo 4: Metodología y Resultados:** Explicar los modelos (colaborativo, contenido, híbrido) y mostrar la tabla de métricas finales.
    *   **Diapo 5: Demo:** Un GIF o un screenshot de la API en acción.
    *   **Diapo 6: Conclusiones y Próximos Pasos:** ¿Qué aprendiste? ¿Cómo podrías mejorar el proyecto en el futuro?
*   [ ] **Grábate a Ti Mismo:** Ensaya y graba tu presentación en 5 minutos. Mírala y critica tu propia claridad y confianza. Repite hasta que estés satisfecho.
*   [ ] **Escribir un Post (Borrador):** Escribir un borrador de un artículo para LinkedIn o un blog personal resumiendo el proyecto. Enfócalo en los desafíos y las soluciones.
*   [ ] **Retrospectiva Semanal:** Anotar: ¿Qué es lo más difícil de explicar de tu proyecto a alguien no técnico? ¿Cuál es el logro técnico del que te sientes más orgulloso?

---

## 📌 Semana 12: Cierre y Transición

*   [ ] **Limpieza Final del Repositorio:** Eliminar cualquier archivo innecesario, ramas de git antiguas, etc. El repositorio debe quedar en un estado "final" y profesional.
*   [ ] **Publicar:** Publicar el post que escribiste la semana pasada en LinkedIn. Enlázalo a tu repositorio de GitHub.
*   [ ] **Portafolio:** Añadir el proyecto a tu CV y a la sección de "proyectos destacados" de tu perfil de LinkedIn.
*   [ ] **Retrospectiva del Trimestre:** Realizar una retrospectiva completa de los 3 meses.
    *   [ ] ¿Qué salió bien? ¿Qué salió mal?
    *   [ ] ¿Cumpliste tus metas de aprendizaje y métricas?
    *   [ ] ¿Qué lecciones de este trimestre aplicarás al siguiente proyecto (Predicción de Fraudes)?
*   [ ] **Planificación Q2:** Empezar a investigar el próximo proyecto.
    *   [ ] Descargar el dataset de "IEEE-CIS Fraud Detection".
    *   [ ] Leer el `README` del dataset y hacer un primer EDA muy rápido para entender la escala y complejidad del desafío que viene.
*   [ ] **¡Descansar!** Tómate unos días libres antes de empezar el siguiente trimestre. El descanso planificado es clave para evitar el burnout y mantener la motivación a largo plazo.