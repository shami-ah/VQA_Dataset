#!/usr/bin/env python3
"""
Pexels Japanese scraper with 403 retry + random UA
"""

import os, time, random
import argparse, requests
from bs4 import BeautifulSoup
from tqdm import tqdm
from urllib.parse import quote

UA_LIST = [
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/125.0 Safari/537.36",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.0 Safari/605.1.15",
    "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0 Safari/537.36"
]

def headers():
    return {"User-Agent": random.choice(UA_LIST)}

def download_image(url: str, path: str) -> bool:
    try:
        res = requests.get(url, headers=headers(), timeout=15, stream=True)
        res.raise_for_status()
        with open(path, "wb") as f:
            for chunk in res.iter_content(1024):
                f.write(chunk)
        return True
    except Exception as e:
        print(f"⚠️ Failed {url[:60]}… : {e}")
        return False

def fetch(url: str):
    for attempt in range(2):
        r = requests.get(url, headers=headers(), timeout=15)
        if r.status_code != 403:
            return r
        time.sleep(5 * (attempt + 1))
    r.raise_for_status()

def scrape_pexels(keyword: str, save_dir: str, max_images: int) -> int:
    print(f"🖼️ Pexels: {keyword}")
    os.makedirs(save_dir, exist_ok=True)
    url = f"https://www.pexels.com/search/{quote(keyword)}/"
    try:
        r = fetch(url)
    except Exception as e:
        print(f"❌ Could not fetch page for '{keyword}': {e}")
        return 0

    soup = BeautifulSoup(r.text, "lxml")
    imgs = soup.select("article img")
    count = 0
    for idx, img in enumerate(imgs):
        if count >= max_images:
            break
        srcset = img.get("srcset", "")
        if not srcset:
            continue
        largest = srcset.split()[-2]
        fname = f"pexels_{keyword}_{count:03}.jpg"
        if download_image(largest, os.path.join(save_dir, fname)):
            count += 1
    print(f"✅ Saved {count} images for '{keyword}'")
    return count

def main():
    parser = argparse.ArgumentParser(description="Pexels Japanese scraper")
    parser.add_argument("--keywords", required=True)
    parser.add_argument("--images_per_keyword", type=int, default=5)
    parser.add_argument("--save_dir", required=True)
    args = parser.parse_args()
    keywords = [k.strip() for k in open(args.keywords, encoding="utf-8") if k.strip()]
    for kw in tqdm(keywords, desc="🔍 Scraping Pexels"):
        scrape_pexels(kw, args.save_dir, args.images_per_keyword)
        time.sleep(random.uniform(1.5, 3))
    print("🎉 Pexels scraping complete.")

if __name__ == "__main__":
    main()