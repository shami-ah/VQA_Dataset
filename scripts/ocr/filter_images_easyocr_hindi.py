import os
import easyocr
from tqdm import tqdm
from PIL import Image

LANGUAGE = 'hi'
INPUT_DIR = "data/raw_hindi"
OUTPUT_DIR = "data/filtered_hindi"

os.makedirs(OUTPUT_DIR, exist_ok=True)
reader = easyocr.Reader([LANGUAGE], gpu=True)

def contains_text(image_path):
    try:
        results = reader.readtext(image_path)
        return len(results) > 0
    except Exception as e:
        print(f"❌ Error on {image_path}: {e}")
        return False

def filter_images():
    image_files = [
        f for f in os.listdir(INPUT_DIR) if f.lower().endswith(('.png', '.jpg', '.jpeg'))
    ]
    for fname in tqdm(image_files, desc="🔍 Filtering"):
        img_path = os.path.join(INPUT_DIR, fname)
        if contains_text(img_path):
            img = Image.open(img_path)
            img.save(os.path.join(OUTPUT_DIR, fname))
    print("✅ Filtering complete.")

if __name__ == "__main__":
    filter_images()