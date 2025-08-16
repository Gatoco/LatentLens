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