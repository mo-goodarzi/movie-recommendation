import os
from dotenv import load_dotenv

load_dotenv()

from openai import OpenAI

client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
pc     = Pinecone(api_key=os.getenv("PINECONE_API"))

client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

def create_embeddings(inputs):
    response = client.embeddings.create(
        model="text-embedding-3-small",
        input=inputs
    )
    return [item.embedding for item in response.data]