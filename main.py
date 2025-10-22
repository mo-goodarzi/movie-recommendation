import pandas as pd
import numpy as np
from utils.utils import create_embeddings, query_embedding

class movie_recommender:
    def __init__(self):
        self.database = pd.read_json("data/merged_data_untill_1990.json", lines=True)
        self.create_embeddings = create_embeddings
        self.query_embedding = query_embedding

    def recommend(self, film_name, top_k=10):
        film = self.database[self.database["title"] == film_name]
        film_list=[row["txt"] for _,row in film.iterrows()]
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






