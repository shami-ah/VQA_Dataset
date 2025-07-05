import os
import json
import argparse
import requests
from PIL import Image
from io import BytesIO
from tqdm import tqdm

API_KEY = "AIzaSyAEoW57qHWSqGaeHuUXvshsMCrhComaccI"
CSE_ID = "01689bfc9acce4570"

def google_search(query, num, api_key, cse_id):
    url = "https://www.googleapis.com/customsearch/v1"
    params = {
        "q": query,
        "cx": cse_id,
        "key": api_key,
        "searchType": "image",
        "num": num
    }
    response = requests.get(url, params=params)
    return response.json()

def scrape_images(keywords, save_dir, images_per_keyword):
    os.makedirs(save_dir, exist_ok=True)
    index = 0
    for keyword in tqdm(keywords, desc="🔎 Scraping Google"):
        try:
            results = google_search(keyword, images_per_keyword, API_KEY, CSE_ID)

            # 🧪 Debug: See what Google returns
            print(f"\n🔍 Raw API response for '{keyword}':")
            print(json.dumps(results, indent=2, ensure_ascii=False))
            for item in results.get("items", []):
                img_url = item.get("link")
                if not img_url: continue
                try:
                    response = requests.get(img_url, timeout=10)
                    img = Image.open(BytesIO(response.content)).convert("RGB")
                    filename = f"{keyword}_{index:03d}.jpg"
                    img.save(os.path.join(save_dir, filename))
                    index += 1
                except Exception as e:
                    continue
        except Exception as e:
            print(f"❌ Error with '{keyword}': {e}")

    print(f"\n✅ Scraping completed. Total images saved: {index}")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="🔎 Google Image Scraper")
    parser.add_argument("--keywords", type=str, required=True, help="Path to keywords.txt")
    parser.add_argument("--images_per_keyword", type=int, default=5)
    parser.add_argument("--save_dir", type=str, default="data/raw_google_test")
    args = parser.parse_args()

    with open(args.keywords, "r", encoding="utf-8") as f:
        keywords = [line.strip() for line in f if line.strip()]

    scrape_images(keywords, args.save_dir, args.images_per_keyword)