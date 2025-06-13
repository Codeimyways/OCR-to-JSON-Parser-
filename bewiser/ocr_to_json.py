import pytesseract
from PIL import Image
import json
import sys
from pdf2image import convert_from_path
import re
import os

def extract_text(image):
    raw_text = pytesseract.image_to_string(image)
    cleaned_text = re.sub(r'\s+', ' ', raw_text).strip()
    return cleaned_text

def detect_key_values(text):
    keys = ["Date", "Total", "Invoice", "Amount", "Name"]
    kv_pairs = {}
    for key in keys:
        match = re.search(rf'{key}[:\-]?\s*([\w\d./-]+)', text, re.IGNORECASE)
        if match:
            kv_pairs[key.lower()] = match.group(1)
    return kv_pairs

def process_file(path):
    ext = os.path.splitext(path)[1].lower()
    if ext == ".pdf":
        images = convert_from_path(path)
    else:
        images = [Image.open(path)]

    full_text = ""
    for img in images:
        full_text += extract_text(img) + " "

    result = {
        "raw_text": full_text.strip(),
        "key_values": detect_key_values(full_text)
    }

    with open("output.json", "w") as f:
        json.dump(result, f, indent=2)
    print("✅ Output saved to output.json")

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python ocr_to_json.py <image_or_pdf_path>")
    else:
        process_file(sys.argv[1])
