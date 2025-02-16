from flask_cors import CORS
from flask import Flask, request, jsonify
import cv2
import pandas as pd
import numpy as np
import os
from skimage import measure

app = Flask(__name__)
CORS(app)


def detect_skin_tone(image):
    lab = cv2.cvtColor(image, cv2.COLOR_BGR2LAB)
    avg_l = np.mean(lab[:, :, 0])
    avg_a = np.mean(lab[:, :, 1])
    avg_b = np.mean(lab[:, :, 2])
    
    if avg_l > 180 and avg_b > 130:
        return "Fair"
    elif 130 < avg_l <= 180 and 110 < avg_b <= 130:
        return "Medium"
    else:
        return "Dark"

def detect_oiliness(image):
    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    blurred = cv2.GaussianBlur(gray, (5, 5), 0)
    _, thresh = cv2.threshold(blurred, 200, 255, cv2.THRESH_BINARY)
    oiliness_ratio = np.sum(thresh == 255) / thresh.size
    return "Oily" if oiliness_ratio > 0.2 else "Dry"

def detect_redness(image):
    hsv = cv2.cvtColor(image, cv2.COLOR_BGR2HSV)
    lower_red1 = np.array([0, 50, 50])
    upper_red1 = np.array([10, 255, 255])
    lower_red2 = np.array([170, 50, 50])
    upper_red2 = np.array([180, 255, 255])
    mask1 = cv2.inRange(hsv, lower_red1, upper_red1)
    mask2 = cv2.inRange(hsv, lower_red2, upper_red2)
    mask = cv2.add(mask1, mask2)
    redness_ratio = np.sum(mask == 255) / mask.size
    redness_percentage = redness_ratio * 100
    
    if redness_percentage > 15:
        return "Severe"
    elif redness_percentage > 5:
        return "Moderate"
    else:
        return "Low"

def detect_pimples(image):
    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    blurred = cv2.GaussianBlur(gray, (5, 5), 0)
    _, binary = cv2.threshold(blurred, 120, 255, cv2.THRESH_BINARY_INV)
    labels = measure.label(binary, connectivity=2, background=0)
    num_pimples = np.max(labels)
    
    if num_pimples > 20:
        return "Severe"
    elif num_pimples > 10:
        return "Moderate"
    elif num_pimples > 0:
        return "Mild"
    else:
        return "None"

def detect_open_pores(image):
    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    blurred = cv2.GaussianBlur(gray, (9, 9), 2)
    edges = cv2.Canny(blurred, 10, 50)
    contours, _ = cv2.findContours(edges, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    pore_count = len(contours)
    
    if pore_count > 100:
        return "Severe"
    elif pore_count > 50:
        return "Moderate"
    else:
        return "Low"

def analyze_image(image_path):
    if not os.path.exists(image_path):
        return {"error": "Image file not found"}
    
    image = cv2.imread(image_path)
    if image is None:
        return {"error": "Invalid image"}
    
    return {
        "skinTone": detect_skin_tone(image),
        "oiliness": detect_oiliness(image),
        "redness": detect_redness(image),
        "pimples": detect_pimples(image),
        "openPores": detect_open_pores(image)
    }

@app.route('/analyze', methods=['POST'])
def analyze():
    data = request.json
    image_path = data.get('imagePath')
    result = analyze_image(image_path)
    return jsonify(result)

if __name__ == '__main__':
    app.run(port=5001, debug=True)
