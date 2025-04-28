import spotipy
from spotipy.oauth2 import SpotifyOAuth


# Configuratie
client_id = "3f75e7c92ac3492cbeb1b6a5d95059ce"
client_secret = "c37ac63669e149059e2b64e80b0c00dd"
redirect_uri = "http://localhost:8080/callback"

# Spotify API authenticatie
sp = spotipy.Spotify(auth_manager=SpotifyOAuth(
    client_id=client_id,
    client_secret=client_secret,
    redirect_uri=redirect_uri,
    scope="user-library-read"
))

album_url = "https://open.spotify.com/album/0ETFjACtuP2ADo6LFhL6HN?si=Hxo06H5JTyuaSAj57xyYMQ"
album_id = album_url.split("/")[-1].split("?")[0]
album_info = sp.album(album_id)

code_link = f"{album_info['name']}"
