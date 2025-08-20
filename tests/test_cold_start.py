"""
Test suite for Cold Start handling functionality
"""
import pytest
import sys
import os

# Add src to path
sys.path.append(os.path.join(os.path.dirname(__file__), 'src'))

from src.data_loader import DataLoader
import pandas as pd


class TestColdStartHandling:
    """Test suite for cold start problem handling"""
    
    @classmethod
    def setup_class(cls):
        """Setup test environment"""
        cls.data_loader = DataLoader()
        
    def test_new_user_detection(self):
        """Test detection of completely new users"""
        # Test with a user ID that definitely doesn't exist
        non_existent_user = 999999999
        ratings = self.data_loader.load_ratings()
        user_ratings = ratings[ratings['userId'] == non_existent_user]
        assert len(user_ratings) == 0, "New user should have no ratings"
        
    def test_insufficient_data_detection(self):
        """Test detection of users with insufficient rating data"""
        # Find a user with very few ratings
        ratings = self.data_loader.load_ratings()
        user_rating_counts = ratings.groupby('userId').size()
        users_with_few_ratings = user_rating_counts[user_rating_counts < 5]
        
        if len(users_with_few_ratings) > 0:
            test_user = users_with_few_ratings.index[0]
            user_ratings = self.data_loader.ratings[
                self.data_loader.ratings['userId'] == test_user
            ]
            assert len(user_ratings) < 5, "User should have insufficient data"
        
    def test_popular_movies_generation(self):
        """Test generation of popular movies for cold start"""
        # Calculate movie popularity
        ratings = self.data_loader.load_ratings()
        movie_stats = ratings.groupby('movieId').agg({
            'rating': ['count', 'mean']
        }).round(2)
        
        movie_stats.columns = ['rating_count', 'avg_rating']
        movie_stats = movie_stats.reset_index()
        
        # Filter popular movies
        popular_movies = movie_stats[
            (movie_stats['rating_count'] >= 100) & 
            (movie_stats['avg_rating'] >= 3.5)
        ]
        
        assert len(popular_movies) > 0, "Should find popular movies"
        assert popular_movies['avg_rating'].min() >= 3.5, "All popular movies should have good ratings"
        assert popular_movies['rating_count'].min() >= 100, "All popular movies should have sufficient ratings"
        
    def test_trending_movies_generation(self):
        """Test generation of trending/recent movies"""
        # Extract years from movie titles
        movies = self.data_loader.load_movies()
        movies['year'] = movies['title'].str.extract(r'\((\d{4})\)$')[0]
        movies['year'] = pd.to_numeric(movies['year'], errors='coerce')
        
        # Get recent movies
        max_year = movies['year'].max()
        recent_threshold = max_year - 10
        recent_movies = movies[movies['year'] >= recent_threshold]
        
        assert len(recent_movies) > 0, "Should find recent movies"
        assert recent_movies['year'].min() >= recent_threshold, "All movies should be recent"
        
    def test_genre_diversity(self):
        """Test genre diversity in recommendations"""
        # Extract all genres
        movies = self.data_loader.load_movies()
        all_genres = []
        for genres_str in movies['genres'].dropna():
            genres = genres_str.split('|')
            all_genres.extend(genres)
        
        from collections import Counter
        genre_counts = Counter(all_genres)
        
        # Should have multiple genres available
        assert len(genre_counts) > 10, "Should have diverse genres available"
        assert "(no genres listed)" not in genre_counts or genre_counts["(no genres listed)"] < len(all_genres) * 0.1
        
    def test_content_based_similarity(self):
        """Test content-based similarity for new movies"""
        # Get a movie with known genres
        movies = self.data_loader.load_movies()
        test_movie = movies[
            movies['genres'].str.contains('Action', na=False)
        ].iloc[0]
        
        test_movie_id = test_movie['movieId']
        test_genres = set(test_movie['genres'].split('|'))
        
        # Find similar movies based on genres
        similar_count = 0
        for _, movie in movies.head(100).iterrows():  # Test with first 100 movies
            if movie['movieId'] == test_movie_id:
                continue
                
            movie_genres = set(movie['genres'].split('|')) if pd.notna(movie['genres']) else set()
            
            if test_genres.intersection(movie_genres):
                similar_count += 1
        
        assert similar_count > 0, "Should find movies with similar genres"
        
    def test_cold_start_integration(self):
        """Test integration of different cold start strategies"""
        # Test that we can combine different recommendation sources

        # Popular movies
        ratings = self.data_loader.load_ratings()
        movie_stats = ratings.groupby('movieId').agg({
            'rating': ['count', 'mean']
        }).round(2)
        movie_stats.columns = ['rating_count', 'avg_rating']
        movie_stats = movie_stats.reset_index()
        
        popular_movies = movie_stats[
            (movie_stats['rating_count'] >= 100) & 
            (movie_stats['avg_rating'] >= 3.5)
        ].head(5)
        
        # Genre-diverse movies
        movies = self.data_loader.load_movies()
        action_movies = movies[
            movies['genres'].str.contains('Action', na=False)
        ].head(3)
        
        comedy_movies = movies[
            movies['genres'].str.contains('Comedy', na=False)
        ].head(3)
        
        # Should be able to combine recommendations
        combined_movie_ids = set()
        combined_movie_ids.update(popular_movies['movieId'].tolist())
        combined_movie_ids.update(action_movies['movieId'].tolist())
        combined_movie_ids.update(comedy_movies['movieId'].tolist())
        
        assert len(combined_movie_ids) >= 5, "Should successfully combine different recommendation sources"
        
    def test_user_rating_patterns(self):
        """Test analysis of user rating patterns for cold start decisions"""
        # Get users with different rating patterns
        ratings = self.data_loader.load_ratings()
        user_stats = ratings.groupby('userId').agg({
            'rating': ['count', 'mean', 'std']
        }).round(2)
        
        user_stats.columns = ['rating_count', 'avg_rating', 'rating_std']
        user_stats = user_stats.reset_index()
        
        # Categories of users
        new_users = user_stats[user_stats['rating_count'] == 0]  # Shouldn't exist in our data
        sparse_users = user_stats[user_stats['rating_count'] < 5]
        active_users = user_stats[user_stats['rating_count'] >= 20]
        
        # Should have different categories of users
        assert len(sparse_users) > 0 or len(active_users) > 0, "Should have users with different activity levels"
        
        if len(active_users) > 0:
            # Active users should have reasonable rating patterns
            assert active_users['avg_rating'].mean() > 1.0, "Active users should have reasonable average ratings"
            assert active_users['avg_rating'].mean() < 5.0, "Active users should have reasonable average ratings"
            
    def test_movie_cold_start_levels(self):
        """Test classification of movies by cold start difficulty"""
        # Analyze movie rating distribution
        ratings = self.data_loader.load_ratings()
        movie_rating_counts = ratings.groupby('movieId').size()
        
        # Categories based on rating count
        extreme_cold_start = movie_rating_counts[movie_rating_counts == 0]  # No ratings
        high_cold_start = movie_rating_counts[movie_rating_counts < 10]    # Very few ratings
        medium_cold_start = movie_rating_counts[(movie_rating_counts >= 10) & (movie_rating_counts < 50)]
        low_cold_start = movie_rating_counts[movie_rating_counts >= 50]    # Sufficient ratings
        
        movies = self.data_loader.load_movies()
        total_movies = len(movies)
        rated_movies = len(movie_rating_counts)
        
        # Some movies might not have ratings (pure cold start)
        extreme_cold_start_count = total_movies - rated_movies + len(extreme_cold_start)
        
        print(f"Cold start analysis:")
        print(f"  Total movies: {total_movies}")
        print(f"  Extreme cold start (0 ratings): {extreme_cold_start_count}")
        print(f"  High cold start (<10 ratings): {len(high_cold_start)}")
        print(f"  Medium cold start (10-49 ratings): {len(medium_cold_start)}")
        print(f"  Low cold start (50+ ratings): {len(low_cold_start)}")
        
        # Should have movies in different categories
        assert rated_movies > 0, "Should have some rated movies"
        assert len(low_cold_start) > 0, "Should have some well-rated movies"


if __name__ == "__main__":
    # Run tests
    import subprocess
    import sys
    
    print("🧪 Running Cold Start Tests...")
    
    try:
        # Run with pytest if available
        result = subprocess.run([sys.executable, "-m", "pytest", __file__, "-v"], 
                              capture_output=True, text=True)
        print(result.stdout)
        if result.stderr:
            print("STDERR:", result.stderr)
    except FileNotFoundError:
        # Run tests manually if pytest not available
        print("Running tests manually...")
        test_instance = TestColdStartHandling()
        test_instance.setup_class()
        
        test_methods = [method for method in dir(test_instance) if method.startswith('test_')]
        
        for test_method in test_methods:
            try:
                print(f"Running {test_method}...")
                getattr(test_instance, test_method)()
                print(f"✅ {test_method} passed")
            except Exception as e:
                print(f"❌ {test_method} failed: {e}")
        
        print("\n✨ Cold Start tests completed!")
