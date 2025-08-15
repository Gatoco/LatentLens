# 🗺️ Centro de Comando: Fase 1 (Analista → Científico de Datos)

**Misión:** Transformarme de un analista de datos junior a un científico de datos listo para el mercado laboral en 16 meses, a través de la ejecución disciplinada de proyectos prácticos y la construcción de un portafolio de nivel profesional.

---

> ## 🔥 Cómo Mantener la Constancia y no Abandonar
>
> **Tu plan es una maratón, no un sprint. El agotamiento es el enemigo principal. Estas son tus defensas:**
>
> 1.  **La Regla de los Dos Días:** Jamás permitas que pasen dos días seguidos sin tocar tu proyecto. ¿Tuviste un día terrible y no estudiaste? Está bien. Mañana es innegociable. Incluso 25 minutos (un Pomodoro) son suficientes para mantener la inercia y la identidad de "alguien que estudia todos los días".
>
> 2.  **Visualiza el Progreso, no solo la Meta:** La meta de "ser un Full-Stack Data Master" es lejana. La meta de "terminar el pipeline de CI/CD esta semana" es tangible. Usa tu plan para enfocarte en las victorias semanales y mensuales. Cada vez que terminas un mes, mira hacia atrás y reconoce conscientemente todo lo que has construido.
>
> 3.  **Perdona y Adapta:** Habrá semanas en las que no cumplas tus objetivos por exámenes, vida personal o simple cansancio. No te castigues. El plan es una guía, no una cárcel. Realiza tu retrospectiva dominical, entiende por qué te desviaste, ajusta el plan para la siguiente semana y sigue adelante. La resiliencia vale más que la perfección.
>
> 4.  **Tu Entorno es Clave:** Prepara tu espacio (físico y digital) para que empezar a estudiar requiera la menor fricción posible. Ten tu aplicación de Pomodoro lista, tu editor de código abierto y tu nota de Obsidian a un clic de distancia. Cierra las pestañas y notificaciones que no necesites.
>
> 5.  **Celebra las Pequeñas Victorias:** ¿Terminaste de dockerizar la aplicación? Eso no es un paso más, es un hito. Prémiate con algo que disfrutes. Asociar el esfuerzo con una recompensa refuerza el hábito a nivel neurológico.

---

## 🚀 Cronograma de Proyectos Trimestrales

| Trimestre | Proyecto | Dataset/Herramientas | Métrica Clave | Enfoque Principal |
| :--- | :--- | :--- | :--- | :--- |
| **Q1 (Actual)** | **Sistema de Recomendación** | MovieLens 25M, Scikit-learn | Precisión > 85% | Fundamentos de ML + Docker & CI/CD |
| **Q2** | **Predicción de Fraudes** | IEEE-CIS Fraud Detection | AUC-ROC > 0.87 | Datos Desbalanceados, Feature Engineering |
| **Q3** | **Clasificación Médica** | NIH Chest X-Ray Dataset | F1-score > 0.85 | Deep Learning, Visión por Computador |
| **Q4** | **Optimización Logística** | OpenStreetMap, OR-Tools | Reducción 15% rutas | Investigación de Operaciones, Grafos |

---
---

## 🎯 Trimestre 1: Sistema de Recomendación de Películas

**Meta del Trimestre:** Construir un sistema de recomendación híbrido de punta a punta, empaquetado como una API reproducible y desplegable automáticamente.

### **Mes 1: Fundamentos y Despliegue Inicial** [[First month]]

El foco de este mes es sentar las bases. El objetivo es pasar de un entorno vacío a un primer modelo funcional dentro de un contenedor Docker. Iniciarás configurando un repositorio profesional y un entorno de trabajo limpio. Realizarás un Análisis Exploratorio de Datos (EDA) para entender el dataset. Luego, implementarás un modelo baseline simple (como SVD) para tener un punto de partida, lo expondrás a través de una API con FastAPI y lo dockerizarás, finalizando el mes con un workflow básico de CI/CD que ejecute tests.

### **Mes 2: Profundización y Calidad del Modelo** [[Second month]]

Este mes se dedica a refinar la calidad de la recomendación y abordar problemas del mundo real. Dejarás atrás métricas simples como el RMSE para adoptar métricas de ranking (Precision@k, MAP@k), que miden mejor la calidad de una lista de recomendaciones. Desarrollarás un segundo modelo basado en contenido (usando TF-IDF) y lo combinarás con el primero para crear un sistema híbrido, resolviendo así el problema del "cold start" para nuevos usuarios y películas.

### **Mes 3: Profesionalización y Cierre** [[Third month]]

El último mes del trimestre se enfoca en convertir el proyecto en una pieza de portafolio de élite. Automatizarás todo el pipeline de entrenamiento en un único script, que será ejecutado por un workflow de GitHub Actions. Configurarás el Despliegue Continuo (CD) para que cada nueva versión del código se suba automáticamente a un registro de contenedores como Docker Hub. Finalmente, te concentrarás en la comunicación: puliendo la documentación, creando una presentación profesional y preparándote para explicar el valor técnico y de negocio de tu trabajo.

---

## ⏳ Trimestre 2: Predicción de Fraudes (Meses 4-6)

**Objetivo:** Desarrollar un modelo de clasificación de alto rendimiento para datos tabulares masivos y desbalanceados, prestando especial atención a la ingeniería de características y la interpretabilidad del modelo.
*   **Enfoque:** Este proyecto te enseñará a lidiar con las complejidades de los datos del mundo real. El foco estará en la **ingeniería de características (feature engineering)** para extraer señales útiles de datos ruidosos, y en técnicas para manejar el **desbalance de clases**. Aprenderás a usar herramientas de interpretabilidad como SHAP para explicar las predicciones del modelo, una habilidad crucial en dominios de alto riesgo como las finanzas.

---

## ⏳ Trimestre 3: Clasificación Diagnóstica Médica (Meses 7-9)

**Objetivo:** Entrar en el mundo de Deep Learning y la visión por computador, aplicando Transfer Learning para clasificar imágenes médicas y utilizando técnicas de visualización para entender las decisiones del modelo.
*   **Enfoque:** Aquí darás el salto de los datos tabulares a los no estructurados (imágenes). El núcleo del proyecto será el **Transfer Learning**, utilizando redes neuronales pre-entrenadas (como EfficientNet) y ajustándolas a tu problema. Una parte clave será implementar técnicas como **Grad-CAM** para visualizar qué partes de la imagen está usando el modelo para decidir, asegurando que está aprendiendo características médicas relevantes.

---

## ⏳ Trimestre 4: Optimización Logística con Grafos (Meses 10-12)

**Objetivo:** Resolver un problema de negocio complejo del mundo real utilizando investigación de operaciones y teoría de grafos, aplicando la solución a datos geográficos de Chile.
*   **Enfoque:** Este proyecto te diferenciará del resto. Irás más allá del Machine Learning predictivo para entrar en el **ML prescriptivo** (que recomienda acciones). Utilizarás librerías como **OR-Tools** para resolver problemas de optimización, como el Ruteo de Vehículos (VRP), añadiendo restricciones realistas (ventanas de tiempo, capacidad). La aplicación a datos chilenos le dará un toque final de relevancia y practicidad.