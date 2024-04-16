import pandas as pd
from fastapi import FastAPI, HTTPException
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from fuzzywuzzy import process
import numpy as np
import requests

app = FastAPI()

# Load data
movie_data_ohe = pd.read_csv('movie_data_ohe.csv')
movie_data = pd.read_csv('movie_data.csv')

def cosine_similarity(vec_A, vec_B):
    """Calculate the cosine similarity between vec A and vec B"""
    # Find the norm
    norm_A = np.linalg.norm(vec_A)
    norm_B = np.linalg.norm(vec_B)

    # Find the dot
    dot_AB = np.dot(vec_A, vec_B)

    # Calculate the similarity
    sim = dot_AB / (norm_A * norm_B)

    return sim

def track_recommendation(track_id, n, track_data, similarity_func):
    """
    Recommend n item based on latest played track_id
    """
    # Generate the similarity score
    n_tracks = len(track_data.index)
    similarity_score = np.zeros(n_tracks)

    # Iterate the whole tracks
    track_target = track_data.loc[track_id]
    for i, track_id_i in enumerate(track_data.index):
        # Extract track_i
        track_i = track_data.loc[track_id_i]

        # Calculate the similarity
        sim_i = similarity_func(vec_A=track_target, vec_B=track_i)

        # Append
        similarity_score[i] = sim_i

    # Sort in descending orders of similarity_score
    sorted_idx = np.argsort(similarity_score)[::-1]

    # Return the n top similar track_id
    top_tracks_id = track_data.index[sorted_idx[1:n+1]]

    return top_tracks_id

def get_movie_id_fuzzy(movie_name, movie_data):
    """
    Get the movie ID based on the movie name using fuzzy matching
    """
    # Create a list of movie titles from the dataset
    movie_titles = movie_data['title'].tolist()
    
    # Use fuzzy matching to find the closest match
    match = process.extractOne(movie_name, movie_titles)
    
    # Check if a match is found and get the movie ID
    if match[1] >= 70:  # Adjust the threshold as needed
        movie_id = movie_data[movie_data['title'] == match[0]].index.values[0]
        return movie_id
    else:
        print("No close match found for the movie name.")
        return None

def fetch_poster(movie_id):
    """Collect poster from database TMDB"""

    # collect api
    url = "https://api.themoviedb.org/3/movie/{}?api_key=d2a4c5175925dade91af903aeefd1cf7".format(movie_id)
    
    # request
    response = requests.get(url)
    
    # change to json
    data = response.json()
    poster_path = data['poster_path']
    
    # collect images
    full_path = "https://image.tmdb.org/t/p/w500/" + poster_path
    
    return full_path

html_file_path = "index.html"

# Mount the static files directory
app.mount("/static", StaticFiles(directory="static"), name="static")

@app.get("/")
async def get():
    with open(html_file_path, "r") as html_file:
        html_content = html_file.read()
    return HTMLResponse(content=html_content, status_code=200)

@app.post('/recommend/')
async def recommend(movie_name: str):
    # Get the movie ID using fuzzy matching function
    movie_id = get_movie_id_fuzzy(movie_name, movie_data)
    
    if movie_id is not None:
        # Get movie recommendations based on the found movie ID
        top_movie_id = track_recommendation(track_id=movie_id,
                                            n=10,
                                            track_data=movie_data_ohe,
                                            similarity_func=cosine_similarity)
        
        # Get the recommended movie data
        selected_movies = []
        for movie_id in top_movie_id:
            movie_title = movie_data.loc[movie_id, 'title']
            poster_url = fetch_poster(movie_id)
            selected_movies.append({'title': movie_title, 'poster_url': poster_url})
        
        # Return the recommended movies as JSON response
        return selected_movies
    else:
        # If no matching movie found, raise HTTP exception
        raise HTTPException(status_code=404, detail='No close match found for the movie name.')


if __name__ == '__main__':
    import uvicorn
    uvicorn.run(app, host='127.0.0.1', port=8000)

