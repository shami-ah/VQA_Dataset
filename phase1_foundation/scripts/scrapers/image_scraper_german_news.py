import os
import time
import argparse
import urllib.request
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from webdriver_manager.chrome import ChromeDriverManager
from tqdm import tqdm
from PIL import Image
from io import BytesIO
import urllib.parse
import random

NEWS_SOURCES = [
    "https://www.spiegel.de/suche/?suchbegriff=",
    "https://www.zeit.de/suche/index?q=",
    "https://www.sueddeutsche.de/suche?q=",
    "https://www.bild.de/suche.bild.html?query=",
    "https://www.dw.com/de/suche/?q="
]

def sanitize_filename(name):
    return name.replace(" ", "_").replace("/", "_").replace("?", "").replace("&", "")

def download_image(url, path):
    try:
        headers = {"User-Agent": "Mozilla/5.0"}
        req = urllib.request.Request(url, headers=headers)
        with urllib.request.urlopen(req, timeout=10) as resp:
            img_data = resp.read()
            img = Image.open(BytesIO(img_data))
            if img.width < 150 or img.height < 150:
                return False
            img.save(path)
        return True
    except:
        return False

def scrape_news_images(keyword, save_dir, max_images, driver):
    os.makedirs(save_dir, exist_ok=True)
    count = 0
    keyword_safe = sanitize_filename(keyword)

    for source in NEWS_SOURCES:
        query_url = source + urllib.parse.quote(keyword)
        driver.get(query_url)
        time.sleep(2 + random.uniform(0.5, 1.5))
        
        # Try generic image selectors
        images = driver.find_elements(By.CSS_SELECTOR, 'img[src]')
        for i, img in enumerate(images):
            src = img.get_attribute("src")
            if src and src.startswith("http") and "logo" not in src.lower() and "icon" not in src.lower():
                filename = f"{keyword_safe}_{i:03}.jpg"
                path = os.path.join(save_dir, filename)
                if download_image(src, path):
                    count += 1
                if count >= max_images:
                    return
        time.sleep(1.2)

def main():
    parser = argparse.ArgumentParser(description="📰 German News & Magazine Image Scraper")
    parser.add_argument("--keywords", type=str, required=True, help="Path to keywords.txt")
    parser.add_argument("--images_per_keyword", type=int, default=5)
    parser.add_argument("--save_dir", type=str, required=True)
    args = parser.parse_args()

    with open(args.keywords, "r", encoding="utf-8") as f:
        keywords = [line.strip() for line in f if line.strip()]

    chrome_options = Options()
    chrome_options.add_argument("--headless=new")
    chrome_options.add_argument("--no-sandbox")
    chrome_options.add_argument("--disable-dev-shm-usage")
    chrome_options.add_argument("--window-size=1920x1080")

    driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=chrome_options)

    for kw in tqdm(keywords, desc="📥 Scraping German News"):
        print(f"🔍 Keyword: {kw}")
        try:
            scrape_news_images(kw, args.save_dir, args.images_per_keyword, driver)
        except Exception as e:
            print(f"❌ Error scraping '{kw}': {e}")
        time.sleep(1.5)

    driver.quit()

if __name__ == "__main__":
    main()