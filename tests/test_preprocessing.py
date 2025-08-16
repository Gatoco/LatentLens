"""
Unit Tests for Text Preprocessing Module

This module contains comprehensive unit tests for the text preprocessing
functions in src.preprocessing. Tests follow the Arrange-Act-Assert pattern
and cover both standard use cases and edge cases.

Author: LatentLens Team
License: MIT
"""

import pytest
from src.preprocessing import clean_movie_title, extract_movie_title_without_year, normalize_movie_title


class TestMovieTitleCleaning:
    """Test suite for movie title cleaning functionality."""
    
    def test_extract_title_standard_case(self):
        """
        Test Case: Standard movie title with year in parentheses.
        
        Objective: Verify that the function correctly removes year information
        and surrounding whitespace from a typical movie title.
        
        Input: Movie title with year in standard format
        Expected Output: Clean title without year information
        """
        # Arrange: Set up test input and expected result
        input_movie_title = "Forrest Gump (1994)"
        expected_clean_title = "Forrest Gump"
        
        # Act: Execute the function under test
        actual_clean_title = extract_movie_title_without_year(input_movie_title)
        
        # Assert: Verify the result matches expectations
        assert actual_clean_title == expected_clean_title
    
    def test_extract_title_with_trailing_whitespace(self):
        """
        Test Case: Movie title with trailing whitespace after year.
        
        Objective: Ensure the function handles extra whitespace correctly.
        """
        # Arrange
        input_movie_title = "Toy Story (1995) "
        expected_clean_title = "Toy Story"
        
        # Act
        actual_clean_title = extract_movie_title_without_year(input_movie_title)
        
        # Assert
        assert actual_clean_title == expected_clean_title
    
    def test_extract_title_no_year_present(self):
        """
        Test Case: Movie title without year information.
        
        Objective: Verify that the function is idempotent for titles
        that don't contain year information.
        
        Input: Clean movie title without year
        Expected Output: Unchanged title
        """
        # Arrange
        input_movie_title = "Pulp Fiction"
        expected_clean_title = "Pulp Fiction"
        
        # Act
        actual_clean_title = extract_movie_title_without_year(input_movie_title)
        
        # Assert
        assert actual_clean_title == expected_clean_title
    
    def test_extract_title_complex_title_with_colons(self):
        """
        Test Case: Complex movie title with colons and year.
        
        Objective: Ensure the function works with complex titles
        containing special characters.
        """
        # Arrange
        input_movie_title = "The Lord of the Rings: The Fellowship of the Ring (2001)"
        expected_clean_title = "The Lord of the Rings: The Fellowship of the Ring"
        
        # Act
        actual_clean_title = extract_movie_title_without_year(input_movie_title)
        
        # Assert
        assert actual_clean_title == expected_clean_title
    
    def test_extract_title_multiple_parentheses(self):
        """
        Test Case: Title with multiple parenthetical information.
        
        Objective: Verify the function removes all parenthetical content,
        not just the last occurrence.
        """
        # Arrange
        input_movie_title = "Movie Title (Special Edition) (2000)"
        expected_clean_title = "Movie Title"
        
        # Act
        actual_clean_title = extract_movie_title_without_year(input_movie_title)
        
        # Assert
        assert actual_clean_title == expected_clean_title
    
    def test_backward_compatibility_clean_movie_title(self):
        """
        Test Case: Backward compatibility with old function name.
        
        Objective: Ensure the clean_movie_title alias still works correctly.
        """
        # Arrange
        input_movie_title = "The Matrix (1999)"
        expected_clean_title = "The Matrix"
        
        # Act
        actual_clean_title = clean_movie_title(input_movie_title)
        
        # Assert
        assert actual_clean_title == expected_clean_title
    
    def test_normalize_movie_title_function(self):
        """
        Test Case: Comprehensive normalization function.
        
        Objective: Verify that the normalize_movie_title function
        works correctly for standard cases.
        """
        # Arrange
        input_movie_title = "Star Wars (1977)"
        expected_normalized_title = "Star Wars"
        
        # Act
        actual_normalized_title = normalize_movie_title(input_movie_title)
        
        # Assert
        assert actual_normalized_title == expected_normalized_title


class TestEdgeCases:
    """Test suite for edge cases and error conditions."""
    
    def test_empty_string_input(self):
        """
        Test Case: Empty string input.
        
        Objective: Ensure the function handles empty strings gracefully.
        """
        # Arrange
        input_movie_title = ""
        expected_clean_title = ""
        
        # Act
        actual_clean_title = extract_movie_title_without_year(input_movie_title)
        
        # Assert
        assert actual_clean_title == expected_clean_title
    
    def test_only_whitespace_input(self):
        """
        Test Case: Input containing only whitespace.
        
        Objective: Verify proper handling of whitespace-only input.
        """
        # Arrange
        input_movie_title = "   "
        expected_clean_title = ""
        
        # Act
        actual_clean_title = extract_movie_title_without_year(input_movie_title)
        
        # Assert
        assert actual_clean_title == expected_clean_title
    
    def test_only_parentheses_content(self):
        """
        Test Case: Input containing only parenthetical content.
        
        Objective: Ensure function returns empty string when only
        parenthetical content is present.
        """
        # Arrange
        input_movie_title = "(2000)"
        expected_clean_title = ""
        
        # Act
        actual_clean_title = extract_movie_title_without_year(input_movie_title)
        
        # Assert
        assert actual_clean_title == expected_clean_title