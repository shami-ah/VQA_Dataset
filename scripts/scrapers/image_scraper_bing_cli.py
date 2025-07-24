import os
import argparse
import time
import urllib.request
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from webdriver_manager.chrome import ChromeDriverManager
from tqdm import tqdm

def sanitize_filename(text):
    return "_".join(text.strip().split())

def download_image(url, path):
    try:
        urllib.request.urlretrieve(url, path)
        return True
    except:
        return False

def scrape_bing_images_selenium(keywords, save_dir, images_per_keyword=5):
    chrome_options = Options()
    chrome_options.add_argument('--headless')
    chrome_options.add_argument('--disable-gpu')
    chrome_options.add_argument('--log-level=3')
    driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=chrome_options)

    for keyword in tqdm(keywords, desc="🔍 Bing (Optimized)"):
        print(f"\n🖼️ Bing (Optimized): {keyword}")
        search_url = f"https://www.bing.com/images/search?q={urllib.parse.quote(keyword)}&form=HDRSC2"
        driver.get(search_url)
        time.sleep(2)

        # Scroll down to load more images
        for _ in range(2):
            driver.execute_script("window.scrollBy(0, document.body.scrollHeight)")
            time.sleep(1)

        images = driver.find_elements(By.CSS_SELECTOR, "img.mimg")
        os.makedirs(save_dir, exist_ok=True)

        count = 0
        for i, img in enumerate(images):
            src = img.get_attribute("src") or img.get_attribute("data-src")
            if src and "http" in src:
                if "data:image" in src:  # Skip base64 inline images
                    continue
                filename = f"bing_{sanitize_filename(keyword)}_{i:03}.jpg"
                path = os.path.join(save_dir, filename)
                if download_image(src, path):
                    print(f"✅ Saved {filename}")
                    count += 1
                if count >= images_per_keyword:
                    break

        if count == 0:
            print(f"⚠️ No valid images for '{keyword}'")

    driver.quit()

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="🖼 Bing Image Scraper (Optimized)")
    parser.add_argument("--keywords", type=str, required=True, help="Path to keywords.txt")
    parser.add_argument("--images_per_keyword", type=int, default=5)
    parser.add_argument("--save_dir", type=str, default="data/raw_bing_selenium")
    args = parser.parse_args()

    with open(args.keywords, "r", encoding="utf-8") as f:
        keywords = [line.strip() for line in f if line.strip()]

    scrape_bing_images_selenium(keywords, args.save_dir, args.images_per_keyword)