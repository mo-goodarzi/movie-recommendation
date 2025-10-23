import sqlite3
import numpy as np
import os
from dotenv import load_dotenv
from utils.utils import create_embeddings, query_embedding

load_dotenv()

class movie_recommender:
    def __init__(self, db_path=None):
        if db_path is None:
            db_path = os.getenv('SQLITE_DB_PATH', 'data/movies.db')
        self.db_path = db_path
        self.create_embeddings = create_embeddings
        self.query_embedding = query_embedding

        # Verify database exists
        if not os.path.exists(self.db_path):
            raise FileNotFoundError(f"Database not found at {self.db_path}. Run utils/migrate_to_sqlite.py first.")

    def _get_connection(self):
        """Get a database connection."""
        return sqlite3.connect(self.db_path)

    def get_movie_texts(self, film_name):
        """Get all text entries for a given movie title."""
        conn = self._get_connection()
        cursor = conn.cursor()

        # Query to get all text entries for the movie
        cursor.execute("""
            SELECT mt.txt
            FROM movies m
            JOIN movie_texts mt ON m.item_id = mt.item_id
            WHERE m.title = ?
        """, (film_name,))

        texts = [row[0] for row in cursor.fetchall()]
        conn.close()
        return texts

    def recommend(self, film_name, top_k=10):
        # Get all text entries for the movie from database
        film_list = self.get_movie_texts(film_name)

        if not film_list:
            return []

        # now we create embeddings for these reviews
        film_list_embeddings = self.create_embeddings(film_list)

        # mean the vectors
        film_list_embeddings = np.array(film_list_embeddings)
        film_list_embeddings_mean = np.mean(film_list_embeddings, axis=0).reshape(1,-1)
        film_list_embeddings_mean_list = film_list_embeddings_mean.flatten().tolist()

        # Request more results to account for duplicate titles
        # Multiply by 3 to ensure we get enough unique movies after deduplication
        query_top_k = top_k * 3
        sugestions = self.query_embedding(film_list_embeddings_mean_list, top_k=query_top_k, namespace="namespace_until_1990", movie_name=film_name)

        recommendations = []
        for match in sugestions.matches:
            title = match.metadata.get('title')
            score = match.score
            imdb_id = match.metadata.get('imdb_id')
            # Convert imdb_id to zero-padded string format (7 digits)
            if imdb_id:
                imdb_id = str(int(imdb_id)).zfill(7)
            item_id  = match.metadata.get('item_id')
            # Filter out duplicate titles
            if title and title not in [t for t, _,_,_ in recommendations]:
                recommendations.append((title, score,imdb_id, item_id))
                # Stop when we have enough unique recommendations
                if len(recommendations) >= top_k:
                    break

        return recommendations





def main():
    recommender = movie_recommender()
    film_name = str(input("enter your liked filme: "))    #"Toy Story (1995)"
    recommendations = recommender.recommend(film_name, top_k=20)
    for title, score, imdb_id, item_id in recommendations:
        print(f"Title: {title}, Score: {score}, Imdb_id: ")

if __name__ == "__main__":
    main()






