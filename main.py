import pandas as pd
import numpy as np
from utils.utils import create_embeddings, query_embedding
database = pd.read_json("data/merged_data_untill_1990.json", lines=True)

file_name = "Toy Story (1995)"
film = database[database["title"] == file_name]
film_list=[row["txt"] for _,row in film.iterrows()]
# now we create embeddings for these reviews
film_list_embeddings = create_embeddings(film_list)

# mean the vectors
film_list_embeddings = np.array(film_list_embeddings)
film_list_embeddings_mean = np.mean(film_list_embeddings, axis=0).reshape(1,-1)
film_list_embeddings_mean_list = film_list_embeddings_mean.flatten().tolist()

sugestions = query_embedding(film_list_embeddings_mean_list, top_k=10, namespace="namespace_until_1990", movie_name=file_name)

for match in sugestions.matches:
    print(f"Title: {match.metadata['title']}, Score: {match.score}")





