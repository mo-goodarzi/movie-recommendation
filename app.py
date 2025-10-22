import streamlit as st
import pandas as pd
import requests
import os
from dotenv import load_dotenv
from main import movie_recommender

load_dotenv()

# Set page config
st.set_page_config(
    page_title="Movie Recommender",
    page_icon="🎬",
    layout="wide"
)

# Custom CSS
st.markdown("""
    <style>
    .main {
        padding: 2rem;
    }
    .stTitle {
        color: #2D3748;
        font-size: 3rem !important;
        font-weight: 700;
        margin-bottom: 1rem;
    }
    .stSubheader {
        color: #4A5568;
        font-size: 1.5rem !important;
        font-weight: 500;
    }
    .stButton > button {
        width: 100%;
        padding: 0.5rem 1rem;
        font-size: 1.1rem;
        background-color: #4A5568 !important;
        color: white !important;
    }
    .stButton > button:hover {
        background-color: #2D3748 !important;
    }
    .stSelectbox > div > div {
        background-color: #E6E9F0;
        color: #2D3748 !important;
    }
    .stSelectbox [data-baseweb="select"] input {
        color: #2D3748 !important;
    }
    .stSelectbox [data-baseweb="select"] input::placeholder {
        color: #2D3748 !important;
        opacity: 1;
    }
    </style>
    """, unsafe_allow_html=True)

# Title and description
st.markdown("<h1 class='stTitle'>🎬 Movie Recommendation System</h1>", unsafe_allow_html=True)
st.markdown("""
    <div style='
        background-color: #E6E9F0;
        padding: 1rem;
        border-radius: 10px;
        margin-bottom: 2rem;
        border-left: 5px solid #4A5568;
        color: #2D3748;
    '>
        Get personalized movie recommendations based on your favorite films!
    </div>
""", unsafe_allow_html=True)

# Initialize the recommender
@st.cache_resource
def get_recommender():
    return movie_recommender()

recommender = get_recommender()

# Load the movie database for the dropdown
@st.cache_data
def get_movie_list():
    database = pd.read_json("data/merged_data_untill_1990.json", lines=True)
    return sorted(database['title'].unique().tolist())

movie_list = get_movie_list()

# Function to get movie poster from OMDb API
@st.cache_data
def get_movie_poster(imdb_id):
    """Fetch movie poster URL from OMDb API"""
    if not imdb_id:
        return None

    api_key = os.getenv("OMDB_API_KEY")
    if not api_key:
        return None

    try:
        url = f"http://www.omdbapi.com/?i=tt{imdb_id}&apikey={api_key}"
        response = requests.get(url, timeout=5)
        if response.status_code == 200:
            data = response.json()
            poster_url = data.get('Poster')
            if poster_url and poster_url != 'N/A':
                return poster_url
    except:
        pass
    return None

# Create the input section
st.markdown("<h2 style='color: #2D3748; font-size: 1.5rem; font-weight: 500; margin-bottom: 1rem;'>Select a Movie</h2>", unsafe_allow_html=True)
selected_movie = st.selectbox(
    "",  # Removing the label since we already have the header
    options=movie_list,
    index=None,
    placeholder="📽️ Select a movie..."
)

# Number of recommendations slider
num_recommendations = st.slider("Number of recommendations:", min_value=5, max_value=20, value=10)

# Add a search button
search_button = st.button("Get Recommendations", type="primary", disabled=not selected_movie)

# Container for recommendations
recommendations_container = st.container()

# Get recommendations when the search button is clicked
if search_button and selected_movie:
    with recommendations_container:
        st.subheader("Recommended Movies")
        with st.spinner('Finding recommendations...'):
            recommendations = recommender.recommend(selected_movie, top_k=num_recommendations)
            
            # Create four columns for displaying recommendations in wide mode
            cols = st.columns(4)
            for idx, (title, score, imdb_id, item_id) in enumerate(recommendations):
                with cols[idx % 4]:
                    # Get poster URL
                    poster_url = get_movie_poster(imdb_id)

                    # Create a card-like container with poster
                    with st.container():
                        if poster_url:
                            # Card with poster image - Fixed height for consistency
                            st.markdown(
                                f"""
                                <div style="
                                    background-color: #E6E9F0;
                                    border-radius: 10px;
                                    padding: 15px;
                                    margin: 10px 0;
                                    box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
                                    border: 1px solid #CBD5E0;
                                    height: 540px;
                                    width: 100%;
                                    display: flex;
                                    flex-direction: column;
                                ">
                                    <h3 style="
                                        color: #2D3748;
                                        margin-bottom: 10px;
                                        font-size: 1rem;
                                        overflow: hidden;
                                        text-overflow: ellipsis;
                                        display: -webkit-box;
                                        -webkit-line-clamp: 2;
                                        -webkit-box-orient: vertical;
                                        height: 45px;
                                    ">{idx + 1}. {title}</h3>
                                    <div style="
                                        width: 100%;
                                        height: 380px;
                                        display: flex;
                                        justify-content: center;
                                        align-items: center;
                                        background-color: #CBD5E0;
                                        border-radius: 8px;
                                        margin-bottom: 10px;
                                        overflow: hidden;
                                    ">
                                        <img src="{poster_url}" style="
                                            max-width: 100%;
                                            max-height: 100%;
                                            object-fit: contain;
                                            display: block;
                                        " alt="{title} poster">
                                    </div>
                                    <div style="
                                        background-color: #4A5568;
                                        height: 4px;
                                        width: {int(score * 100)}%;
                                        border-radius: 2px;
                                        margin: 8px 0;
                                    "></div>
                                    <p style="
                                        color: #555;
                                        font-size: 0.85rem;
                                        margin: 0 0 10px 0;
                                    ">Similarity: {score:.2f}</p>
                                    {f'<a href="https://www.imdb.com/title/tt{imdb_id}" target="_blank" style="text-decoration: none;"><div style="background-color: #f5c518; color: #000; padding: 8px 12px; border-radius: 5px; text-align: center; font-weight: bold; font-size: 0.85rem;">View on IMDb</div></a>' if imdb_id else ''}
                                </div>
                                """,
                                unsafe_allow_html=True
                            )
                        else:
                            # Card without poster - Same fixed height for consistency
                            st.markdown(
                                f"""
                                <div style="
                                    background-color: #E6E9F0;
                                    border-radius: 10px;
                                    padding: 15px;
                                    margin: 10px 0;
                                    box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
                                    border: 1px solid #CBD5E0;
                                    height: 540px;
                                    width: 100%;
                                    display: flex;
                                    flex-direction: column;
                                    justify-content: space-between;
                                ">
                                    <div>
                                        <h3 style="
                                            color: #2D3748;
                                            margin-bottom: 10px;
                                            font-size: 1rem;
                                            overflow: hidden;
                                            text-overflow: ellipsis;
                                            display: -webkit-box;
                                            -webkit-line-clamp: 2;
                                            -webkit-box-orient: vertical;
                                            height: 45px;
                                        ">{idx + 1}. {title}</h3>
                                        <div style="
                                            width: 100%;
                                            height: 380px;
                                            display: flex;
                                            justify-content: center;
                                            align-items: center;
                                            background-color: #CBD5E0;
                                            border-radius: 8px;
                                            margin-bottom: 10px;
                                        ">
                                            <p style="color: #555; font-size: 0.9rem;">No poster available</p>
                                        </div>
                                        <div style="
                                            background-color: #4A5568;
                                            height: 4px;
                                            width: {int(score * 100)}%;
                                            border-radius: 2px;
                                            margin: 8px 0;
                                        "></div>
                                        <p style="
                                            color: #555;
                                            font-size: 0.85rem;
                                            margin: 0 0 10px 0;
                                        ">Similarity: {score:.2f}</p>
                                    </div>
                                    {f'<a href="https://www.imdb.com/title/tt{imdb_id}" target="_blank" style="text-decoration: none;"><div style="background-color: #f5c518; color: #000; padding: 8px 12px; border-radius: 5px; text-align: center; font-weight: bold; font-size: 0.85rem;">View on IMDb</div></a>' if imdb_id else ''}
                                </div>
                                """,
                                unsafe_allow_html=True
                            )
elif not selected_movie:
    with recommendations_container:
        st.info("Please select a movie to get recommendations.")

# Add footer
st.markdown("---")
st.markdown("Made with ❤️ using Streamlit and AI")

