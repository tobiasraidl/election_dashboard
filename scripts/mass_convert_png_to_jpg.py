import os
from PIL import Image

# Specify the directory containing the images
directory = "../images"

# Loop through all files in the directory
for filename in os.listdir(directory):
    if filename.endswith(".png"):
        # Construct full file path
        file_path = os.path.join(directory, filename)
        
        # Open the PNG image
        with Image.open(file_path) as img:
            # Convert to RGB (required for saving as JPG)
            rgb_image = img.convert("RGB")
            
            # Save the image as JPG
            new_filename = os.path.splitext(filename)[0] + ".jpg"
            rgb_image.save(os.path.join(directory, new_filename), "JPEG")
        
        # Remove the original PNG file
        os.remove(file_path)
        print(f"Converted and removed {filename}")
