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