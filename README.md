# Movie Recommendation System

A semantic movie recommendation system that uses OpenAI embeddings and Pinecone vector search to find similar films based on review content.

## Features

- Semantic search based on movie reviews
- Interactive Streamlit web interface
- Movie poster display using OMDb API
- IMDb integration for additional information
- Similarity scoring with visual indicators

## Setup

### Prerequisites

- Python 3.8+
- OpenAI API key
- Pinecone API key
- OMDb API key (for movie posters)

### Installation

1. Clone the repository
2. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

3. Create a `.env` file with the following keys:
   ```env
   OPENAI_API_KEY=your_openai_api_key
   PINECONE_API=your_pinecone_api_key
   INDEX_NAME=your_pinecone_index_name
   OMDB_API_KEY=your_omdb_api_key
   NAMESPACE=namespace_until_1990
   EMBEDDING_MODEL=text-embedding-3-small
   DATABASE_PATH=data/merged_data_untill_1990.json
   ```

### Getting an OMDb API Key

1. Visit [OMDb API](https://www.omdbapi.com/apikey.aspx)
2. Sign up for a free API key (1,000 daily requests)
3. Add the key to your `.env` file as `OMDB_API_KEY`

## Usage

Run the Streamlit app:
```bash
streamlit run app.py
```

## How It Works

1. User selects a movie from the database
2. System retrieves all reviews for that movie
3. Creates embeddings for each review using OpenAI
4. Averages embeddings to create a movie representation
5. Queries Pinecone for similar movie vectors
6. Displays recommendations with posters and similarity scores