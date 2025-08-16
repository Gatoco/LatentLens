"""
Text Preprocessing Utilities for LatentLens

This module provides text processing functions for cleaning and normalizing
movie titles and other text data in the MovieLens dataset. All functions
are designed to be pure, deterministic, and easily testable.

Author: LatentLens Team
License: MIT
"""

import re
from typing import Optional


def extract_movie_title_without_year(movie_title_with_year: str) -> str:
    """
    Extract the clean movie title by removing the release year and extra whitespace.
    
    This function removes parenthetical year information (e.g., "(1995)") from
    movie titles and normalizes whitespace. It's designed to be deterministic
    and handle edge cases gracefully.
    
    Args:
        movie_title_with_year (str): The raw movie title that may contain
            release year in parentheses and extra whitespace.
            
    Returns:
        str: The cleaned movie title without year information.
        
    Examples:
        >>> extract_movie_title_without_year("Toy Story (1995)")
        'Toy Story'
        
        >>> extract_movie_title_without_year("Forrest Gump (1994) ")
        'Forrest Gump'
        
        >>> extract_movie_title_without_year("Pulp Fiction")
        'Pulp Fiction'
        
        >>> extract_movie_title_without_year("The Lord of the Rings: The Fellowship of the Ring (2001)")
        'The Lord of the Rings: The Fellowship of the Ring'
    
    Note:
        This function uses a regex pattern that matches any content within
        parentheses, not just years. This is intentional to handle edge cases
        where titles might have other parenthetical information.
    """
    # Remove any parenthetical content (typically years) and surrounding whitespace
    # Pattern explanation: \s* matches optional whitespace, \([^)]*\) matches parentheses and content
    title_without_parentheses = re.sub(r'\s*\([^)]*\)', '', movie_title_with_year)
    
    # Normalize whitespace: remove leading/trailing spaces and collapse multiple spaces
    normalized_title = ' '.join(title_without_parentheses.split())
    
    return normalized_title


def normalize_movie_title(raw_title: str) -> str:
    """
    Comprehensive movie title normalization.
    
    This function applies multiple normalization steps to ensure consistent
    title formatting across the dataset. Currently, it only removes years,
    but can be extended for other normalization needs.
    
    Args:
        raw_title (str): The original movie title from the dataset.
        
    Returns:
        str: The normalized movie title.
        
    Note:
        This function currently delegates to extract_movie_title_without_year
        but provides a logical extension point for additional normalization
        steps like handling special characters, case normalization, etc.
    """
    normalized_title = extract_movie_title_without_year(raw_title)
    return normalized_title


# Backward compatibility alias
# TODO: Consider deprecating this in favor of the more descriptive function name
clean_movie_title = extract_movie_title_without_year