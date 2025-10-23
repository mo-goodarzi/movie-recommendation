import streamlit as st
import sqlite3
import requests
import os
from dotenv import load_dotenv
from main import movie_recommender

load_dotenv()

# Get database path from environment
DB_PATH = os.getenv('SQLITE_DB_PATH', 'data/movies.db')

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
    """Get sorted list of all movie titles from SQLite database."""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("SELECT DISTINCT title FROM movies ORDER BY title")
    movies = [row[0] for row in cursor.fetchall()]
    conn.close()
    return movies

movie_list = get_movie_list()

# Function to get movie IMDb ID from database
@st.cache_data
def get_movie_imdb_id(movie_title):
    """Get IMDb ID for a movie from the SQLite database."""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("SELECT imdb_id FROM movies WHERE title = ? LIMIT 1", (movie_title,))
    result = cursor.fetchone()
    conn.close()

    if result and result[0]:
        # Convert to zero-padded string format (7 digits)
        return str(int(result[0])).zfill(7)
    return None

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
        # Display the chosen movie in a special card
        st.markdown("<h2 style='color: #2D3748; font-size: 1.5rem; font-weight: 500; margin-bottom: 1rem; margin-top: 2rem;'>Your Selected Movie</h2>", unsafe_allow_html=True)

        # Get chosen movie details
        chosen_movie_imdb_id = get_movie_imdb_id(selected_movie)
        chosen_movie_poster = get_movie_poster(chosen_movie_imdb_id) if chosen_movie_imdb_id else None

        # Create centered column for chosen movie
        col1, col2, col3 = st.columns([1, 2, 1])
        with col2:
            if chosen_movie_poster:
                st.markdown(
                    f"""
                    <div style="
                        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                        border-radius: 15px;
                        padding: 20px;
                        margin: 10px 0 30px 0;
                        box-shadow: 0 8px 16px rgba(0, 0, 0, 0.2);
                        border: 3px solid #f5c518;
                    ">
                        <h3 style="
                            color: white;
                            text-align: center;
                            margin-bottom: 15px;
                            font-size: 1.3rem;
                            font-weight: bold;
                        ">{selected_movie}</h3>
                        <div style="
                            width: 100%;
                            display: flex;
                            justify-content: center;
                            align-items: center;
                            margin-bottom: 15px;
                        ">
                            <img src="{chosen_movie_poster}" style="
                                max-width: 100%;
                                max-height: 450px;
                                object-fit: contain;
                                border-radius: 10px;
                                box-shadow: 0 4px 8px rgba(0, 0, 0, 0.3);
                            " alt="{selected_movie} poster">
                        </div>
                        {f'<a href="https://www.imdb.com/title/tt{chosen_movie_imdb_id}" target="_blank" style="text-decoration: none;"><div style="background-color: #f5c518; color: #000; padding: 12px 20px; border-radius: 8px; text-align: center; font-weight: bold; font-size: 1rem; margin-top: 10px;">View on IMDb</div></a>' if chosen_movie_imdb_id else ''}
                    </div>
                    """,
                    unsafe_allow_html=True
                )
            else:
                st.markdown(
                    f"""
                    <div style="
                        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                        border-radius: 15px;
                        padding: 30px;
                        margin: 10px 0 30px 0;
                        box-shadow: 0 8px 16px rgba(0, 0, 0, 0.2);
                        border: 3px solid #f5c518;
                        text-align: center;
                    ">
                        <h3 style="
                            color: white;
                            font-size: 1.5rem;
                            font-weight: bold;
                            margin-bottom: 20px;
                        ">{selected_movie}</h3>
                        <p style="color: white; font-size: 1rem; margin-bottom: 20px;">Poster not available</p>
                        {f'<a href="https://www.imdb.com/title/tt{chosen_movie_imdb_id}" target="_blank" style="text-decoration: none;"><div style="background-color: #f5c518; color: #000; padding: 12px 20px; border-radius: 8px; text-align: center; font-weight: bold; font-size: 1rem; display: inline-block;">View on IMDb</div></a>' if chosen_movie_imdb_id else ''}
                    </div>
                    """,
                    unsafe_allow_html=True
                )

        # Recommendations section
        st.markdown("<h2 style='color: #2D3748; font-size: 1.5rem; font-weight: 500; margin-bottom: 1rem; margin-top: 2rem;'>Recommended Movies Based on Your Selection</h2>", unsafe_allow_html=True)
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

