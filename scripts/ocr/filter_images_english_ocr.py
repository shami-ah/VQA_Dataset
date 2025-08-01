#!/usr/bin/env python3
import os
import argparse
import json
import shutil
import hashlib
import easyocr

from PIL import Image


def process_images(source_dir, save_dir):
    """
    OCR-filter English-language images, deduplicate, and save metadata.
    Only images containing English text are copied to save_dir, with OCR text in JSON.
    """
    os.makedirs(save_dir, exist_ok=True)

    # Initialize English EasyOCR reader
    reader = easyocr.Reader(['en'], gpu=True)
    seen_hashes = set()
    metadata = []

    for root, _, files in os.walk(source_dir):
        for fname in files:
            if not fname.lower().endswith(('.png', '.jpg', '.jpeg', '.bmp', '.tiff')):
                continue
            img_path = os.path.join(root, fname)

            # OCR
            try:
                lines = reader.readtext(img_path, detail=0, paragraph=True)
                ocr_text = " ".join(lines).strip()
            except Exception as e:
                print(f"⚠️ OCR error on {img_path}: {e}")
                continue

            if not ocr_text:
                continue

            # Deduplicate by content hash
            try:
                with open(img_path, 'rb') as f:
                    h = hashlib.md5(f.read()).hexdigest()
            except Exception as e:
                print(f"⚠️ Hash error on {img_path}: {e}")
                continue

            if h in seen_hashes:
                continue
            seen_hashes.add(h)

            # Copy and record
            rel = os.path.relpath(img_path, source_dir)
            dest = os.path.join(save_dir, rel)
            os.makedirs(os.path.dirname(dest), exist_ok=True)
            shutil.copy2(img_path, dest)
            metadata.append({'image_path': dest, 'ocr_text': ocr_text})

    # Write metadata
    out_file = os.path.join(save_dir, 'ocr_metadata_english.json')
    with open(out_file, 'w', encoding='utf-8') as f:
        json.dump(metadata, f, ensure_ascii=False, indent=2)

    print(f"✅ OCR complete: {len(metadata)} images with English text saved to {save_dir}")
    print(f"🔖 Metadata at {out_file}")


def main():
    parser = argparse.ArgumentParser(
        description='Filter and OCR English images using EasyOCR.'
    )
    parser.add_argument(
        '--source_dir', required=True,
        help='Directory of raw images'
    )
    parser.add_argument(
        '--save_dir', required=True,
        help='Directory for OCR-filtered images and metadata'
    )
    args = parser.parse_args()
    process_images(args.source_dir, args.save_dir)

if __name__ == '__main__':
    main()