import os
import shutil
import argparse
import json
from PIL import Image
from tqdm import tqdm
import easyocr

def is_arabic(text):
    return any('\u0600' <= c <= '\u06FF' for c in text)

def filter_arabic_images(input_dir, output_dir, annotation_path):
    os.makedirs(output_dir, exist_ok=True)
    annotations = []
    reader = easyocr.Reader(['ar'], verbose=False)

    # Recursive image file search
    files = []
    for root, _, filenames in os.walk(input_dir):
        for fname in filenames:
            if fname.lower().endswith(('.jpg', '.jpeg', '.png')):
                files.append(os.path.join(root, fname))

    arabic_count = 0
    for src_path in tqdm(files, desc="🔍 Running OCR"):
        try:
            img = Image.open(src_path)
            result = reader.readtext(img)
            text = " ".join([x[1] for x in result])

            if is_arabic(text):
                dst_path = os.path.join(output_dir, os.path.basename(src_path))
                shutil.copy(src_path, dst_path)

                annotations.append({
                    "filename": os.path.basename(src_path),
                    "text": text
                })
                arabic_count += 1
        except Exception as e:
            print(f"⚠️ Error on {src_path}: {e}")
            continue

    with open(annotation_path, "w", encoding="utf-8") as f:
        json.dump(annotations, f, indent=2, ensure_ascii=False)

    print(f"\n✅ OCR filtering complete. Arabic-only images saved: {arabic_count} / {len(files)}")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="🧠 Filter Arabic Images with EasyOCR")
    parser.add_argument("--input_dir", type=str, required=True, help="Directory of scraped images")
    parser.add_argument("--output_dir", type=str, required=True, help="Where to save filtered Arabic images")
    args = parser.parse_args()

    annotation_path = os.path.join(args.output_dir, "annotations.json")
    filter_arabic_images(args.input_dir, args.output_dir, annotation_path)