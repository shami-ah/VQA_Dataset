import os
import shutil
import argparse
from PIL import Image
from tqdm import tqdm
import easyocr

def is_arabic(text):
    return any('\u0600' <= c <= '\u06FF' for c in text)

def filter_arabic_images(input_dir, output_dir, min_width=200, min_height=200):
    os.makedirs(output_dir, exist_ok=True)
    reader = easyocr.Reader(['ar'], verbose=False)
    arabic_count = 0
    all_images = []

    # Recursively collect image paths
    for root, _, files in os.walk(input_dir):
        for f in files:
            if f.lower().endswith(('.jpg', '.jpeg', '.png')):
                all_images.append(os.path.join(root, f))

    for img_path in tqdm(all_images, desc="🔍 Running OCR"):
        try:
            img = Image.open(img_path)

            # Skip very small images
            if img.width < min_width or img.height < min_height:
                continue

            result = reader.readtext(img)
            extracted_text = " ".join([x[1] for x in result])

            if is_arabic(extracted_text):
                shutil.copy(img_path, os.path.join(output_dir, os.path.basename(img_path)))
                arabic_count += 1
        except:
            continue

    print(f"\n✅ OCR filtering complete. Arabic-only images saved: {arabic_count} / {len(all_images)}")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="🧠 Filter Arabic OCR Images")
    parser.add_argument("--input_dir", type=str, required=True, help="Directory of scraped images")
    parser.add_argument("--output_dir", type=str, required=True, help="Directory to save filtered images")

    args = parser.parse_args()
    filter_arabic_images(args.input_dir, args.output_dir)