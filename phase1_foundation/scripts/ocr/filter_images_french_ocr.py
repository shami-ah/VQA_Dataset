import os
import argparse
import json
import shutil
import hashlib
import easyocr

from PIL import Image


def process_images(source_dir, save_dir):
    os.makedirs(save_dir, exist_ok=True)
    # Initialize EasyOCR reader for French
    lang_code = "fr"  # Hardcoded for French
    reader = easyocr.Reader([lang_code], gpu=True)
    metadata = []
    seen_hashes = set()

    for root, _, files in os.walk(source_dir):
        for fname in files:
            if not fname.lower().endswith((".png", ".jpg", ".jpeg", ".bmp", ".tiff")):
                continue
            img_path = os.path.join(root, fname)
            try:
                # Read text in paragraph mode
                text_lines = reader.readtext(img_path, detail=0, paragraph=True)
                ocr_text = " ".join(text_lines).strip()
            except Exception as e:
                print(f"⚠️ OCR error on {img_path}: {e}")
                continue

            if ocr_text:
                try:
                    # Compute file-content hash for deduplication
                    with open(img_path, 'rb') as f:
                        data = f.read()
                    hash_str = hashlib.md5(data).hexdigest()
                except Exception as e:
                    print(f"⚠️ Hash error on {img_path}: {e}")
                    continue

                if hash_str in seen_hashes:
                    # Duplicate image; skip copying
                    continue
                seen_hashes.add(hash_str)

                # Copy valid and unique image to processed directory
                rel_path = os.path.relpath(img_path, source_dir)
                dest_path = os.path.join(save_dir, rel_path)
                os.makedirs(os.path.dirname(dest_path), exist_ok=True)
                shutil.copy2(img_path, dest_path)

                # Collect metadata
                metadata.append({
                    "image_path": dest_path,
                    "ocr_text": ocr_text
                })

    # Save metadata to JSON
    meta_file = os.path.join(save_dir, "ocr_metadata_french.json")
    with open(meta_file, "w", encoding="utf-8") as f:
        json.dump(metadata, f, ensure_ascii=False, indent=2)

    print(f"✅ OCR complete: {len(metadata)} unique images with French text saved to {save_dir}")
    print(f"🔖 Metadata written to {meta_file}")


def main():
    parser = argparse.ArgumentParser(
        description="Filter and OCR French-language images using EasyOCR (hardcoded to French)"
    )
    parser.add_argument(
        "--source_dir", required=True,
        help="Directory containing raw scraped images"
    )
    parser.add_argument(
        "--save_dir", required=True,
        help="Directory to store OCR-filtered images and metadata"
    )
    args = parser.parse_args()

    process_images(args.source_dir, args.save_dir)


if __name__ == "__main__":
    main()