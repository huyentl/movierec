import streamlit as st
import pandas as pd
import requests
from star_ratings import star_ratings


st.set_page_config(layout="wide")

st.title("Movie Recommender")

# url for movie images
IMAGE_BASE_URL = "https://liangfgithub.github.io/MovieImages/"


# Load data
@st.cache_data
def load_data():
    ratings_url = 'https://liangfgithub.github.io/MovieData/ratings.dat?raw=true'
    ratings = pd.read_csv(
        ratings_url,
        sep='::',
        engine='python',
        names=['UserID', 'MovieID', 'Rating', 'Timestamp']
    )

    movies_url = 'https://liangfgithub.github.io/MovieData/movies.dat?raw=true'
    movies = pd.read_csv(
        movies_url,
        sep='::',
        engine='python',
        names=['MovieID', 'Title', 'Genres'],
        encoding='latin-1'
    )

    movies['MovieID'] = movies['MovieID'].astype(int)

    return ratings, movies


ratings, movies = load_data()

#limit to 200 movies
top_movies = ratings['MovieID'].value_counts().head(200).index
ratings = ratings[ratings['MovieID'].isin(top_movies)]
movies = movies[movies['MovieID'].isin(top_movies)]

user_movie_matrix = ratings.pivot_table(index='UserID', columns='MovieID', values='Rating')
user_movie_matrix = user_movie_matrix.fillna(0)


@st.cache_data

def call_similarity_model():
    pass

st.write("### Step 1: Rate the following movies")

if 'user_ratings' not in st.session_state:
    st.session_state.user_ratings = {}

if 'sample_movies' not in st.session_state:
    st.session_state.sample_movies = movies.sample(120).reset_index(drop=True)

sample_movies = st.session_state.sample_movies

def display_movie_grid(movies_df):
    movies = movies_df.to_dict('records')
    num_cols = 6
    rows = [movies[i:i + num_cols] for i in range(0, len(movies), num_cols)]

    for row in rows:
        cols = st.columns(num_cols)
        for col, movie in zip(cols, row):
            with col:
                # get image
                movie_id = movie['MovieID']
                image_url = f"{IMAGE_BASE_URL}{movie_id}.jpg?raw=true"
                try:
                    response = requests.get(image_url)
                    if response.status_code == 200:
                        st.image(image_url, use_column_width=True)
                    else:
                        st.image('placeholder.png', use_column_width=True)
                except:
                    st.image('placeholder.png', use_column_width=True)
                st.write(movie['Title'])
                # ratings display
                rating = star_ratings(
                    name='',  # No label
                    numStars=0,
                    key=f"rating_{movie_id}"
                )
                st.session_state.user_ratings[movie_id] = rating

# display sections in tabs
tab1, tab2 = st.tabs(["Step 1: Rate Movies", "Step 2: Get Recommendations"])

with tab1:
    st.write("### Step 1: Rate as many movies as possible")
    display_movie_grid(sample_movies)

with tab2:
    st.write("### Step 2: Discover movies you might like")
    if st.button("Click here to get your recommendations"):
        # fetch user rating state
        user_ratings = st.session_state.user_ratings

        user_ratings_df = pd.DataFrame({
            'MovieID': list(user_ratings.keys()),
            'Rating': list(user_ratings.values())
        })

        user_ratings_df = user_ratings_df[user_ratings_df['Rating'] > 0]

        if user_ratings_df.empty:
            st.write("Please rate some movies to get recommendations.")
        else:
            user_profile = user_movie_matrix.iloc[0] * 0
            for idx, row in user_ratings_df.iterrows():
                user_profile[row['MovieID']] = row['Rating']

            def call_IBCF_model():
                pass
            st.markdown("""
            **Note:** Limited movie dataset
            """)
