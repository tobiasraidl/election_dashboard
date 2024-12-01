import os
import base64
import dash_bootstrap_components as dbc
from dash import html, dcc, callback


def load_image(img_hash):
    imgfile = f'images/{img_hash}.jpg'
    if os.path.exists(imgfile):
        with open(imgfile, "rb") as image_file:
            img_data = base64.b64encode(image_file.read())
            img_data = img_data.decode()
            img_data = "{}{}".format("data:image/jpg;base64, ", img_data)
    else:
        img_data = 'assets/placeholder.jpg'
        
    return img_data

def generate_image_grid(image_hashes):
    image_urls = [load_image(image_hash) for image_hash in image_hashes]
    # Create a list to hold rows
    rows = []

    # Loop through image URLs and group them in pairs
    for i in range(0, len(image_urls), 2):
        # Create a row with up to two columns (images)
        row = dbc.Row(
            [
                dbc.Col(
                    html.Img(
                        src=image_urls[i],
                        id={"type": "image", "index": image_hashes[i]},
                        style={'width': '100%', 'height': 'auto', 'object-fit': 'contain'}
                    ),
                    width=6
                ),
                dbc.Col(
                    html.Img(
                        src=image_urls[i + 1], 
                        id={"type": "image", "index": image_hashes[i]},
                        style={'width': '100%', 'height': 'auto', 'object-fit': 'contain'}
                    ),
                    width=6
                ) if i + 1 < len(image_urls) else None
            ],
            className="mb-3"
        )
        rows.append(row)

    return rows
