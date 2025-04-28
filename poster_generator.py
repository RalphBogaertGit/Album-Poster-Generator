from reportlab.lib.pagesizes import A4
from reportlab.pdfgen import canvas
from reportlab.lib import colors as rl_colors
import requests
from io import BytesIO
from PIL import Image
import tempfile
import re
import os
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from index import album_info, code_link

# Layout parameters
LEFT_MARGIN = 85
RIGHT_MARGIN = 90
TITLE_FONT_SIZE = 22
INFO_Y_POS = 100
TITLE_Y_POS = 345
ARTIST_FONT_SIZE = 18
TEXT_FONT_SIZE = 10
COVER_WIDTH = 424  # Width of the album cover image
COVER_HEIGHT = 424  # Height of the album cover image
COVER_Y_POS = 370  # Vertical position of the album cover
TRACKS_Y_START = 400  # Adjusted vertical position for track listings
COLOR_BOX_SIZE = 30
COLOR_BOX_SPACING = 10  # Space between color boxes
COLORS_Y_POS = 70  # Position for the color boxes
SPOTIFY_CODE_POS = 50  # Position for the Spotify Code
TRACK_POS = LEFT_MARGIN

def extract_dominant_colors(image, num_colors=5):
    image = image.resize((100, 100))
    result = image.convert("RGB").getcolors(10000)
    sorted_colors = sorted(result, key=lambda x: -x[0])[:num_colors]
    return [color[1] for color in sorted_colors]

def validate_and_adjust_colors(colors_extracted):
    print("Extracted Dominant Colors:")
    for i, color in enumerate(colors_extracted):
        print(f"{i + 1}: RGB{color}")

    # Ask if the user wants to change any of the colors
    choice = input("Do you want to keep all these colors? (y/n): ").strip().lower()
    if choice == 'y':
        return colors_extracted  # Return the original colors if the user is satisfied

    # User provides custom colors if not satisfied
    validated_colors = []
    for i, color in enumerate(colors_extracted):
        while True:
            rgb_input = input(f"Enter new RGB values for color {i + 1} (e.g., 255,128,64): ")
            try:
                r, g, b = map(int, rgb_input.split(','))
                if 0 <= r <= 255 and 0 <= g <= 255 and 0 <= b <= 255:
                    validated_colors.append((r, g, b))
                    break
                else:
                    print("RGB values must be between 0 and 255.")
            except ValueError:
                print("Invalid format. Please enter three integers separated by commas.")

    return validated_colors


def generate_album_poster(album_info, spotify_code_path, genre, validated_colors):
    # Create the "posters" directory if it does not exist
    if not os.path.exists("posters"):
        os.makedirs("posters")

    pdf_filename = f"posters/{re.sub(r'[<>:\"/\\|?*]', '_', album_info['name'].upper())}_poster.pdf"
    pdfmetrics.registerFont(TTFont('AptosDisplay-Bold', 'aptos-display-bold.ttf'))

    # Fetch album cover
    cover_url = album_info['images'][0]['url']
    response = requests.get(cover_url)
    cover_image = Image.open(BytesIO(response.content))

    if not validated_colors:
        colors_extracted = extract_dominant_colors(cover_image)
        validated_colors = colors_extracted

    total_duration_ms = sum(track['duration_ms'] for track in album_info['tracks']['items'])
    total_minutes = total_duration_ms // 60000
    total_seconds = (total_duration_ms // 1000) % 60

    c = canvas.Canvas(pdf_filename, pagesize=A4)
    c.setFillColor(rl_colors.white)
    c.rect(0, 0, A4[0], A4[1], fill=1)

    # Title using custom font
    c.setFont("AptosDisplay-Bold", TITLE_FONT_SIZE)
    c.setFillColor(rl_colors.black)
    c.drawString(LEFT_MARGIN, TITLE_Y_POS, f"{album_info['name'].upper()}")

    # Artist using custom font
    c.setFont("AptosDisplay-Bold", ARTIST_FONT_SIZE)
    c.setFillColor(rl_colors.black)
    c.drawString(LEFT_MARGIN, 320, f"{album_info['artists'][0]['name'].upper()}")

    # Info positions
    middle_position = (A4[0] - LEFT_MARGIN - RIGHT_MARGIN) / 2 + LEFT_MARGIN
    right_position = A4[0] - RIGHT_MARGIN

    # Release Date aligned left
    c.setFont("AptosDisplay-Bold", TEXT_FONT_SIZE)
    c.drawString(LEFT_MARGIN, INFO_Y_POS, f"{total_minutes}:{total_seconds:02}")

    # Style centered
    c.drawCentredString(middle_position, INFO_Y_POS, f"{genre}")

    # Duration aligned right
    c.drawRightString(right_position, INFO_Y_POS, f"{album_info['release_date'].upper()}")

    # Album Cover
    with tempfile.NamedTemporaryFile(suffix=".png", delete=False) as temp_file:
        cover_image.save(temp_file.name, format="PNG")
        temp_path = temp_file.name
    c.drawImage(temp_path, LEFT_MARGIN, COVER_Y_POS, COVER_WIDTH, COVER_HEIGHT)

    # Spotify Code
    # Spotify Code
    spotify_code_img = Image.open(spotify_code_path)

    with tempfile.NamedTemporaryFile(suffix=".png", delete=False) as temp_file:
        spotify_code_img.save(temp_file.name, format="PNG")
        temp_path = temp_file.name

    c.drawImage(temp_path, A4[0] - RIGHT_MARGIN - 170, SPOTIFY_CODE_POS, 180, 45)


    # Tracks in two columns
    num_tracks = len(album_info['tracks']['items'])
    column_break = num_tracks // 2 + num_tracks % 2
    column_width = (A4[0] - LEFT_MARGIN - RIGHT_MARGIN) / 2
    track_y = 300
    TRACK_POS = LEFT_MARGIN

    for i, track in enumerate(album_info['tracks']['items'], 1):
        cleaned_track = track['name'].split('-')[0]
        current_track_pos = TRACK_POS
        if i == column_break + 1:
            track_y = 300
            TRACK_POS = LEFT_MARGIN + column_width + 40
            current_track_pos = TRACK_POS

        c.drawString(current_track_pos, track_y, f"{i}. {cleaned_track.upper()}")
        track_y -= 18

    # Dominant Colors Display with rounded corners
    x_offset = LEFT_MARGIN
    for i, color in enumerate(validated_colors):
        rgb_color = rl_colors.Color(color[0] / 255, color[1] / 255, color[2] / 255)
        c.setFillColor(rgb_color)
        c.roundRect(x_offset , SPOTIFY_CODE_POS + 8, COLOR_BOX_SIZE, COLOR_BOX_SIZE, 5, fill=1, stroke=0)  # 5 is the radius for rounded corners
        x_offset += COLOR_BOX_SIZE + COLOR_BOX_SPACING

    c.save()
    print(f"Poster saved as {pdf_filename}")
    return pdf_filename

# Example usage

# generate_album_poster(album_info, f"codes/{code_link}.jpeg")
