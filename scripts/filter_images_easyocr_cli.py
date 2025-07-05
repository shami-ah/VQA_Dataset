import os
import shutil
import argparse
from PIL import Image
from tqdm import tqdm
import easyocr

def filter_arabic_images(input_dir, output_dir):
    os.makedirs(output_dir, exist_ok=True)
    reader = easyocr.Reader(['ar'], verbose=False)

    files = [f for f in os.listdir(input_dir) if f.lower().endswith(('.jpg', '.jpeg', '.png'))]
    arabic_count = 0

    for fname in tqdm(files, desc="🔍 Running OCR"):
        src_path = os.path.join(input_dir, fname)
        try:
            img = Image.open(src_path)
            result = reader.readtext(img)
            text = " ".join([x[1] for x in result])

            if any('\u0600' <= c <= '\u06FF' for c in text):
                shutil.copy(src_path, os.path.join(output_dir, fname))
                arabic_count += 1
        except:
            continue

    print(f"\n✅ OCR filtering complete. Arabic-only images saved: {arabic_count} / {len(files)}")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="🧠 Filter Arabic OCR Images")
    parser.add_argument("--input_dir", type=str, required=True, help="Directory of scraped images")
    parser.add_argument("--output_dir", type=str, required=True, help="Directory to save filtered images")

    args = parser.parse_args()
    filter_arabic_images(args.input_dir, args.output_dir)