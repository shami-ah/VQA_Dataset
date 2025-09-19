#!/usr/bin/env python3
"""
Getty Images Hindi Image Scraper
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
    
    # Try webdriver-manager first
    try:
        from webdriver_manager.chrome import ChromeDriverManager
        from selenium.webdriver.chrome.service import Service
        service = Service(ChromeDriverManager().install())
        return webdriver.Chrome(service=service, options=chrome_options)
    except Exception:
        # Fallback to system ChromeDriver
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

def scrape_getty(keyword: str, save_dir: str, max_images: int) -> int:
    print(f"🖼️ Getty Images: {keyword}")
    os.makedirs(save_dir, exist_ok=True)

    driver = setup_driver()
    url = f"https://www.gettyimages.com/photos/{quote(keyword)}"
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
        fname = f"getty_{keyword}_{count:03}.jpg"
        if download_image(src, os.path.join(save_dir, fname)):
            count += 1
    driver.quit()
    print(f"✅ Saved {count} images for '{keyword}'")
    return count

def main():
    parser = argparse.ArgumentParser(description="Getty Images Hindi scraper")
    parser.add_argument("--keywords", required=True)
    parser.add_argument("--images_per_keyword", type=int, default=10)
    parser.add_argument("--save_dir", required=True)
    args = parser.parse_args()

    keywords = [k.strip() for k in open(args.keywords, encoding="utf-8") if k.strip()]
    for kw in tqdm(keywords, desc="🔍 Scraping Getty Images"):
        scrape_getty(kw, args.save_dir, args.images_per_keyword)

    print("🎉 Getty Images scraping complete.")

if __name__ == "__main__":
    main()