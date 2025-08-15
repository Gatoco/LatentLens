# 🏛️ Guía Tarea 11: Del 'Qué' al 'Porqué' - Implementando SVD para Descubrir el ADN de las Películas

[[First month]]

## Introducción: Graduándose a los Factores Latentes

Hemos validado nuestros modelos con métricas y hemos construido una infraestructura de producción robusta. Ahora es el momento de implementar formalmente el modelo avanzado que elegimos por su eficiencia y poder: la Descomposición en Valores Singulares (SVD). Ya lo usamos para resolver una crisis de memoria; ahora lo adoptaremos como el cerebro principal de `LatentLens` por su capacidad superior para descubrir los patrones ocultos en los gustos de los usuarios.

Esta guía formalizará el código de experimentación que ya hemos perfeccionado, asegurando que nuestro modelo campeón sea tratado con el rigor que se merece y completando así uno de los hitos más importantes de nuestro `Roadmap`.

---

## 🚦 Pre-vuelo: Checklist de Requisitos

- [x] **1. El Flujo de Trabajo Profesional Establecido:** Confirma que tu notebook `05-MLflow-Experiment-Tracking.ipynb` está estructurado en dos celdas: la Celda 1 para el `Mise en Place` (carga de datos) y la Celda 2 para la experimentación. Este es nuestro estándar de oro.
- [x] **2. Un Escenario Limpio (Protocolo "Tierra Quemada"):** Para asegurar que este "experimento oficial" no se contamine con pruebas anteriores, sigue meticulosamente este protocolo:
    - [x] Ve a tu terminal y asegúrate de que ningún servicio de Docker esté corriendo. Si es así, detén el proceso (`Ctrl + C`).
    - [x] Ejecuta el comando de demolición total para eliminar contenedores y volúmenes antiguos:
          ```bash
          docker-compose down -v
          ```
    - [x] Borra la carpeta `mlruns` de la raíz de tu proyecto para empezar con una biblioteca de experimentos completamente limpia. Puedes hacerlo desde el explorador de archivos o con el comando en la terminal.

---

## ✅ Checklist de Ejecución: La Coronación del Modelo SVD

### **Fase 1: Preparar el Laboratorio (El `Mise en Place`)**

- [x] **1. Abre tu Notebook `05-MLflow-Experiment-Tracking.ipynb`**.
- [x] **2. Ejecuta la Celda 1 (Preparación de Datos):** No necesitamos cambiar nada en esta celda. Nuestra lógica de carga y división de datos es robusta y reutilizable.
    - [x] Simplemente ejecuta esta celda una vez.
    - [x] Espera a que termine. El mensaje `¡Mise en Place completado!...` confirmará que las variables `trainset` y `testset` están listas en la memoria del Kernel.

### **Fase 2: Ejecutar el Experimento Campeón y Desplegar la Infraestructura**

- [x] **1. Ve a la Celda 2 (Experimento):** Esta celda contiene nuestro código de grado producción. Es el resultado de todas nuestras batallas de depuración.
- [x] **2. Revisa y Confirma los Hiperparámetros:** Antes de ejecutar, echa un último vistazo a los valores dentro de la celda. Basado en nuestros hallazgos, `n_factors: 150` y `n_epochs: 20` son una configuración campeona.
    - [x] Confirma que estás usando el `run_name` que deseas para esta ejecución formal. Por ejemplo: `SVD_PRODUCTION_READY_FINAL_V2`.
- [x] **3. Ejecuta la Celda 2 (Experimento):** Lanza la ejecución de entrenamiento y registro.
    - [x] Observa la salida. Debería ser limpia, sin errores, y mostrar los mensajes de `INFO` de MLflow validando la firma.
    - [x] Al finalizar, una nueva y prístina carpeta `mlruns` habrá sido creada con el resultado de este experimento.
- [x] **4. Lanza la Orquesta:** Una vez que el notebook haya terminado, ve a tu terminal (en la raíz del proyecto) y levanta todo el sistema con un solo comando:
      ```bash
      docker-compose up
      ```

### **Fase 3: La Auditoría Final del Campeón en la UI**

- [x] **1. Inspecciona la Telemetría en la UI de MLflow:**
    - [x] Abre tu navegador. **No uses una pestaña antigua o un marcador.**
    - [x] Escribe la dirección a mano: `http://localhost:5000`.
    - [x] Navega hasta tu último "run", identificado por el `run_name` que usaste.
- [x] **2. Realiza la Verificación de Calidad:**
    - [x] **Verifica los Artefactos:** Ve a la pestaña `Artifacts`. Confirma que la carpeta `surprise_svd_model` está presente, indicando que el modelo se guardó correctamente.
    - [ ] **Verifica la Firma:** En la pestaña `Overview`, dsplázate hacia abajo y confirma que la `Model Signature` está visible y define correctamente las columnas de entrada (`userId`, `movieId`) y la salida (`double`).
    - [ ] **Verifica los Parámetros y Métricas:** Confirma que los valores de `n_factors` y `rmse` en la UI coinciden con los de la salida de tu notebook.

---

## Verificación Final

1.  **Modelo Entrenado y Registrado:** Has ejecutado con éxito un experimento SVD, y su resultado completo (métrica, parámetros y el propio modelo como artefacto) está guardado de forma segura y auditable en MLflow.
2.  **Infraestructura Desplegada:** Tu comando `docker-compose up` ha levantado exitosamente tanto la UI de MLflow (que muestra la evidencia de tu trabajo) como la API de FastAPI.
3.  **Sistema Cohesionado:** Tu API, al arrancar, ha cargado automáticamente el modelo que acabas de registrar desde el volumen compartido de `mlruns`. El ciclo está completo.
4.  **(Bonus) Prueba de la API:** Ve a `http://localhost:8000/docs`, prueba el endpoint `/recommend/{user_id}` con un ID como `1` y confirma que obtienes una lista de recomendaciones.

¡Felicidades! Has completado formalmente el hito del "Modelo Avanzado". Tu sistema `LatentLens` ahora no solo tiene una infraestructura robusta, sino que su cerebro es un algoritmo de recomendación potente, probado y desplegado.