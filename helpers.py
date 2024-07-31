import os
import spotipy
from dotenv import load_dotenv
from spotipy.oauth2 import SpotifyClientCredentials
from flask import redirect, render_template, session
from functools import wraps
import concurrent.futures
from functools import partial



def login_required(f):
    """
    Decorate routes to require login.

    https://flask.palletsprojects.com/en/latest/patterns/viewdecorators/
    """

    @wraps(f)
    def decorated_function(*args, **kwargs):
        if session.get("user_id") is None:
            return redirect("/login")
        return f(*args, **kwargs)

    return decorated_function



#get client id/secret from .env file
load_dotenv()
client_id = os.getenv("CLIENT_ID")
client_secret = os.getenv("CLIENT_SECRET")
client_credentials_manager = SpotifyClientCredentials(client_id=client_id, client_secret=client_secret)
sp = spotipy.Spotify(client_credentials_manager=client_credentials_manager)

class Track():
    def __init__(self, track_id, sp):
        self.track_id = track_id
        self.album_id = None
        self.sp = sp
        self.name = None
        self.artists = []
        self.release_date = None
        self.tracks = []
        self.image = None
        
        self.load_track_info()

    def load_track_info(self):
        track_info = self.sp.track(self.track_id)
        self.album_id = track_info['album']['id'] 
        self.name = track_info['name']
        self.artists = [artist['name'] for artist in track_info['artists']]
        self.image = track_info['album']['images'][0]['url']
        self.release_date = track_info['album']['release_date']


def fetch_track_info(track_id, sp):
    return Track(track_id, sp)


class Album:
    def __init__(self, album_id, sp):
        self.album_id = album_id
        self.sp = sp
        self.name = None
        self.artist = []
        self.release_date = None
        self.tracks = []
        self.image = None

        self.load_album_info()
    
    def load_album_info(self):
        album_info = self.sp.album(self.album_id)
        self.name = album_info['name']
        self.artist = [artist['name'] for artist in album_info['artists']]
        self.image = album_info['images'][0]['url']
        self.release_date = album_info['release_date']
        self.load_tracks(album_info['tracks']['items'])

    def load_tracks(self, tracks):
        for track in tracks:
            track_name = track['name']
            track_sample_url = None

            # Check if the track has a preview URL
            if 'preview_url' in track and track['preview_url']:
                track_sample_url = track['preview_url']
            self.tracks.append({'name': track_name, 'sample_url': track_sample_url})


def fetch_album_info(album_id, sp):
    return Album(album_id, sp)



def search_albums(search, sp):
    # search for albums based on input (limit 12)
    results = sp.search(q=search, limit=12, type='album')

    # Check if there are any album results
    if results['albums']['items']:
        albums_ids = [album['id'] for album in results['albums']['items']]

        # Use ThreadPoolExecutor for concurrent execution
        with concurrent.futures.ThreadPoolExecutor() as executor:
            # Fetch album details concurrently
            fetch_album_partial = partial(fetch_album_info, sp=sp)
            albums = list(executor.map(fetch_album_partial, albums_ids))

        return albums
    else:
        return ("Albums not found.")
    
def get_new_releases(sp):
    new_releases = sp.new_releases(limit=12)
    album_ids = [album['id'] for album in new_releases['albums']['items']]
    
    # Use ThreadPoolExecutor for concurrent execution
    with concurrent.futures.ThreadPoolExecutor() as executor:
        # Fetch album details concurrently
        fetch_album_partial = partial(fetch_album_info, sp=sp)
        albums = list(executor.map(fetch_album_partial, album_ids))

    return albums

def get_top_songs(sp):
    playlist_tracks = sp.playlist_tracks('37i9dQZEVXbMDoHDwVN2tF', limit=10)
    album_ids = [item['track']['album']['id'] for item in playlist_tracks['items']]
    # Create a list to store Album instances

    with concurrent.futures.ThreadPoolExecutor() as executor:
        # Fetch album details concurrentl
        fetch_album_partial = partial(fetch_album_info, sp=sp)
        albums = list(executor.map(fetch_album_partial, album_ids))

    return albums


#rap caviar, hot country, today's top hits, rnb weekly. top songs global, all new rock
playlist = {'name': 'Blues Classics', 'id': '37i9dQZF1DXd9rSDyQguIk'}
playlist_list = [{'name': 'Rap Caviar', 'id': '37i9dQZF1DX0XUsuxWHRQd'}, {'name': 'Hot Country', 'id': '37i9dQZF1DX1lVhptIYRda'}, {'name': 'Today\'s Top Hits', 'id': '37i9dQZF1DXcBWIGoYBM5M'}, {'name': 'Top Songs Global', 'id': '37i9dQZEVXbNG2KDcFcKOF'}, {'name': 'All New Rock', 'id': '37i9dQZF1DWZryfp6NSvtz'}, {'name': 'All New Indie', 'id': '37i9dQZF1DXdbXrPNafg9d'}, {'name': 'State of Jazz', 'id': '37i9dQZF1DX7YCknf2jT6s'}, {'name': 'All New Metal', 'id': '37i9dQZF1DX5J7FIl4q56G'}, {'name': 'Classical Essentials', 'id': '37i9dQZF1DWWEJlAGA9gs0'}, {'name': 'Viva Latino', 'id': '37i9dQZF1DX10zKzsJ2jva'}, {'name': 'Front Page Indie', 'id': '37i9dQZF1DX2Nc3B70tvx0'}, {'name': 'Blues Classics', 'id': '37i9dQZF1DXd9rSDyQguIk'}]

