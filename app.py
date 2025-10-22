import streamlit as st
import pandas as pd
from main import movie_recommender

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
            
            # Create three columns for displaying recommendations
            cols = st.columns(3)
            for idx, (title, score, imdb_id, item_id) in enumerate(recommendations):
                with cols[idx % 3]:
                    # Create a card-like container with fixed size and custom styling
                    with st.container():
                        st.markdown(
                            f"""
                            <div style="
                                background-color: #E6E9F0;
                                border-radius: 10px;
                                padding: 20px;
                                margin: 10px 0;
                                box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
                                border: 1px solid #CBD5E0;
                                height: 250px;
                                width: 100%;
                                position: relative;
                                display: flex;
                                flex-direction: column;
                            ">
                                <div style="flex-grow: 1;">
                                    <h3 style="
                                        color: #2D3748;
                                        margin-bottom: 10px;
                                        font-size: 1.2rem;
                                        overflow: hidden;
                                        text-overflow: ellipsis;
                                    ">{idx + 1}. {title}</h3>
                                    <div style="
                                        background-color: #4A5568;
                                        height: 4px;
                                        width: {int(score * 100)}%;
                                        border-radius: 2px;
                                        margin: 10px 0;
                                    "></div>
                                    <p style="
                                        color: #555;
                                        font-size: 0.9rem;
                                        margin-bottom: 15px;
                                    ">Similarity Score: {score:.2f}</p>
                                </div>
                                <div style="
                                    position: absolute;
                                    bottom: 20px;
                                    left: 20px;
                                    right: 20px;
                                ">
                                    {f'<a href="https://www.imdb.com/title/tt{imdb_id}" target="_blank" style="text-decoration: none;"><div style="background-color: #f5c518; color: #000; padding: 8px 12px; border-radius: 5px; text-align: center; font-weight: bold;">View on IMDb</div></a>' if imdb_id else ''}
                                </div>
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

