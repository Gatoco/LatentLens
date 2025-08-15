# 📖 Diccionario Técnico: Mes 1 - Sistema de Recomendación
[[First month]]
Esta es una guía de los conceptos y tecnologías clave que encontrarás durante el primer mes. Úsala para entender no solo el "qué", sino el "porqué" de cada paso.

---

### Semana 1: Setup y Exploración de Datos (EDA)

#### **`Repositorio en GitHub`**
- **Qué es:** Una carpeta de proyecto cuyo historial de cambios está gestionado por el sistema de control de versiones **Git**. **GitHub** es la plataforma en la nube donde alojas esa carpeta para colaborar y mantener un respaldo.
- **Por qué es Importante:** Es el estándar de la industria para trabajar en software. Te permite guardar versiones de tu código, retroceder si cometes un error y, fundamentalmente, mostrar tu trabajo a reclutadores.
- **Analogía:** Un "Google Docs mágico" para tu código. Cada cambio queda registrado y puedes ver quién cambió qué y cuándo.

#### **`.gitignore`**
- **Qué es:** Un archivo de texto que le dice a Git qué archivos o carpetas debe ignorar y no incluir en el historial de cambios.
- **Por qué es Importante:** Evita que subas archivos innecesarios, pesados o privados a tu repositorio (como los datos mismos, archivos de configuración personal, credenciales, etc.), manteniéndolo limpio y profesional.
- **Analogía:** Una lista de "cosas que no quieres meter en la maleta" antes de un viaje.

#### **`Entorno Virtual (venv / conda)`**
- **Qué es:** Un directorio aislado que contiene una versión específica de Python y un conjunto de librerías específicas para un proyecto.
- **Por qué es Importante:** Evita conflictos de versiones. Tu proyecto A puede necesitar la librería X en su versión 1.0, mientras que el proyecto B necesita la versión 2.0. Los entornos virtuales aseguran que cada proyecto tenga exactamente lo que necesita sin interferir con los demás. Es la base de la **reproducibilidad**.
- **Analogía:** Una cocina separada y perfectamente equipada para cada receta que preparas. Nunca mezclas los ingredientes.

#### **`Análisis Exploratorio de Datos (EDA)`**
- **Qué es:** El proceso de investigar un dataset para resumir sus características principales, a menudo con visualizaciones y estadísticas. Es el primer paso antes de aplicar cualquier modelo.
- **Por qué es Importante:** Te permite entender la "personalidad" de tus datos. ¿Hay valores faltantes? ¿Hay datos extraños (outliers)? ¿Cómo se distribuyen? Sin EDA, estarías construyendo un modelo a ciegas.
- **Analogía:** Lo que hace un chef antes de cocinar: oler, tocar y probar los ingredientes para saber con qué está trabajando.

#### **`README.md`**
- **Qué es:** Un archivo de texto escrito en formato Markdown (`.md`) que sirve como la página de inicio o el manual de instrucciones de tu repositorio.
- **Por qué es Importante:** Es lo primero que verá cualquiera que visite tu proyecto. Un buen README explica qué hace el proyecto, por qué es útil y cómo ejecutarlo. Es tu carta de presentación.
- **Analogía:** La portada, el índice y el resumen de un libro.

---

### Semana 2: Primer Modelo Baseline y API

#### **`Modularizar Código`**
- **Qué es:** La práctica de organizar el código en archivos y funciones separadas y reutilizables, en lugar de tener todo en un solo script largo o notebook.
- **Por qué es Importante:** Hace que tu código sea más fácil de leer, de testear y de mantener. Es un principio fundamental de la ingeniería de software que te diferencia de un simple analista.
- **Analogía:** Crear bloques de Lego (funciones) que puedes usar para construir muchas cosas diferentes, en lugar de una sola escultura gigante e inmodificable.

#### **`Modelo Baseline`**
- **Qué es:** Un modelo muy simple y rápido de implementar que sirve como punto de referencia para medir el rendimiento de modelos más complejos.
- **Por qué es Importante:** Te da un "suelo" de rendimiento. Si tu modelo avanzado y sofisticado no supera al baseline, sabes que algo anda mal o que el problema es más simple de lo que pensabas.
- **Analogía:** La puntuación mínima que debes superar en un videojuego para que tu esfuerzo haya valido la pena.

#### **`Filtrado Colaborativo`**
- **Qué es:** Una técnica de recomendación que se basa en la idea de que si a la persona A le gusta lo mismo que a la persona B, entonces a A probablemente le gustará otras cosas que a B le gustan. Se basa en el comportamiento colectivo de los usuarios.
- **Por qué es Importante:** Es uno de los métodos más potentes y clásicos de la recomendación, la base de sistemas como los de Netflix y Amazon.
- **Analogía:** El principio de "dime con quién andas y te diré quién eres", pero aplicado a gustos y preferencias.

#### **`Métrica (RMSE)`**
- **Qué es:** Una métrica (Error Cuadrático Medio) usada para medir la diferencia promedio entre los valores predichos por el modelo y los valores reales.
- **Por qué es Importante:** Cuantifica qué tan "equivocado" está tu modelo. El RMSE penaliza más los errores grandes, lo cual es útil para saber si tu modelo está haciendo algunas predicciones terriblemente malas.
- **Analogía:** Una regla que mide la distancia promedio entre donde apuntaste y donde realmente aterrizó la flecha.

#### **`API (FastAPI)`**
- **Qué es:** Una Interfaz de Programación de Aplicaciones. Es un conjunto de reglas y herramientas que permite que diferentes programas de software se comuniquen entre sí. **FastAPI** es una librería de Python para construir estas interfaces de forma rápida y moderna.
- **Por qué es Importante:** Hace que tu modelo sea útil. En lugar de ser solo un script en tu PC, una API permite que otras aplicaciones (una página web, una app móvil) puedan "preguntarle" a tu modelo por una recomendación y obtener una respuesta.
- **Analogía:** Un mesero en un restaurante. Tú (el cliente/aplicación) no necesitas entrar a la cocina (el modelo), simplemente le haces un pedido (request) al mesero (API) y él te trae el plato (response).

#### **`Endpoint`**
- **Qué es:** Una URL específica dentro de una API a la que una aplicación puede hacer una petición para ejecutar una función particular.
- **Por qué es Importante:** Es la "puerta" a una funcionalidad específica de tu API. Puedes tener un endpoint para recomendaciones (`/recommend`) y otro para estado del sistema (`/health`).
- **Analogía:** Una opción específica en el menú del restaurante (ej: "Pedir el plato del día").

---

### Semana 3: Dockerización y Modelo Avanzado

#### **`Docker`**
- **Qué es:** Una plataforma que te permite empaquetar una aplicación con TODAS sus dependencias (código, librerías, sistema operativo, etc.) en una unidad estandarizada llamada **contenedor**.
- **Por qué es Importante:** Resuelve el clásico problema de "en mi máquina funciona". Un contenedor se ejecutará exactamente igual sin importar dónde lo despliegues (tu PC, el servidor de un colega, la nube). Es la clave de la **reproducibilidad** y el **despliegue moderno**.
- **Analogía:** Un tupperware perfectamente sellado que contiene un plato ya cocinado con todos sus ingredientes. Puedes llevarte ese tupperware a cualquier lugar y el plato estará exactamente igual.

#### **`Dockerfile` / `Imagen` / `Contenedor`**
- **`Dockerfile`:** El archivo de texto con las instrucciones paso a paso para construir el "paquete". **Analogía:** La receta.
- **`Imagen`:** El "paquete" construido y listo para ser ejecutado. Es un archivo estático. **Analogía:** El plato cocinado y listo, guardado en el refrigerador.
- **`Contenedor`:** Una instancia en ejecución de una imagen. Es el proceso vivo y activo. **Analogía:** El plato servido en la mesa, listo para comer.

#### **`Docker-Compose`**
- **Qué es:** Una herramienta para definir y ejecutar aplicaciones Docker que constan de múltiples contenedores (por ejemplo, tu API en un contenedor y una base de datos en otro).
- **Por qué es Importante:** Simplifica la gestión de arquitecturas complejas, permitiéndote levantar todo tu sistema con un solo comando.
- **Analogía:** El director de una orquesta que le dice a cada músico (contenedor) exactamente cuándo y cómo empezar a tocar.

#### **`Descomposición en Valores Singulares (SVD)`**
- **Qué es:** Una técnica de álgebra lineal para descomponer una matriz en partes más pequeñas. En Machine Learning, se usa para descubrir **factores latentes** (características ocultas) en los datos.
- **Por qué es Importante:** Es un modelo de filtrado colaborativo más avanzado. En lugar de solo comparar usuarios, SVD intenta entender los "gustos subyacentes". Por ejemplo, puede descubrir que a ciertos usuarios les gustan las películas con un alto "factor de acción" y un bajo "factor de comedia".
- **Analogía:** Descubrir el "ADN" de una película, descomponiéndola en sus componentes fundamentales (un 80% de acción, un 15% de ciencia ficción, un 5% de romance).

---

### Semana 4: CI/CD Básico y Refinamiento

#### **`Test Unitario (pytest)`**
- **Qué es:** Un fragmento de código que prueba una pequeña "unidad" aislada de tu código (generalmente una función) para asegurar que funciona como se espera. **Pytest** es una librería popular para escribir estos tests en Python.
- **Por qué es Importante:** Te da la confianza para hacer cambios en tu código. Si todos los tests pasan, sabes que no has roto ninguna funcionalidad existente. Es la red de seguridad de un desarrollador.
- **Analogía:** Probar que el motor de un auto funciona perfectamente antes de ensamblar el resto del vehículo.

#### **`CI/CD (Integración y Despliegue Continuo)`**
- **`CI (Integración Continua)`:** La práctica de fusionar automáticamente los cambios de código de todos los desarrolladores en un repositorio central, ejecutando tests automáticos en cada cambio. **Tu objetivo esta semana es el CI.**
- **`CD (Despliegue Continuo)`:** La práctica de desplegar automáticamente la aplicación en producción después de que pasa los tests de CI.
- **Por qué es Importante:** Automatiza el proceso de prueba y despliegue, haciéndolo más rápido, seguro y menos propenso a errores humanos. Es el núcleo de la filosofía MLOps y DevOps.
- **Analogía:** Una línea de ensamblaje automatizada. Cada vez que llega una nueva pieza (código), la línea la integra, la prueba y (en el caso de CD) la empaqueta para enviarla al cliente, todo sin intervención manual.

#### **`GitHub Actions`**
- **Qué es:** La herramienta de CI/CD integrada en GitHub. Te permite definir `workflows` (flujos de trabajo) que se ejecutan automáticamente en respuesta a eventos (como un `push` de código).
- **Por qué es Importante:** Es una forma increíblemente accesible y potente de empezar a implementar CI/CD para tus proyectos sin necesidad de servidores externos.
- **Analogía:** Los robots trabajadores en tu línea de ensamblaje automatizada.

#### **`Refactorizar`**
- **Qué es:** El proceso de reestructurar y mejorar el código existente sin cambiar su comportamiento externo.
- **Por qué es Importante:** Mejora la legibilidad, la eficiencia y la mantenibilidad del código. Es la diferencia entre un prototipo rápido y una pieza de software robusta y profesional.
- **Analogía:** Limpiar y organizar la cocina después de haber cocinado. No cambias la receta, pero la dejas lista y ordenada para la próxima vez que necesites usarla.