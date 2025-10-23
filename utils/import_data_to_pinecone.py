import os
import pandas as pd
import numpy as np

from dotenv import load_dotenv
from openai import OpenAI
from uuid import uuid4
from pinecone import Pinecone, ServerlessSpec



load_dotenv()


client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
pc = Pinecone(api_key=os.getenv("PINECONE_API"))

# conect to pinecone index
index = pc.Index(os.getenv("INDEX_NAME"))

# specify batch limit for inserting data to pinecone
batch_limit = 50

# load data

df = pd.read_json(path_or_buf=os.getenv("DATABASE_PATH"), lines=True)


# insert data to pinecone in batches
# for batch in np.array_split(df, len(df) / batch_limit):
for batch in np.array_split(df.iloc[20176:], len(df.iloc[20176:]) / batch_limit):
    metadatas = [
        {
            "item_id": row["item_id"],
            "title": row["title"],
            "year": row["year"],
            # "text": row["txt"],
            "directed_by": row["directedBy"],
            "stars": list(row["starring"].split(", ")),
            "average_rating": row["avgRating"],
            "imdb_id": row["imdbId"],
        }
        for _, row in batch.iterrows()
    ]
    texts = batch["txt"].tolist()
    ids = [str(uuid4()) for _ in range(len(texts))]
    response = client.embeddings.create(input=texts, model=os.getenv("EMBEDDING_MODEL"))
    embeds = [np.array(item.embedding, dtype=np.float32) for item in response.data]
    index.upsert(vectors=zip(ids, embeds, metadatas), namespace=os.getenv("NAMESPACE"))