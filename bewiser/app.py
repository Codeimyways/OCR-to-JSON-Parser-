import os
import pytesseract
from flask import Flask, request, render_template, jsonify
from PIL import Image
from pdf2image import convert_from_path
import re
import uuid

app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = 'uploads'
os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)

def extract_text(image):
    raw_text = pytesseract.image_to_string(image)
    cleaned = re.sub(r'\s+', ' ', raw_text).strip()
    return cleaned

def detect_key_values(text):
    keys = ["Date", "Total", "Invoice", "Amount", "Name"]
    kv = {}
    for key in keys:
        match = re.search(rf'{key}[:\-]?\s*([\w\d./-]+)', text, re.IGNORECASE)
        if match:
            kv[key.lower()] = match.group(1)
    return kv

@app.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'POST':
        file = request.files['document']
        if not file:
            return "No file uploaded.", 400

        filename = str(uuid.uuid4()) + os.path.splitext(file.filename)[1]
        filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        file.save(filepath)

        text = ""
        ext = os.path.splitext(filename)[1].lower()

        try:
            if ext == '.pdf':
                images = convert_from_path(filepath)
            else:
                images = [Image.open(filepath)]

            for img in images:
                text += extract_text(img) + " "

            output = {
                "raw_text": text.strip(),
                "key_values": detect_key_values(text)
            }

            return jsonify(output)

        except Exception as e:
            return jsonify({"error": str(e)})

    return render_template('index.html')

if __name__ == '__main__':
    app.run(debug=True)
