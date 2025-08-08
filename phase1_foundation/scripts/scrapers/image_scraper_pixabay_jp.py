#!/usr/bin/env python3
"""
Pixabay Japanese Image Scraper
No login, no API, pure requests + BeautifulSoup
"""

import os
import time                     #  <-- added
import requests
import argparse
from bs4 import BeautifulSoup
from tqdm import tqdm
from urllib.parse import quote

HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
                  "AppleWebKit/537.36 (KHTML, like Gecko) Chrome/125.0 Safari/537.36"
}

def download_image(url: str, path: str) -> bool:
    try:
        res = requests.get(url, headers=HEADERS, timeout=15, stream=True)
        res.raise_for_status()
        with open(path, "wb") as f:
            for chunk in res.iter_content(1024):
                f.write(chunk)
        return True
    except Exception as e:
        print(f"⚠️ Failed {url[:60]}… : {e}")
        return False


def scrape_pixabay(keyword: str, save_dir: str, max_images: int) -> int:
    print(f"🖼️ Pixabay: {keyword}")
    os.makedirs(save_dir, exist_ok=True)

    url = f"https://pixabay.com/images/search/{quote(keyword)}/"
    try:
        r = requests.get(url, headers=HEADERS, timeout=15)
        r.raise_for_status()
    except Exception as e:
        print(f"❌ Could not fetch page for '{keyword}': {e}")
        return 0

    soup = BeautifulSoup(r.text, "lxml")
    img_tags = soup.select("div.container--M7Xk1 img")
    count = 0
    for idx, img in enumerate(img_tags):
        if count >= max_images:
            break
        thumb = img.get("src", "")
        if not thumb or "pixabay.com" not in thumb:
            continue
        full = thumb.replace("__340", "_1280")
        fname = f"pixabay_{keyword}_{count:03}.jpg"
        if download_image(full, os.path.join(save_dir, fname)):
            count += 1
    print(f"✅ Saved {count} images for '{keyword}'")
    return count


def main():
    parser = argparse.ArgumentParser(description="Pixabay Japanese scraper (no login)")
    parser.add_argument("--keywords", required=True, help="Path to keywords.txt")
    parser.add_argument("--images_per_keyword", type=int, default=5)
    parser.add_argument("--save_dir", required=True)
    args = parser.parse_args()

    keywords = [k.strip() for k in open(args.keywords, encoding="utf-8") if k.strip()]
    for kw in tqdm(keywords, desc="🔍 Scraping Pixabay"):
        scrape_pixabay(kw, args.save_dir, args.images_per_keyword)
        time.sleep(1)
    print("🎉 Pixabay scraping complete.")


if __name__ == "__main__":
    main()