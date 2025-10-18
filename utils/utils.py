import os
from dotenv import load_dotenv
from pinecone import Pinecone
from openai import OpenAI

load_dotenv()


client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))


pc = Pinecone(api_key=os.getenv("PINECONE_API"))
index = pc.Index(os.getenv("INDEX_NAME"))


def create_embeddings(inputs):
    response = client.embeddings.create(model="text-embedding-3-small", input=inputs)
    return [item.embedding for item in response.data]


def query_embedding(
    input_embedding, top_k=10, namespace="namespace_until_1990", movie_name=None
):

    response = index.query(
        vector=input_embedding,
        top_k=top_k,
        include_metadata=True,
        filter={"title": {"$ne": movie_name}},
        namespace=namespace,
    )
    return response
