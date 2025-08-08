#!/usr/bin/env python3
"""
EasyOCR for Japanese Text Detection
"""

import os
import argparse
import json
import shutil
from PIL import Image
from tqdm import tqdm
import easyocr

def contains_japanese(text):
    return any('\u3040' <= c <= '\u30FF' or '\u4E00' <= c <= '\u9FFF' for c in text)

def check_image_integrity(image_path):
    try:
        img = Image.open(image_path)
        img.verify()
        return True
    except (IOError, SyntaxError) as e:
        print(f"⚠️ Corrupted image: {image_path} - {e}")
        return False

def filter_japanese_images(input_dir, output_dir, annotation_path):
    os.makedirs(output_dir, exist_ok=True)
    reader = easyocr.Reader(['ja'], verbose=False)
    files = [f for f in os.listdir(input_dir) if f.lower().endswith(('.jpg', '.jpeg', '.png'))]
    annotations = []
    count = 0

    for fname in tqdm(files, desc="🔍 OCR Filtering (Japanese)"):
        src_path = os.path.join(input_dir, fname)
        print(f"Processing: {src_path}")
        if not check_image_integrity(src_path):
            print(f"Skipping corrupted image: {fname}")
            continue

        try:
            img = Image.open(src_path)
            result = reader.readtext(img)
            text = " ".join([t[1] for t in result if contains_japanese(t[1])])
            if text:
                dst_path = os.path.join(output_dir, fname)
                shutil.copy(src_path, dst_path)
                annotations.append({"filename": fname, "text": text})
                count += 1
        except Exception as e:
            print(f"⚠️ Error processing {fname}: {e}")

    with open(annotation_path, "w", encoding="utf-8") as f:
        json.dump(annotations, f, ensure_ascii=False, indent=2)

    print(f"\n✅ OCR complete. Japanese-text images saved: {count} / {len(files)}")
    print(f"📄 Annotations saved to: {annotation_path}")

def main():
    parser = argparse.ArgumentParser(description="EasyOCR for Japanese Text Detection")
    parser.add_argument("--input_dir", required=True, help="Directory of images to filter")
    parser.add_argument("--output_dir", required=True, help="Directory to save filtered images")
    parser.add_argument("--annotation_path", required=True, help="Path to save annotations.json")
    args = parser.parse_args()

    filter_japanese_images(args.input_dir, args.output_dir, args.annotation_path)

if __name__ == "__main__":
    main()