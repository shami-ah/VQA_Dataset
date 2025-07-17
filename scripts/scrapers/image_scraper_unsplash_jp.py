#!/usr/bin/env python3
"""
Unsplash Japanese Image Scraper – updated selectors
"""

import os
import time
import argparse
import requests
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from tqdm import tqdm

HEADERS = {"User-Agent": "Mozilla/5.0"}

def download_image(url: str, path: str) -> bool:
    try:
        res = requests.get(url, headers=HEADERS, stream=True, timeout=15)
        res.raise_for_status()
        with open(path, "wb") as f:
            for chunk in res.iter_content(1024):
                f.write(chunk)
        return True
    except Exception as e:
        print(f"⚠️ Download fail {url[:60]}… : {e}")
        return False


def scrape_unsplash(keyword: str, save_dir: str, max_images: int) -> int:
    print(f"🖼️ Unsplash: {keyword}")
    os.makedirs(save_dir, exist_ok=True)

    chrome_options = Options()
    chrome_options.add_argument("--headless=new")
    chrome_options.add_argument("--window-size=1366,768")
    driver = webdriver.Chrome(options=chrome_options)

    query = keyword.replace(" ", "+")
    driver.get(f"https://unsplash.com/s/photos/{query}")

    # scroll & wait for lazy images
    for _ in range(5):
        driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
        time.sleep(2.5)

    soup = BeautifulSoup(driver.page_source, "lxml")
    # New selector: each photo inside <a> with <img>
    imgs = soup.select('a[href*="/photos/"] img[srcset]')
    count = 0
    for idx, img in enumerate(imgs):
        if count >= max_images:
            break
        srcset = img.get("srcset", "")
        if not srcset:
            continue
        # pick largest (last) URL in srcset
        largest = srcset.split()[-2]  # e.g. "https://...1280.jpg"
        fname = f"unsplash_{keyword}_{count:03}.jpg"
        if download_image(largest, os.path.join(save_dir, fname)):
            count += 1
    driver.quit()
    print(f"✅ Saved {count} images for '{keyword}'")
    return count


def main():
    parser = argparse.ArgumentParser(description="Unsplash Japanese scraper (fixed)")
    parser.add_argument("--keywords", required=True)
    parser.add_argument("--images_per_keyword", type=int, default=5)
    parser.add_argument("--save_dir", required=True)
    args = parser.parse_args()

    keywords = [k.strip() for k in open(args.keywords, encoding="utf-8") if k.strip()]
    for kw in tqdm(keywords, desc="🔍 Scraping Unsplash"):
        scrape_unsplash(kw, args.save_dir, args.images_per_keyword)

    print("🎉 Unsplash scraping complete.")


if __name__ == "__main__":
    main()