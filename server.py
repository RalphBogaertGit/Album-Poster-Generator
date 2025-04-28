from flask import Flask, request, send_file, render_template
import os
import tempfile
from PIL import Image
import spotipy
from spotipy.oauth2 import SpotifyClientCredentials
from poster_generator import generate_album_poster

app = Flask(__name__)

# Spotify API credentials
client_id = "3f75e7c92ac3492cbeb1b6a5d95059ce"
client_secret = "c37ac63669e149059e2b64e80b0c00dd"

sp = spotipy.Spotify(auth_manager=SpotifyClientCredentials(client_id=client_id, client_secret=client_secret))

@app.route('/')
def index():
    return render_template('index.html')  # Zorg dat je index.html in templates-map staat

@app.route('/generate', methods=['POST'])
def generate():
    # Haal data uit formulier
    spotify_link = request.form['spotifyLink']
    genre = request.form['genre']
    spotify_code_file = request.files['spotifyCode']

    colors = []
    for i in range(1, 6):
        color_hex = request.form.get(f'color{i}')
        if color_hex:
            color_rgb = tuple(int(color_hex.lstrip('#')[j:j+2], 16) for j in (0, 2, 4))
            colors.append(color_rgb)

    # Haal album info op
    album_id = spotify_link.split("/")[-1].split("?")[0]
    album_info = sp.album(album_id)

    # Save Spotify code temporarily
    with tempfile.NamedTemporaryFile(delete=False, suffix=".png") as tmp:
        spotify_code_path = tmp.name
        spotify_code_file.save(spotify_code_path)

    # Genereer de poster
    output_path = generate_album_poster(album_info, spotify_code_path, genre, colors)

    # Stuur de PDF naar de gebruiker
    return send_file(output_path, as_attachment=True)

if __name__ == '__main__':
    app.run(debug=True)
