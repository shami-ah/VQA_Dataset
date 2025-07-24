import os
import json
import cv2
from tqdm import tqdm
import easyocr
import argparse

# Initialize EasyOCR reader with Malay
reader = easyocr.Reader(['ms'], gpu=False)

def has_watermark(image):
    h, w = image.shape[:2]
    roi = image[0:int(h * 0.15), int(w * 0.7):w]
    gray = cv2.cvtColor(roi, cv2.COLOR_BGR2GRAY)
    edges = cv2.Canny(gray, 100, 200)
    return cv2.countNonZero(edges) > 0.1 * edges.size

def is_high_quality(image):
    height, width = image.shape[:2]
    return width >= 400 and height >= 400

def extract_text(image):
    result = reader.readtext(image)
    return " ".join([item[1] for item in result]).strip()

def process_images(input_dir, output_dir):
    os.makedirs(output_dir, exist_ok=True)
    skipped_log = []
    annotations = {}
    image_files = [f for f in os.listdir(input_dir) if f.lower().endswith(('.jpg', '.jpeg', '.png'))]
    count = 1

    for filename in tqdm(sorted(image_files), desc="Processing images"):
        image_path = os.path.join(input_dir, filename)
        image = cv2.imread(image_path)

        if image is None:
            skipped_log.append((filename, "Unreadable image"))
            continue

        if not is_high_quality(image):
            skipped_log.append((filename, "Low quality"))
            continue

        if has_watermark(image):
            skipped_log.append((filename, "Watermark detected"))
            continue

        text = extract_text(image)
        if not text:
            skipped_log.append((filename, "No Malay text detected"))
            continue

        out_name = f"{count:02d}.jpg"
        out_path = os.path.join(output_dir, out_name)
        cv2.imwrite(out_path, image)
        annotations[out_name] = text
        count += 1

    # Save annotations
    with open(os.path.join(output_dir, "annotation.json"), "w", encoding='utf-8') as f:
        json.dump(annotations, f, ensure_ascii=False, indent=2)

    # Save skipped logs
    with open(os.path.join(output_dir, "skipped_log.txt"), "w", encoding='utf-8') as f:
        for item in skipped_log:
            f.write(f"{item[0]}: {item[1]}\n")

    print(f"\n✅ Done! Saved {count - 1} images and annotation.json in {output_dir}")
    print(f"ℹ️ Skipped {len(skipped_log)} images. Reasons logged in skipped_log.txt")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Malay OCR Image Filter with EasyOCR")
    parser.add_argument("--input_dir", required=True, help="Raw images folder")
    parser.add_argument("--output_dir", required=True, help="Filtered output folder")
    args = parser.parse_args()

    process_images(args.input_dir, args.output_dir)