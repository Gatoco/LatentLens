# 📖 Diccionario Técnico: Mes 2 - Profundización y Modelos Híbridos
[[Second month]]

---

### Semana 5: Métricas de Ranking y Contenido

#### **`Métricas de Ranking`**
- **Qué es:** Un tipo de métrica de evaluación que, a diferencia de RMSE, no mide el error de predicción de la calificación, sino la **calidad del orden** de los ítems recomendados. Mide qué tan buenos son los "top K" resultados que le muestras al usuario.
- **Por qué es Importante:** Un usuario nunca verá las miles de predicciones de tu modelo; solo le importan las 10 primeras que le muestras. Estas métricas evalúan precisamente esa experiencia del usuario, que es lo más importante en un sistema de recomendación.
- **Analogía:** Si buscas en Google, no te importa si la página correcta está en el resultado 5,897,241. Te importa si está en los primeros 5. Las métricas de ranking miden qué tan bien "posiciona" Google los resultados relevantes al principio.

#### **`Precision@k`**
- **Qué es:** De los "k" ítems que recomendaste, ¿qué fracción fue relevante para el usuario? (Ej: Si recomiendas 10 películas (k=10) y al usuario le gustaron 3 de ellas, la Precision@10 es 30%).
- **Por qué es Importante:** Mide directamente la tasa de aciertos de tu lista de recomendaciones. Es muy fácil de entender e interpretar.
- **Analogía:** Eres un cazador de talentos y le presentas a un director 10 actores (k=10) para un papel. Si el director considera que 2 de ellos son adecuados, tu precisión fue del 20%.

#### **`Recall@k`**
- **Qué es:** De todos los ítems que hubieran sido relevantes para el usuario, ¿qué fracción lograste "atrapar" en tu lista de "k" recomendaciones?
- **Por qué es Importante:** Mide la capacidad de tu modelo para encontrar todos los ítems relevantes. Es un balance con la precisión. A veces quieres encontrar "todo" lo bueno, aunque incluyas algunas recomendaciones no tan buenas.
- **Analogía:** En el mar hay 50 peces que valen la pena (total de ítems relevantes). Lanzas una red y atrapas 10 peces (k=10). De esos 10, 5 son de los valiosos. Tu recall es 5/50 = 10%. Atrapaste el 10% de todo lo bueno que había.

#### **`MAP@k (Mean Average Precision at k)`**
- **Qué es:** Una métrica más sofisticada que la Precision@k porque **toma en cuenta el orden** de los resultados. Le da más peso a los aciertos que aparecen en las primeras posiciones de la lista.
- **Por qué es Importante:** Es una de las métricas estándar para evaluar sistemas de recomendación y búsqueda porque penaliza a los modelos que ponen los resultados buenos al final de la lista.
- **Analogía:** Es mejor que tu restaurante favorito aparezca como el resultado #1 de la búsqueda, no como el #9. MAP@k te da más "puntos" por el acierto en la posición #1 que por el de la posición #9.

#### **`Modelo Basado en Contenido (Content-Based)`**
- **Qué es:** Un tipo de sistema de recomendación que sugiere ítems basándose en sus propiedades o atributos. Recomienda ítems similares a los que a un usuario le han gustado en el pasado.
- **Por qué es Importante:** No depende de otros usuarios, por lo que puede recomendar ítems nuevos o poco populares (resuelve parte del "cold start") y puede dar explicaciones lógicas ("Te recomiendo esta película porque comparte el género de 'Ciencia Ficción' y al director de otra que te gustó").
- **Analogía:** Un librero que te recomienda un libro porque es del mismo autor o del mismo género de misterio que el último que compraste.

#### **`TF-IDF Vectorizer`**
- **Qué es:** Una técnica para convertir texto en un conjunto de números (un vector) que una máquina puede entender. Asigna un "peso" o importancia a cada palabra. Se compone de:
    - **TF (Term Frequency):** ¿Qué tan frecuente es una palabra en un documento?
    - **IDF (Inverse Document Frequency):** ¿Qué tan rara o común es esa palabra en todos los documentos?
- **Por qué es Importante:** Es el método clásico para cuantificar texto. Da una alta importancia a las palabras que son frecuentes en un documento específico pero raras en general, identificando así las palabras que mejor lo describen.
- **Analogía:** La palabra "motor" es muy frecuente en el manual de un auto (alto TF), pero no tan común en todos los libros del mundo (alto IDF), por lo que "motor" es una palabra muy descriptiva para ese manual y obtiene un alto peso TF-IDF.

#### **`Similitud del Coseno (Cosine Similarity)`**
- **Qué es:** Una métrica matemática que mide la similitud entre dos vectores. En nuestro caso, mide qué tan parecidas son dos películas basándose en sus vectores TF-IDF. Un valor de 1 significa que son idénticos, 0 que no tienen nada en común.
- **Por qué es Importante:** Es la herramienta matemática que te permite comparar las películas una vez que las has convertido en números con TF-IDF. Es la base del recomendador por contenido.
- **Analogía:** Mide el ángulo entre dos flechas que apuntan en diferentes direcciones. Si las dos flechas apuntan exactamente en la misma dirección (ángulo de 0°), son muy similares (similitud del coseno = 1).

---

### Semana 6: Modelo Híbrido y "Cold Start"

#### **`Modelo Híbrido`**
- **Qué es:** Un sistema de recomendación que combina dos o más técnicas diferentes (en tu caso, Filtrado Colaborativo + Basado en Contenido).
- **Por qué es Importante:** Permite aprovechar las fortalezas de cada técnica y mitigar sus debilidades, generalmente resultando en un sistema más robusto y preciso que cualquiera de los modelos por sí solo.
- **Analogía:** Un detective que no solo se basa en las pistas de la escena del crimen (contenido), sino que también entrevista a los testigos para saber qué hicieron otras personas (colaborativo).

#### **`Re-rankear (Re-ranking)`**
- **Qué es:** El proceso de tomar una lista de resultados (posiblemente de varias fuentes) y reordenarla según un nuevo criterio o una combinación de puntuaciones.
- **Por qué es Importante:** Es una estrategia común en los modelos híbridos. Puedes generar una lista larga de candidatos y luego usar un modelo más fino o una lógica de negocio para ordenarlos de la manera más óptima para el usuario.
- **Analogía:** Tienes dos listas de "mejores restaurantes", una de un crítico gastronómico y otra de un amigo. Combinas ambas listas y luego las reordenas poniendo primero los restaurantes que aparecen en ambas.

#### **`Cold Start (Arranque en Frío)`**
- **Qué es:** El problema que ocurre cuando el sistema no tiene suficientes datos para hacer recomendaciones a un usuario o sobre un ítem. Existen dos tipos:
    - **Cold Start de Usuario:** Un nuevo usuario se registra y no tiene historial de calificaciones.
    - **Cold Start de Ítem:** Una nueva película se añade al catálogo y nadie la ha calificado aún.
- **Por qué es Importante:** Todos los sistemas del mundo real deben enfrentar este problema. Un mal manejo del "cold start" puede frustrar a nuevos usuarios y hacer que abandonen la plataforma.
- **Analogía:** Intentar recomendarle un regalo a un completo desconocido (usuario nuevo) o intentar vender un producto completamente nuevo que nadie conoce (ítem nuevo).

---

### Semana 7: Configuración y Pruebas

#### **`Externalizar Configuración (.py / .yaml)`**
- **Qué es:** La práctica de sacar parámetros y valores "mágicos" (como el número de recomendaciones `k=10`, rutas de archivos, etc.) de tu código principal y ponerlos en un archivo separado. `.yaml` es un formato de archivo muy popular para esto por ser muy legible para los humanos.
- **Por qué es Importante:** Permite cambiar el comportamiento de tu aplicación sin modificar el código fuente. Facilita la configuración para diferentes entornos (desarrollo, producción) y hace el código más limpio y mantenible.
- **Analogía:** El panel de configuración de una aplicación. No necesitas ser un programador para cambiar el idioma o el brillo; simplemente ajustas las opciones en el menú.

#### **`FastAPI.TestClient`**
- **Qué es:** Una herramienta que viene con FastAPI y te permite escribir tests para tu API simulando peticiones HTTP (como las que haría un navegador) directamente en tu código Python, sin necesidad de levantar un servidor real.
- **Por qué es Importante:** Te permite automatizar las pruebas de tus endpoints, asegurando que tu API funciona correctamente y sigue devolviendo los resultados esperados cada vez que haces un cambio.
- **Analogía:** Un robot de control de calidad que automáticamente "llama" a tu mesero (API) y verifica que cada plato del menú que pide llega correctamente y con los ingredientes esperados.

---

### Semana 8: Limpieza y Documentación

#### **`Linter (flake8)`**
- **Qué es:** Una herramienta que analiza tu código fuente para encontrar errores de programación, bugs, errores estilísticos y constructos sospechosos. `flake8` es una combinación de varias herramientas de chequeo para Python.
- **Por qué es Importante:** Impone un estándar de calidad y consistencia en el código. Es como tener un supervisor de código automático que te ayuda a escribir de forma más limpia y profesional.
- **Analogía:** Un editor de estilo para un periódico que se asegura de que todos los artículos sigan la misma guía de estilo, gramática y formato.