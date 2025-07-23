import os
import json
import pytesseract
import cv2
from PIL import Image
from tqdm import tqdm
import re
import argparse

# Hardcoded language: Bengali
OCR_LANG = 'ben'
pytesseract.pytesseract.tesseract_cmd = 'tesseract'

def is_bengali(text):
    return len(re.findall(r'[\u0980-\u09FF]', text)) >= 5

def has_watermark(image):
    h, w = image.shape[:2]
    roi = image[0:int(h * 0.15), int(w * 0.7):w]
    gray = cv2.cvtColor(roi, cv2.COLOR_BGR2GRAY)
    edges = cv2.Canny(gray, 100, 200)
    return cv2.countNonZero(edges) > 0.1 * edges.size

def is_high_quality(image):
    height, width = image.shape[:2]
    return width >= 400 and height >= 400

def process_images(input_dir, output_dir):
    os.makedirs(output_dir, exist_ok=True)
    annotations = {}
    image_files = [f for f in os.listdir(input_dir) if f.lower().endswith(('.jpg', '.jpeg', '.png'))]
    count = 1

    for filename in tqdm(sorted(image_files), desc="Processing images"):
        image_path = os.path.join(input_dir, filename)
        image = cv2.imread(image_path)

        if image is None or not is_high_quality(image) or has_watermark(image):
            continue

        text = pytesseract.image_to_string(Image.fromarray(image), lang=OCR_LANG).strip()

        if is_bengali(text):
            out_name = f"{count:02d}.jpg"
            out_path = os.path.join(output_dir, out_name)
            cv2.imwrite(out_path, image)
            annotations[out_name] = text
            count += 1

    # Save annotation.json in the same processed folder
    annotation_path = os.path.join(output_dir, "annotation.json")
    with open(annotation_path, "w", encoding='utf-8') as f:
        json.dump(annotations, f, ensure_ascii=False, indent=2)

    print(f"\n✅ Done! Saved {count - 1} images and annotation.json in {output_dir}")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Bengali OCR Image Filter")
    parser.add_argument("--input_dir", required=True, help="Raw images folder")
    parser.add_argument("--output_dir", required=True, help="Filtered output folder")
    args = parser.parse_args()

    process_images(args.input_dir, args.output_dir)