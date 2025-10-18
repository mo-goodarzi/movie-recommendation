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

        sugestions = self.query_embedding(film_list_embeddings_mean_list, top_k=top_k, namespace="namespace_until_1990", movie_name=film_name)

        recommendations = []
        for match in sugestions.matches:
            title = match.metadata.get('title')
            score = match.score
            imdb_id = match.metadata.get('imdb_id')
            item_id  = match.metadata.get('item_id') 
            if title and title not in [t for t, _,_,_ in recommendations]:
                recommendations.append((title, score,imdb_id, item_id))

        return recommendations





def main():
    recommender = movie_recommender()
    film_name = str(input("enter your liked filme: "))    #"Toy Story (1995)"
    recommendations = recommender.recommend(film_name, top_k=20)
    for title, score, imdb_id, item_id in recommendations:
        print(f"Title: {title}, Score: {score}")

if __name__ == "__main__":
    main()



# file_name = "Toy Story (1995)"
# film = database[database["title"] == file_name]
# film_list=[row["txt"] for _,row in film.iterrows()]
# # now we create embeddings for these reviews
# film_list_embeddings = create_embeddings(film_list)

# # mean the vectors
# film_list_embeddings = np.array(film_list_embeddings)
# film_list_embeddings_mean = np.mean(film_list_embeddings, axis=0).reshape(1,-1)
# film_list_embeddings_mean_list = film_list_embeddings_mean.flatten().tolist()

# sugestions = query_embedding(film_list_embeddings_mean_list, top_k=10, namespace="namespace_until_1990", movie_name=file_name)

# for match in sugestions.matches:
#     print(f"Title: {match.metadata['title']}, Score: {match.score}")





