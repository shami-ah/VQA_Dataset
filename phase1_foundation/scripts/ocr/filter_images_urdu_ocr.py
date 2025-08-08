import os
import json
import argparse
import hashlib
from PIL import Image
import easyocr
from tqdm import tqdm
import warnings
import torch

# Suppress irrelevant MPS pin_memory warnings
warnings.filterwarnings("ignore", message="'pin_memory' argument is set as true but not supported on MPS")

def get_image_hash(image_path):
    with open(image_path, "rb") as f:
        return hashlib.sha256(f.read()).hexdigest()

def is_low_resolution(image, min_width=500, min_height=500):
    return image.width < min_width or image.height < min_height

def run_ocr_filter(input_dir, output_dir, annotation_path):
    os.makedirs(output_dir, exist_ok=True)
    annotations = {}
    seen_hashes = set()
    counter = 1

    reader = easyocr.Reader(['ur'], gpu=torch.cuda.is_available())

    # Gather all valid image files first
    valid_files = []
    for root, _, files in os.walk(input_dir):
        for file in sorted(files):
            if file.lower().endswith(('.jpg', '.jpeg', '.png', '.bmp', '.webp')):
                valid_files.append(os.path.join(root, file))

    for idx, img_path in enumerate(tqdm(valid_files, desc="🔍 OCR Processing", unit="image")):
        try:
            image_hash = get_image_hash(img_path)
            if image_hash in seen_hashes:
                continue  # skip duplicate

            img = Image.open(img_path)
            if is_low_resolution(img):
                continue  # skip low-quality image

            results = reader.readtext(img_path, detail=0)
            urdu_text = " ".join([line for line in results if line.strip()])

            if urdu_text:
                new_filename = f"{counter:03}.jpg"
                new_img_path = os.path.join(output_dir, new_filename)

                img.save(new_img_path, format="JPEG", quality=100, optimize=True)

                annotations[new_filename] = urdu_text
                seen_hashes.add(image_hash)
                counter += 1

        except Exception as e:
            print(f"❌ Error processing {img_path}: {e}")

    with open(annotation_path, "w", encoding="utf-8") as f:
        json.dump(annotations, f, ensure_ascii=False, indent=2)

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="OCR Filter for Urdu Images")
    parser.add_argument("--input_dir", type=str, required=True)
    parser.add_argument("--output_dir", type=str, required=True)
    args = parser.parse_args()

    annotation_file = os.path.join(args.output_dir, "annotation.json")
    run_ocr_filter(args.input_dir, args.output_dir, annotation_file)