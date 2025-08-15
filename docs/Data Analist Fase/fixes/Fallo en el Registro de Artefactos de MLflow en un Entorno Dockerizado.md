# 🏛️ Post-mortem Técnico: Fallo en el Registro de Artefactos de MLflow en un Entorno Dockerizado

**Etiquetas:** #mlops #docker #mlflow #post-mortem #debugging #docker-volumes #client-server

## Resumen Ejecutivo

Durante el despliegue de la pila de MLOps (`MLflow` + `FastAPI`) a través de `Docker Compose`, se encontró un fallo persistente y silencioso en el registro de artefactos del modelo. Aunque las métricas y los parámetros se registraban correctamente, los artefactos no aparecían en la UI de MLflow. Un análisis forense reveló que la causa raíz no era un único error, sino una cascada de problemas sistémicos derivados de una arquitectura de seguimiento incorrecta para un entorno contenedorizado heterogéneo (host Windows, contenedor Linux). La solución requirió una refactorización de la arquitectura de seguimiento de un modelo de sistema de archivos compartido (`file://...`) a un modelo cliente-servidor puro (`http://...`), además de resolver incompatibilidades de versiones y condiciones de carrera en la inicialización de servicios.

---

## 1. Descripción del Problema Inicial

- **Síntoma Principal:** La ejecución de `mlflow.pyfunc.log_model` desde un notebook de Jupyter se completaba sin lanzar excepciones. Sin embargo, la sección de "Artifacts" para el "run" correspondiente en la UI de MLflow permanecía vacía.
- **Síntomas Secundarios:** En fases de depuración anteriores, la UI de MLflow devolvía errores genéricos `500 Internal Server Error`, y los logs del contenedor revelaban errores `TypeError` relacionados con metadatos de "run" corruptos.

---

## 2. Metodología de Diagnóstico y Análisis de Causa Raíz (RCA)

El diagnóstico se realizó mediante la desarticulación sistemática del problema en tres fases, cada una revelando una capa más profunda del fallo.

### Fase 1: Error de Conectividad de Red (`ConnectionRefusedError`)

- **Análisis:** La traza inicial de errores mostró una `ConnectionRefusedError` explícita al intentar ejecutar `mlflow.set_experiment()`. El cliente de MLflow no podía establecer una conexión TCP con el servidor en `localhost:5000`.
- **Causa Raíz Identificada:** Violación del orden de operaciones requerido para un sistema distribuido. El cliente (notebook) se ejecutaba antes de que la pila de `docker-compose` hubiera inicializado completamente y vinculado el puerto del servicio `mlflow-ui`.
- **Lección Técnica:** La inicialización de servicios en `docker-compose` no es instantánea. Un flujo de trabajo robusto debe garantizar que los servicios del backend estén en un estado `HEALTHY` o `LISTENING` antes de que los clientes intenten comunicarse con ellos.

### Fase 2: Corrupción de Estado y Conflicto de Versiones (`TypeError: missing run_uuid`)

- **Análisis:** Una vez corregido el orden de operaciones, la conexión se establecía, pero la UI del servidor fallaba con un `500 Internal Server Error`. El `traceback` del contenedor `mlflow-ui` indicaba un `TypeError` fatal: `RunInfo.__init__() missing 1 required positional argument: 'run_uuid'`.
- **Causa Raíz Identificada:** Incompatibilidad de esquema entre la versión de la librería de `mlflow` utilizada por el cliente (v3.x) y la versión de la imagen de Docker del servidor de `mlflow` (v2.x). La versión más reciente del cliente serializaba los metadatos del "run" con un campo `run_id`, mientras que el servidor más antiguo esperaba un campo `run_uuid`. Un solo archivo `meta.yaml` con el esquema incorrecto era suficiente para hacer que el `FileStore` del servidor fallara en su totalidad.
- **Lección Técnica:** La paridad de versiones (o, como mínimo, la compatibilidad garantizada) entre los componentes de cliente y servidor de una misma herramienta es un prerrequisito para la estabilidad del sistema.

### Fase 3: Falla de Sincronización de Volumen (`Bind Mount`)

- **Análisis:** Tras alinear las versiones y confirmar mediante inspección manual del sistema de archivos (`ls -la`) que el notebook SÍ escribía los artefactos correctamente en el directorio `./mlruns` del host, la UI de MLflow seguía sin mostrarlos.
- **Causa Raíz Identificada:** Fallo en la capa de virtualización del sistema de archivos de Docker. El "bind mount" que mapea el directorio del host (`./mlruns`) al directorio del contenedor (`/mlruns`) no estaba sincronizando los archivos correctamente. Esto suele deberse a complejos problemas de permisos entre el sistema de archivos NTFS del host de Windows y el sistema de archivos POSIX del contenedor de Linux, especialmente en lo que respecta a la propiedad de los archivos (`UID`/`GID`).
- **Lección Técnica:** Los "bind mounts" en entornos de desarrollo heterogéneos (Windows-Linux) son inherentemente frágiles. Si bien son útiles, introducen una fuerte dependencia del comportamiento y la configuración de Docker Desktop.

---

## 3. Solución Arquitectónica Implementada

Se determinó que la causa fundamental de todos los problemas era el **diseño arquitectónico original**, que trataba al sistema de archivos local (`./mlruns`) como una base de datos compartida. Esto creaba un acoplamiento indebido y era la fuente de todos los conflictos. La solución fue refactorizar a una **arquitectura cliente-servidor estricta**.

1.  **Reconfiguración del Cliente (`tracking_uri`):** El notebook fue modificado para dejar de usar un `tracking_uri` basado en archivos (`file://...`). En su lugar, se configuró para apuntar directamente al endpoint HTTP del servidor.
    ```python
    mlflow.set_tracking_uri("http://localhost:5000")
    ```
2.  **Aislamiento de la Responsabilidad de Escritura:** En esta nueva arquitectura, el cliente del notebook **nunca escribe directamente en `./mlruns`**. Su única responsabilidad es enviar los datos (parámetros, métricas y el payload binario de los artefactos) al servidor a través de la API REST de MLflow.
3.  **Centralización de la Persistencia:** El servidor de MLflow (corriendo dentro de Docker) se convierte en la **única entidad autorizada para escribir** en el sistema de archivos. Recibe los datos del cliente a través de la red y los persiste en su propio directorio `/mlruns`, que a su vez está mapeado de vuelta al host a través del `volume`.

---

## 4. Conclusión y Lección de Ingeniería Senior

La cascada de fallos fue el resultado directo de violar un principio de diseño clave para sistemas distribuidos: la **separación de incumbencias (`Separation of Concerns`)**. Al tratar el sistema de archivos como una base de datos compartida, se creó una dependencia frágil y compleja entre el host y el contenedor.

La transición a una arquitectura cliente-servidor pura, donde la comunicación se produce exclusivamente a través de una API de red bien definida, elimina esta clase de problemas por diseño. El sistema resultante es más robusto, predecible y menos dependiente de la configuración del entorno del host, alineándose con las mejores prácticas para sistemas de MLOps en producción. El `Traceback` final (`ConnectionRefusedError` vs. `500 Internal Server Error`) fue la pieza de diagnóstico clave que permitió diferenciar entre un problema de disponibilidad de red y un problema de estado corrupto, guiando la solución final.