# 🏛️ Guía Tarea 12: La Cámara Hiperbárica - Tu Primer Test Unitario con Pytest

[[Week 4: CI/CD Básico y Refinamiento]]

## 1. Contexto Técnico: De la Confianza a la Certeza Verificable

Hasta la fecha, la validación del sistema se ha realizado a nivel macro (métricas de modelo, endpoints de API funcionales). Esta tarea introduce el concepto de **testing unitario**, una disciplina fundamental de la ingeniería de software para garantizar la corrección a nivel micro.

Un **test unitario** aísla la unidad de lógica más pequeña posible —una única función— de sus dependencias externas (sistemas de archivos, bases de datos, APIs) y verifica su comportamiento contra un conjunto de aserciones predefinidas. El objetivo es confirmar que para una entrada `X` conocida, la función produce de forma determinista una salida `Y` esperada.

La creación de una suite de tests unitarios robusta es un prerrequisito indispensable para la automatización segura (CI/CD) y el refactoring a largo plazo del código base.

---

## 2. Prerrequisitos de Infraestructura

- [x] **1. Entorno Virtual Activo:** Confirme que el prompt de la terminal está prefijado con `(venv)`.
- [x] **2. Instalación del Framework de Pruebas:** `pytest` es el framework estándar de facto en el ecosistema de Python. Proceda con su instalación.
      ```bash
      pip install pytest
      ```

---

## 3. Protocolo de Ejecución

### Fase 3.1: Refactoring para la Testeabilidad

El código acoplado a dependencias externas (I/O) es inherentemente difícil de testear unitariamente. Por lo tanto, el primer paso es refactorizar para aislar una función pura.

- [x] **1. Crear Módulo de Preprocesamiento:**
    - [x] Dentro del directorio `/src`, cree un nuevo archivo: `preprocessing.py`.
- [x] **2. Implementar Función Pura:** Inserte el siguiente código en `/src/preprocessing.py`. Esta función no tiene efectos secundarios y su salida depende únicamente de su entrada.

    ```python
    import re

    def clean_movie_title(title: str) -> str:
        """
        Aísla el título de una película eliminando el año de lanzamiento
        y el espacio en blanco circundante. Es una función determinista
        y sin estado, ideal para el testing unitario.

        Ejemplo: 'Toy Story (1995) ' -> 'Toy Story'
        
        Args:
            title (str): El título crudo de la película.

        Returns:
            str: El título procesado.
        """
        # Expresión regular para encontrar un año entre paréntesis y los espacios asociados
        title_no_year = re.sub(r'\s*\([^)]*\)', '', title)
        # Eliminación de espacios en blanco al inicio o al final
        cleaned_title = title_no_year.strip()
        return cleaned_title
    ```

### Fase 3.2: Establecimiento de la Infraestructura de Pruebas

`pytest` opera basado en convenciones de nomenclatura para el descubrimiento automático de tests.

- [x] **1. Crear Directorio de Tests:** En el directorio **raíz del proyecto** (`LatentLens/`), cree una nueva carpeta llamada `tests`.
- [x] **2. Crear Archivo de Test:** Dentro del nuevo directorio `tests`, cree un nuevo archivo llamado `test_preprocessing.py`. El prefijo `test_` es mandatorio para el descubrimiento de `pytest`.

### Fase 3.3: Implementación de Casos de Prueba

Se utilizará el patrón estándar **Arrange-Act-Assert (AAA)** para estructurar los tests, garantizando su legibilidad y mantenibilidad.

- [x] **1. Implementar el Archivo de Test:** Inserte el siguiente código en `/tests/test_preprocessing.py`.

    ```python
    # Importar la unidad bajo prueba (Unit Under Test - UUT)
    from src.preprocessing import clean_movie_title

    def test_clean_title_standard_case():
        """
        Caso de Prueba 1: Verifica el comportamiento estándar.
        - Objetivo: Confirmar la eliminación del año y el espacio en blanco.
        - Entrada: Un título con año y paréntesis.
        - Salida Esperada: El título sin el año.
        """
        # 1. Arrange: Definición de las condiciones de entrada y el resultado esperado.
        input_title = "Forrest Gump (1994)"
        expected_output = "Forrest Gump"
        
        # 2. Act: Ejecución de la unidad bajo prueba.
        actual_output = clean_movie_title(input_title)
        
        # 3. Assert: Aserción de que el resultado actual es igual al esperado.
        # Si esta condición es falsa, el test falla.
        assert actual_output == expected_output

    def test_clean_title_no_year_case():
        """
        Caso de Prueba 2: Verifica el caso borde.
        - Objetivo: Confirmar que la función es idempotente para títulos ya limpios.
        - Entrada: Un título sin año.
        - Salida Esperada: El mismo título de entrada.
        """
        # 1. Arrange
        input_title = "Pulp Fiction"
        expected_output = "Pulp Fiction"
        
        # 2. Act
        actual_output = clean_movie_title(input_title)
        
        # 3. Assert
        assert actual_output == expected_output
    ```

### Fase 3.4: Ejecución de la Suite de Tests

- [x] **1. Posición de la Terminal:** Asegúrese de que su terminal se encuentra en el directorio **raíz del proyecto** (`LatentLens/`).
- [x] **2. Lanzar el "Test Runner":** Ejecute el comando de `pytest`.
      ```bash
      pytest
      ```
- [x] **3. Análisis del Resultado:** La salida del "test runner" debe indicar que todos los casos de prueba han pasado.
      ```
      ============================= test session starts ==============================
      ...
      collected 2 items

      tests/test_preprocessing.py ..                                           [100%]

      ============================== 2 passed in ...s ===============================
      ```

---

## 4. Verificación de Criterios de Éxito

- [ ] **Refactoring Completado:** Se ha creado y poblado un nuevo módulo, `src/preprocessing.py`, mejorando la cohesión y reduciendo el acoplamiento.
- [ ] **Infraestructura de Tests Creada:** Existe una estructura de directorios `tests/` con un archivo `test_*.py` que sigue las convenciones estándar.
- [ ] **Tests Unitarios Funcionales:** La ejecución de `pytest` resulta en un estado de "éxito" (`passed`), verificando empíricamente la corrección de la función `clean_movie_title`.

Se ha establecido la base del control de calidad automatizado. Este artefacto (`tests/`) es un prerrequisito para la siguiente fase: Integración Continua (CI).