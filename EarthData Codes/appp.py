import logging
import streamlit as st
from flask import Flask, jsonify, render_template, send_from_directory
from werkzeug.utils import secure_filename
from flask_cors import CORS  
import os
import rasterio
import numpy as np
from PIL import Image

from pathlib import Path
app = Flask(__name__, static_folder='static', template_folder='templates')  
CORS(app)  

BASE_DIR = Path("C:/Users/ciluno1/Desktop/Javascripts-course/proposed/Earth Data")

@app.route('/')
def index():
    return render_template('index.html')  

@app.route('/get-years')
def get_years():
    years = [folder for folder in os.listdir(BASE_DIR) if os.path.isdir(os.path.join(BASE_DIR, folder))]
    return jsonify(years)

@app.route('/get-files/<year>')
def get_files(year):
    year_folder = os.path.join(BASE_DIR, year)
    if os.path.exists(year_folder):
        files = [f for f in os.listdir(year_folder) if f.endswith('.tif')]
        return jsonify(files)
    else:
        return jsonify({"error": "Year not found"}), 404

@app.route('/get-boundaries/<year>')
def get_boundaries(year):
    folder_path = os.path.join(BASE_DIR, year)
    if not os.path.exists(folder_path):
        return jsonify({"error": "Year not found"}), 404
    
    file_list = os.listdir(folder_path)
    tiff_files = [file for file in file_list if file.endswith('.tif')]

    boundaries = {}
    for tiff_file in tiff_files:
        file_path = os.path.join(folder_path, tiff_file)
        with rasterio.open(file_path) as dataset:
            transform = dataset.transform
            cols, rows = dataset.width, dataset.height
            left = transform.c
            top = transform.f
            right = left + cols * transform.a
            bottom = top + rows * transform.e
            boundaries[tiff_file] = [left, bottom, right, top]
    
    return jsonify(boundaries)

@app.route('/get-image/<year>/<filename>')
def get_image(year, filename):
    folder_path = os.path.join(BASE_DIR, year)
    if not os.path.exists(folder_path):
        return jsonify({"error": "Year not found"}), 404
    
    filename = secure_filename(filename) 
    file_path = os.path.join(folder_path, filename)
    
    try:
        with rasterio.open(file_path) as dataset:
            array = dataset.read()
            img = Image.fromarray(np.dstack(array).astype('uint8'))
            temp_filename = f"temp_{filename}.png"
            img.save(temp_filename, "PNG")
        return send_from_directory('.', temp_filename)
    except Exception as e:
        logging.error(f"Error getting years: {e}")
        return jsonify({"error": "Error getting years"}), 500

logging.basicConfig(level=logging.INFO) 

@app.route('/get_tiff/<date>', methods=['GET'])
def get_tiff(date):
    year = date[:4]
    tiff_folder = 'tiff_images' 
    tiff_filename = f"SMAP_L4_C_mdl_{date}T000000_Vv7042_001_NEE_nee_mean_c044d1b.tif"
    path = os.path.join(tiff_folder, year)

    if not os.path.exists(path):
        return jsonify({"error": "Path not found"}), 404
    
    if not os.path.isfile(os.path.join(path, tiff_filename)):
        return jsonify({"error": "File not found"}), 404
    
    return send_from_directory(path, tiff_filename)

@app.route('/data/<int:year>/<int:month>/<int:day>.tif')
def serve_tif(year, month, day):
    # Construct the file path
    file_path = f'{year}/{str(month).zfill(2)}/{str(day).zfill(2)}.tif'
    # Serve the file from the directory
    return send_from_directory('C:/Users/ciluno1/Desktop/Javascripts-course/proposed/Earth Data', file_path)

if __name__ == '__main__':
    app.run(debug=True)


