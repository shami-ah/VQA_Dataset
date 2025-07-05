import os
import json
import argparse
from PIL import Image
import easyocr
from tqdm import tqdm

def enrich_metadata(img_dir, output_json):
    reader = easyocr.Reader(['ar'], verbose=False)
    metadata = {}

    for fname in tqdm(os.listdir(img_dir), desc="🧠 Enriching metadata"):
        if not fname.lower().endswith(('.jpg', '.jpeg', '.png')):
            continue
        fpath = os.path.join(img_dir, fname)
        try:
            img = Image.open(fpath)
            result = reader.readtext(img)
            text = " ".join([x[1] for x in result])
            metadata[fname] = {"text": text}
        except:
            continue

    with open(output_json, "w", encoding="utf-8") as f:
        json.dump(metadata, f, ensure_ascii=False, indent=2)
    print(f"✅ Metadata saved to {output_json}")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="🧠 Enrich OCR metadata")
    parser.add_argument("--img_dir", required=True)
    parser.add_argument("--output_json", default="metadata/arabic_image_metadata.json")

    args = parser.parse_args()
    enrich_metadata(args.img_dir, args.output_json)