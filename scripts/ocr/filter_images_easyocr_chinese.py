import os
import shutil
import argparse
import json
from PIL import Image
from tqdm import tqdm
import warnings
warnings.filterwarnings("ignore", message=".*pin_memory.*")
import easyocr

def contains_chinese(text):
    return any('\u4e00' <= c <= '\u9fff' for c in text)

def normalize_text(text):
    return "".join(c for c in text if c.isalnum())

def filter_chinese_images(input_dir, output_dir):
    os.makedirs(output_dir, exist_ok=True)
    reader = easyocr.Reader(['ch_sim'], verbose=False)

    seen_texts = set()
    annotations = []
    chinese_count = 0

    files = [f for f in os.listdir(input_dir) if f.lower().endswith(('.jpg', '.jpeg', '.png'))]

    for fname in tqdm(files, desc="🔍 OCR Filtering (Chinese)"):
        src_path = os.path.join(input_dir, fname)
        try:
            img = Image.open(src_path)
            result = reader.readtext(img)
            text = " ".join([x[1] for x in result])
            norm_text = normalize_text(text)

            if contains_chinese(text) and norm_text not in seen_texts:
                seen_texts.add(norm_text)

                dst_path = os.path.join(output_dir, fname)
                shutil.copy(src_path, dst_path)
                chinese_count += 1

                annotations.append({
                    "image_filename": fname,
                    "ocr_text": text.strip()
                })
        except Exception as e:
            print(f"⚠️ Error processing {fname}: {e}")
            continue

    # Write to annotations.json inside processed_dir
    annotations_path = os.path.join(output_dir, "annotations.json")
    with open(annotations_path, "w", encoding="utf-8") as f:
        json.dump(annotations, f, ensure_ascii=False, indent=2)

    print(f"\n✅ OCR complete. Chinese-text images saved: {chinese_count} / {len(files)}")
    print(f"📄 Annotations saved to: {annotations_path}")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="🔍 Filter Chinese images using EasyOCR")
    parser.add_argument("--input_dir", type=str, required=True)
    parser.add_argument("--output_dir", type=str, required=True)
    args = parser.parse_args()

    filter_chinese_images(args.input_dir, args.output_dir)