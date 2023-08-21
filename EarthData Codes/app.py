# Importing required libraries and modules
from flask import Flask, render_template, jsonify, send_from_directory
import os
import rasterio
from PIL import Image
import numpy as np
from werkzeug.utils import secure_filename

# Initializing the Flask application
app = Flask(__name__)

# Route to serve the main index page
@app.route('/')
def index():
    return render_template('index.html')

# Route to get boundaries of all .tif files in a specific directory
@app.route('/get-boundaries')
def get_boundaries():
    # Define the path where the .tif files are stored
    folder_path = r'C:\Users\ciluno1\Documents\Earth Data\2016'
    
    # Get a list of all files in the directory
    file_list = os.listdir(folder_path)
    
    # Filter out only the .tif files
    tiff_files = [file for file in file_list if file.endswith('.tif')]

    boundaries = {}
    # Loop through each .tif file to extract its boundaries
    for tiff_file in tiff_files:
        file_path = os.path.join(folder_path, tiff_file)
        
        with rasterio.open(file_path) as dataset:
            transform = dataset.transform
            cols, rows = dataset.width, dataset.height
            
            # Extracting the boundaries of the image
            left = transform.c
            top = transform.f
            right = left + cols * transform.a
            bottom = top + rows * transform.e
            
            # Saving boundaries in the format Leaflet expects: [SouthWest, NorthEast]
            boundaries[tiff_file] = [left, bottom, right, top]

    # Return the boundaries as a JSON response
    return jsonify(boundaries)

# Route to get a specific image and convert it to PNG format
@app.route('/get-image/<filename>')
def get_image(filename):
    folder_path = r'C:\Users\ciluno1\Documents\Earth Data\2016'
    
    # Ensuring the filename is secure to prevent potential security risks
    filename = secure_filename(filename)
    file_path = os.path.join(folder_path, filename)

    try:
        # Open the .tif file with rasterio
        with rasterio.open(file_path) as dataset:
            array = dataset.read()
            
            # Convert the raster data to an image using PIL
            img = Image.fromarray(np.dstack(array))
            
            # Saving the image as a temporary PNG file
            temp_filename = f"temp_{filename}.png"
            img.save(temp_filename, "PNG")
        
        # Sending the PNG image as a response
        return send_from_directory('.', temp_filename)
    except Exception as e:
        # If there's an error, print it for troubleshooting and return an error response
        print(f"Error processing {filename}: {e}")
        return str(e), 500

# Running the Flask application
if __name__ == '__main__':
    app.run(debug=True)
