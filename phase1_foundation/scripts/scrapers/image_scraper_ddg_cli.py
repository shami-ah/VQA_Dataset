import os
import requests
import argparse
try:
    from ddgs import DDGS
except ImportError:
    from duckduckgo_search import DDGS
from PIL import Image
from io import BytesIO
from tqdm import tqdm

def scrape_images(keywords, save_dir, max_images, images_per_keyword):
    os.makedirs(save_dir, exist_ok=True)
    index = 0

    with DDGS() as ddgs:
        for keyword in tqdm(keywords, desc="🔍 Scraping Keywords"):
            try:
                results = ddgs.images(keywords=keyword, max_results=images_per_keyword)
                for r in results:
                    if index >= max_images:
                        return
                    url = r.get("image")
                    if not url or not url.lower().endswith((".jpg", ".jpeg", ".png")):
                        continue

                    try:
                        response = requests.get(url, timeout=10)
                        img = Image.open(BytesIO(response.content)).convert("RGB")

                        filename = f"{index:05d}.jpg"
                        path = os.path.join(save_dir, filename)
                        img.save(path)
                        index += 1
                    except Exception as e:
                        continue
            except Exception as e:
                print(f"⚠️ {keyword} skipped due to error: {e}")
            if index >= max_images:
                break

    print(f"\n✅ Scraping completed. Total images saved: {index}")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="🖼 Scrape Arabic Images using DuckDuckGo")
    parser.add_argument("--keywords", type=str, required=True, help="Path to keywords.txt")
    parser.add_argument("--max_images", type=int, default=3000)
    parser.add_argument("--images_per_keyword", type=int, default=100)
    parser.add_argument("--save_dir", type=str, default="data/raw_images")
    args = parser.parse_args()

    # Load keywords from file
    with open(args.keywords, "r", encoding="utf-8") as f:
        keywords = [line.strip() for line in f if line.strip()]

    scrape_images(keywords, args.save_dir, args.max_images, args.images_per_keyword)