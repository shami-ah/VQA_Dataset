import os
import shutil
import argparse
import json
from PIL import Image
from tqdm import tqdm
import easyocr

def contains_korean(text):
    return any('\uac00' <= c <= '\ud7af' for c in text)

def is_high_resolution(img, min_width=300, min_height=300):
    return img.width >= min_width and img.height >= min_height

def filter_korean_images(input_dir, output_dir, annotations_path):
    os.makedirs(output_dir, exist_ok=True)
    reader = easyocr.Reader(['ko'], verbose=False)

    files = [f for f in os.listdir(input_dir) if f.lower().endswith(('.jpg', '.jpeg', '.png'))]
    annotations = {}
    count = 0

    for fname in tqdm(files, desc="🔍 OCR Filtering (Korean)"):
        src_path = os.path.join(input_dir, fname)
        try:
            img = Image.open(src_path)
            if not is_high_resolution(img):
                continue

            result = reader.readtext(img)
            text = " ".join([x[1] for x in result if contains_korean(x[1])])

            if text.strip():
                new_name = f"korean_{count:04}.jpg"
                dst_path = os.path.join(output_dir, new_name)
                img.save(dst_path)
                annotations[new_name] = text.strip()
                count += 1
        except Exception:
            continue

    with open(os.path.join(output_dir, annotations_path), "w", encoding="utf-8") as f:
        json.dump(annotations, f, ensure_ascii=False, indent=2)

    print(f"\n✅ OCR complete. Korean-text images saved: {count} / {len(files)}")
    print(f"📝 Annotations saved to: {annotations_path}")

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--input_dir", type=str, required=True, help="Directory with raw images")
    parser.add_argument("--output_dir", type=str, required=True, help="Directory for processed images")
    parser.add_argument("--annotations_path", type=str, default="annotations.json", help="JSON filename for OCR results")
    args = parser.parse_args()

    filter_korean_images(args.input_dir, args.output_dir, args.annotations_path)