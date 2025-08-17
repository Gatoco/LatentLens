"""
Data Loading Module for LatentLens

This module provides functions to load and preprocess the MovieLens 25M dataset.
It handles path resolution, data loading, and basic data cleaning operations
in a robust and reusable manner.

Author: LatentLens Team
License: MIT
"""

import os
import sys
from typing import Tuple, Optional
import pandas as pd
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class DataLoader:
    """
    Class to handle loading and preprocessing of MovieLens 25M dataset.
    """
    
    def __init__(self, data_path: Optional[str] = None):
        """
        Initialize DataLoader with dataset path.
        
        Args:
            data_path (Optional[str]): Path to the dataset folder. If None, 
                                     will auto-detect from project structure.
        """
        if data_path is None:
            self.project_root, self.data_path = get_project_paths()
        else:
            self.data_path = data_path
            self.project_root = os.path.dirname(self.data_path)
        
        logger.info(f"DataLoader initialized with data path: {self.data_path}")
    
    def load_ratings(self) -> pd.DataFrame:
        """
        Load the ratings dataset.
        
        Returns:
            pd.DataFrame: Ratings dataframe with columns ['userId', 'movieId', 'rating', 'timestamp']
        """
        ratings_path = os.path.join(self.data_path, 'ratings.csv')
        
        if not os.path.exists(ratings_path):
            raise FileNotFoundError(f"Ratings file not found at: {ratings_path}")
        
        logger.info(f"Loading ratings from: {ratings_path}")
        ratings_df = pd.read_csv(ratings_path)
        
        logger.info(f"Loaded {len(ratings_df)} ratings for {ratings_df['userId'].nunique()} users and {ratings_df['movieId'].nunique()} movies")
        
        return ratings_df
    
    def load_movies(self) -> pd.DataFrame:
        """
        Load the movies dataset.
        
        Returns:
            pd.DataFrame: Movies dataframe with columns ['movieId', 'title', 'genres']
        """
        movies_path = os.path.join(self.data_path, 'movies.csv')
        
        if not os.path.exists(movies_path):
            raise FileNotFoundError(f"Movies file not found at: {movies_path}")
        
        logger.info(f"Loading movies from: {movies_path}")
        movies_df = pd.read_csv(movies_path)
        
        logger.info(f"Loaded {len(movies_df)} movies")
        
        return movies_df
    
    def load_tags(self) -> pd.DataFrame:
        """
        Load the tags dataset.
        
        Returns:
            pd.DataFrame: Tags dataframe with columns ['userId', 'movieId', 'tag', 'timestamp']
        """
        tags_path = os.path.join(self.data_path, 'tags.csv')
        
        if not os.path.exists(tags_path):
            raise FileNotFoundError(f"Tags file not found at: {tags_path}")
        
        logger.info(f"Loading tags from: {tags_path}")
        tags_df = pd.read_csv(tags_path)
        
        logger.info(f"Loaded {len(tags_df)} tags")
        
        return tags_df


# Path configuration with cross-platform compatibility
def get_project_paths() -> Tuple[str, str]:
    """
    Get the absolute paths for the project root and dataset folder.
    
    This function ensures that data loading works regardless of where
    the script is executed from (notebooks/, src/, or project root).
    
    Returns:
        Tuple[str, str]: A tuple containing:
            - project_root_path (str): Absolute path to the project root
            - dataset_folder_path (str): Absolute path to the ml-25m dataset folder
    """
    current_script_directory = os.path.dirname(os.path.abspath(__file__))
    project_root_path = os.path.dirname(current_script_directory)
    dataset_folder_path = os.path.join(project_root_path, 'data', 'ml-25m')
    
    return project_root_path, dataset_folder_path


def load_movieLens_datasets() -> Tuple[pd.DataFrame, pd.DataFrame]:
    """
    Load the movies and ratings datasets from MovieLens 25M.
    
    Returns:
        Tuple[pd.DataFrame, pd.DataFrame]: A tuple containing:
            - movies_dataframe (pd.DataFrame): Movies data with columns [movieId, title, genres]
            - ratings_dataframe (pd.DataFrame): Ratings data with columns [userId, movieId, rating, timestamp]
            
    Raises:
        FileNotFoundError: If the dataset files cannot be found in the expected location
        pd.errors.EmptyDataError: If the CSV files are empty or corrupted
    """
    project_root, dataset_folder = get_project_paths()
    
    print(f"Loading datasets from: {dataset_folder}")
    
    # Construct file paths using os.path.join for cross-platform compatibility
    movies_file_path = os.path.join(dataset_folder, 'movies.csv')
    ratings_file_path = os.path.join(dataset_folder, 'ratings.csv')
    
    # Verify files exist before attempting to load
    if not os.path.exists(movies_file_path):
        raise FileNotFoundError(f"Movies dataset not found at: {movies_file_path}")
    if not os.path.exists(ratings_file_path):
        raise FileNotFoundError(f"Ratings dataset not found at: {ratings_file_path}")
    
    # Load datasets with explicit encoding for robustness
    movies_dataframe = pd.read_csv(movies_file_path, encoding='utf-8')
    ratings_dataframe = pd.read_csv(ratings_file_path, encoding='utf-8')
    
    print(f"Movies dataset loaded: {len(movies_dataframe):,} rows")
    print(f"Ratings dataset loaded: {len(ratings_dataframe):,} rows")
    
    return movies_dataframe, ratings_dataframe


def merge_and_clean_datasets(movies_df: pd.DataFrame, ratings_df: pd.DataFrame) -> pd.DataFrame:
    """
    Merge movies and ratings datasets and perform basic cleaning.
    
    This function combines the movies and ratings data into a single DataFrame
    and removes columns that are not immediately needed for basic recommendation
    algorithms (timestamp, genres).
    
    Args:
        movies_df (pd.DataFrame): Movies dataset with movie metadata
        ratings_df (pd.DataFrame): Ratings dataset with user preferences
        
    Returns:
        pd.DataFrame: Merged and cleaned dataset with columns:
            [userId, movieId, rating, title]
    """
    print("Merging datasets...")
    
    # Perform left join to preserve all ratings even if movie metadata is missing
    merged_dataframe = pd.merge(
        ratings_df, 
        movies_df, 
        on='movieId', 
        how='left'
    )
    
    # Remove columns not needed for basic collaborative filtering
    columns_to_remove = ['timestamp', 'genres']
    cleaned_dataframe = merged_dataframe.drop(columns=columns_to_remove, errors='ignore')
    
    # Check for missing movie titles (indicates data quality issues)
    missing_titles_count = cleaned_dataframe['title'].isnull().sum()
    if missing_titles_count > 0:
        print(f"Warning: {missing_titles_count} ratings have missing movie titles")
    
    print(f"Data merge completed. Final dataset: {len(cleaned_dataframe):,} rows")
    
    return cleaned_dataframe


def load_and_prepare_data() -> pd.DataFrame:
    """
    Complete data loading and preparation pipeline.
    
    This is the main entry point for data loading. It orchestrates the
    loading of raw datasets, merging, and basic cleaning operations.
    
    Returns:
        pd.DataFrame: Cleaned and merged dataset ready for analysis
        
    Raises:
        FileNotFoundError: If dataset files are not found
        Exception: For any other data loading or processing errors
    """
    try:
        movies_dataframe, ratings_dataframe = load_movieLens_datasets()
        final_dataframe = merge_and_clean_datasets(movies_dataframe, ratings_dataframe)
        
        print("Data preparation pipeline completed successfully")
        return final_dataframe
        
    except Exception as error:
        print(f"Error in data loading pipeline: {error}")
        raise


def main():
    """
    Main function for testing the data loading module in isolation.
    
    This function is executed only when the script is run directly,
    not when imported as a module. It provides a way to test the
    data loading functionality independently.
    """
    print("LatentLens Data Loader - Testing Mode")
    print("=" * 50)
    
    try:
        main_dataframe = load_and_prepare_data()
        
        print("\nDataset Overview:")
        print(f"Shape: {main_dataframe.shape}")
        print(f"Columns: {list(main_dataframe.columns)}")
        print("\nSample data:")
        print(main_dataframe.head())
        
        print("\nData types:")
        print(main_dataframe.dtypes)
        
    except Exception as error:
        print(f"Failed to load data: {error}")
        sys.exit(1)


# Execute main function only when script is run directly
if __name__ == '__main__':
    main()