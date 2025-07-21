#!/usr/bin/env python3
"""
Pinterest Hindi Image Scraper
No login, no API, pure Selenium + BeautifulSoup
"""

import os
import argparse
import time
import requests
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from bs4 import BeautifulSoup
from tqdm import tqdm
from urllib.parse import quote

def setup_driver():
    chrome_options = Options()
    chrome_options.add_argument("--headless")
    chrome_options.add_argument("--no-sandbox")
    chrome_options.add_argument("--disable-dev-shm-usage")
    return webdriver.Chrome(options=chrome_options)

def download_image(url: str, path: str) -> bool:
    try:
        response = requests.get(url, timeout=15)
        if response.status_code == 200:
            with open(path, 'wb') as f:
                f.write(response.content)
            return True
    except Exception as e:
        print(f"⚠️ Failed to download {url}: {e}")
    return False

def scrape_pinterest(keyword: str, save_dir: str, max_images: int) -> int:
    print(f"🖼️ Pinterest: {keyword}")
    os.makedirs(save_dir, exist_ok=True)

    driver = setup_driver()
    url = f"https://www.pinterest.com/search/pins/?q={quote(keyword)}"
    driver.get(url)
    time.sleep(2)

    soup = BeautifulSoup(driver.page_source, "lxml")
    imgs = soup.select("img[src]")
    count = 0
    for idx, img in enumerate(imgs):
        if count >= max_images:
            break
        src = img.get("src")
        if not src or not src.startswith("http"):
            continue
        fname = f"pinterest_{keyword}_{count:03}.jpg"
        if download_image(src, os.path.join(save_dir, fname)):
            count += 1
    driver.quit()
    print(f"✅ Saved {count} images for '{keyword}'")
    return count

def main():
    parser = argparse.ArgumentParser(description="Pinterest Hindi scraper")
    parser.add_argument("--keywords", required=True)
    parser.add_argument("--images_per_keyword", type=int, default=10)
    parser.add_argument("--save_dir", required=True)
    args = parser.parse_args()

    keywords = [k.strip() for k in open(args.keywords, encoding="utf-8") if k.strip()]
    for kw in tqdm(keywords, desc="🔍 Scraping Pinterest"):
        scrape_pinterest(kw, args.save_dir, args.images_per_keyword)

    print("🎉 Pinterest scraping complete.")

if __name__ == "__main__":
    main()