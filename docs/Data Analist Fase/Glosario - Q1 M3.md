# 📖 Diccionario Técnico: Mes 3 - Producción y Cierre

---

### Semana 9: Automatización del Entrenamiento (Pipeline)

#### **`Pipeline de Entrenamiento`**
- **Qué es:** Un script (como `train.py`) que orquesta y ejecuta todos los pasos necesarios para entrenar y evaluar un modelo de forma automática y en una secuencia definida (cargar datos -> preprocesar -> entrenar -> evaluar -> guardar).
- **Por qué es Importante:** Elimina la necesidad de ejecutar celdas de un notebook manualmente. Asegura que el proceso de entrenamiento sea **100% reproducible** y pueda ser ejecutado por cualquier persona (o máquina) con un solo comando. Es el primer paso para la automatización seria.
- **Analogía:** Una línea de ensamblaje en una fábrica. En lugar de construir un auto a mano moviendo las piezas de un lado a otro (como en un notebook), creas una cadena de montaje donde cada estación hace su parte en el orden correcto, produciendo un resultado consistente siempre.

#### **`Artefactos (Artifacts)`**
- **Qué es:** Los archivos de salida que produce tu pipeline de entrenamiento. No es solo el modelo entrenado (`.pkl` o `.joblib`), sino también archivos con las métricas (`results.json`), gráficos de evaluación (`confusion_matrix.png`), etc.
- **Por qué es Importante:** Son la evidencia tangible de un experimento. MLflow se especializa en almacenar y organizar estos artefactos para que puedas comparar no solo una métrica, sino todos los resultados de diferentes "runs".
- **Analogía:** Cuando un auto sale de la línea de ensamblaje, los artefactos no son solo el auto en sí, sino también el informe de inspección de calidad, las fotos de la prueba de choque y el manual de usuario.

#### **`DVC (Data Version Control)`**
- **Qué es:** Una herramienta de control de versiones diseñada para la ciencia de datos. Funciona junto con Git. Mientras Git versiona tu **código**, DVC versiona tus **datos** y **modelos** (que suelen ser archivos muy grandes y no deben ir en Git).
- **Por qué es Importante:** Permite una reproducibilidad total. Con Git+DVC, puedes viajar en el tiempo y recrear un experimento exactamente como era, con la misma versión del código, de los datos y del modelo.
- **Analogía:** Git es el recetario que registra cada cambio en las instrucciones. DVC es un sistema de inventario para tus ingredientes (datos). No guarda el saco de 50kg de harina dentro del libro de recetas, pero registra "para esta versión de la receta, se usó el lote #1234 de harina".

#### **`workflow_dispatch`**
- **Qué es:** Un tipo de evento en GitHub Actions que te permite disparar un workflow (flujo de trabajo) **manualmente** desde la interfaz de GitHub, haciendo clic en un botón.
- **Por qué es Importante:** Es ideal para tareas que no quieres que se ejecuten en cada `push`, como un re-entrenamiento completo del modelo, que puede ser lento y costoso. Te da control para decidir cuándo ejecutarlo.
- **Analogía:** Una máquina que tiene un modo automático pero también un gran botón rojo para que un operador la pueda encender y ejecutar un ciclo completo cuando lo considere necesario.

---

### Semana 10: Despliegue Continuo (CD) y Monitoreo

#### **`Registro de Contenedores (Container Registry)`**
- **Qué es:** Un servicio de almacenamiento y distribución para imágenes de Docker. Es un lugar centralizado donde guardas tus imágenes para que puedan ser descargadas y usadas en cualquier otro lugar (como un servidor en la nube). **Docker Hub** es el registro más conocido.
- **Por qué es Importante:** Es el puente entre tu máquina local y el mundo exterior. Para que otro sistema pueda ejecutar tu contenedor, primero debe poder descargarlo de un registro.
- **Analogía:** Un "App Store" o un "GitHub" pero para tus imágenes de Docker.

#### **`docker tag` y `docker push`**
- **`docker tag`:** El comando para darle un nombre o etiqueta a tu imagen de Docker en el formato `usuario/nombre-repositorio:version`. (Ej: `myusername/recommender-api:v1.0`).
- **`docker push`:** El comando que sube tu imagen etiquetada al registro de contenedores (como Docker Hub).
- **Por qué son Importantes:** Son los comandos operativos que te permiten interactuar con un registro. `tag` prepara la imagen para el envío y `push` la envía.
- **Analogía:** `tag` es como poner la dirección de envío y una etiqueta de "Frágil" en un paquete. `push` es llevar el paquete a la oficina de correos para enviarlo.

#### **`Despliegue Continuo (CD)`**
- **Qué es:** Es la extensión lógica de la Integración Continua (CI). Después de que el código es integrado y pasa todos los tests automáticamente (CI), el Despliegue Continuo **libera o despliega automáticamente** ese nuevo artefacto (en tu caso, la imagen de Docker).
- **Por qué es Importante:** Reduce drásticamente el tiempo y el esfuerzo para llevar nuevas versiones de tu software a los usuarios (o a un entorno de producción). Es el pináculo de la automatización en el ciclo de vida del software.
- **Analogía:** La línea de ensamblaje (CI) no solo construye y prueba el auto, sino que una vez aprobado, un robot lo conduce automáticamente fuera de la fábrica y lo aparca en el concesionario, listo para la venta (CD).

#### **`Logging`**
- **Qué es:** La práctica de registrar eventos, errores y otra información importante que ocurre mientras una aplicación se está ejecutando. Estos registros se guardan en archivos o se envían a un sistema de monitoreo.
- **Por qué es Importante:** Es fundamental para la depuración y el monitoreo. Cuando tu aplicación falle en producción a las 3 AM, no podrás conectar un debugger. Tu única herramienta para entender qué pasó serán los logs que dejaste.
- **Analogía:** La caja negra de un avión. Registra todo lo que ocurre durante el "vuelo" de tu aplicación para que, si se "estrella", puedas investigar la causa.

#### **`stdout (Salida Estándar)`**
- **Qué es:** El flujo de salida de datos por defecto en un sistema operativo. En términos simples, es donde se imprime el texto que ves en tu terminal. Docker captura este `stdout` de los contenedores.
- **Por qué es Importante:** Es la forma más simple y estándar de hacer logging en aplicaciones modernas y contenerizadas. En lugar de escribir a un archivo (lo que puede ser complicado dentro de un contenedor), simplemente imprimes a la consola y dejas que la plataforma (Docker) se encargue de recolectar esos logs.
- **Analogía:** Un micrófono en un escenario. El cantante (tu aplicación) simplemente canta (imprime a `stdout`), y el sistema de sonido del teatro (Docker) se encarga de recogerlo y enviarlo a los altavoces (los logs).

#### **`GitHub Secrets` y `Variables de Entorno`**
- **`GitHub Secrets`:** Un lugar seguro en la configuración de tu repositorio de GitHub para almacenar información sensible como contraseñas, tokens o claves de API.
- **`Variables de Entorno`:** Variables que se definen fuera del código de tu aplicación y que son accesibles desde dentro de ella. Son el mecanismo para pasar los GitHub Secrets a tu aplicación de forma segura.
- **Por qué son Importantes:** **NUNCA** debes escribir contraseñas o claves directamente en tu código (hardcoding). Es una vulnerabilidad de seguridad gravísima. Este mecanismo te permite mantener tu código limpio de secretos y configurar tu aplicación de forma segura.
- **Analogía:** Tienes una carta muy importante (tu aplicación). En lugar de escribir tu número de cuenta bancaria (el secreto) dentro de la carta, la dejas en una caja fuerte (GitHub Secrets). Le das una llave especial (la Variable de Entorno) al cartero (GitHub Actions) que le permite abrir la caja fuerte y darle el número al destinatario justo cuando lo necesita, sin que quede escrito en la carta.