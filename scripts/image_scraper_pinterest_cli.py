# scripts/image_scraper_pinterest_cli.py

import os
import argparse
import requests
from bs4 import BeautifulSoup
from fake_useragent import UserAgent
from urllib.parse import quote
from tqdm import tqdm
from PIL import Image
from io import BytesIO

def fetch_pinterest_images(keyword, max_images, save_dir):
    headers = {'User-Agent': UserAgent().random}
    query = quote(keyword)
    url = f"https://www.pinterest.com/search/pins/?q={query}"

    try:
        response = requests.get(url, headers=headers, timeout=10)
        soup = BeautifulSoup(response.text, "html.parser")
        images = soup.find_all("img")
    except Exception as e:
        print(f"⚠️ Error fetching {keyword}: {e}")
        return 0

    count = 0
    for img in images:
        src = img.get("src")
        if not src or not src.startswith("http"):
            continue

        try:
            img_resp = requests.get(src, headers=headers, timeout=10)
            pil_img = Image.open(BytesIO(img_resp.content)).convert("RGB")
            filename = os.path.join(save_dir, f"{keyword}_{count:03}.jpg")
            pil_img.save(filename)
            count += 1

            if count >= max_images:
                break
        except:
            continue

    return count

def main():
    parser = argparse.ArgumentParser(description="📌 Pinterest Image Scraper")
    parser.add_argument("--keywords", type=str, required=True, help="Path to keyword .txt file")
    parser.add_argument("--images_per_keyword", type=int, default=5)
    parser.add_argument("--save_dir", type=str, default="data/raw_pinterest_test")
    args = parser.parse_args()

    os.makedirs(args.save_dir, exist_ok=True)

    with open(args.keywords, "r", encoding="utf-8") as f:
        keywords = [line.strip() for line in f if line.strip()]

    for keyword in tqdm(keywords, desc="🔍 Scraping Pinterest"):
        saved = fetch_pinterest_images(keyword, args.images_per_keyword, args.save_dir)
        print(f"✅ {keyword}: {saved} images saved.")

    print("\n🎉 Done scraping Pinterest images.")

if __name__ == "__main__":
    main()