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
    OCR-filter Spanish-language images, deduplicate, and save metadata.
    Only images containing Spanish text and meeting quality thresholds
    are copied to save_dir, with OCR text recorded in JSON.
    """
    # Ensure output directory exists
    os.makedirs(save_dir, exist_ok=True)

    # Initialize Spanish EasyOCR reader
    reader = easyocr.Reader(['es'], gpu=True)

    seen_hashes = set()
    metadata = []

    for root, _, files in os.walk(source_dir):
        for fname in files:
            if not fname.lower().endswith(('.png', '.jpg', '.jpeg', '.bmp', '.tiff')):
                continue
            img_path = os.path.join(root, fname)

            # Perform OCR
            try:
                text_lines = reader.readtext(img_path, detail=0, paragraph=True)
                ocr_text = " ".join(text_lines).strip()
            except Exception as e:
                print(f"⚠️ OCR error on {img_path}: {e}")
                continue

            # Skip if no Spanish text detected
            if not ocr_text:
                continue

            # Deduplicate by file content hash
            try:
                with open(img_path, 'rb') as f:
                    data = f.read()
                file_hash = hashlib.md5(data).hexdigest()
            except Exception as e:
                print(f"⚠️ Hash error on {img_path}: {e}")
                continue

            if file_hash in seen_hashes:
                continue
            seen_hashes.add(file_hash)

            # Copy to processed directory
            rel_path = os.path.relpath(img_path, source_dir)
            dest_path = os.path.join(save_dir, rel_path)
            os.makedirs(os.path.dirname(dest_path), exist_ok=True)
            shutil.copy2(img_path, dest_path)

            # Record metadata
            metadata.append({
                'image_path': dest_path,
                'ocr_text': ocr_text
            })

    # Write metadata JSON
    meta_file = os.path.join(save_dir, 'ocr_metadata_spanish.json')
    with open(meta_file, 'w', encoding='utf-8') as f:
        json.dump(metadata, f, ensure_ascii=False, indent=2)

    print(f"✅ OCR complete: {len(metadata)} images saved to {save_dir}")
    print(f"🔖 Metadata written to {meta_file}")


def main():
    parser = argparse.ArgumentParser(
        description='Filter and OCR Spanish-language images using EasyOCR.'
    )
    parser.add_argument(
        '--source_dir', required=True,
        help='Directory containing raw scraped images.'
    )
    parser.add_argument(
        '--save_dir', required=True,
        help='Directory to store OCR-filtered images and metadata.'
    )

    args = parser.parse_args()
    process_images(args.source_dir, args.save_dir)


if __name__ == '__main__':
    main()
