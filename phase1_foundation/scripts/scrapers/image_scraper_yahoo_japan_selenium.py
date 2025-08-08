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

def sanitize_filename(name):
    return name.replace(" ", "_").replace("/", "_")

def download_image(url, path):
    try:
        headers = {"User-Agent": "Mozilla/5.0"}
        req = urllib.request.Request(url, headers=headers)
        with urllib.request.urlopen(req, timeout=10) as resp:
            img_data = resp.read()
            img = Image.open(BytesIO(img_data))
            if img.width < 150 or img.height < 150:  # Skip low-quality
                return False
            img.save(path)
        return True
    except Exception as e:
        return False

def scrape_yahoo_images(keyword, save_dir, max_images, driver):
    base_url = "https://search.yahoo.co.jp/image/search?p="
    query = urllib.parse.quote(keyword)
    url = f"{base_url}{query}"

    driver.get(url)
    time.sleep(2)

    # Scroll to load more
    for _ in range(3):
        driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
        time.sleep(1.5)

    # Get image elements
    image_elements = driver.find_elements(By.CSS_SELECTOR, 'img[src]')
    print(f"🔍 Found {len(image_elements)} thumbnails for '{keyword}'")

    keyword_safe = sanitize_filename(keyword)
    os.makedirs(save_dir, exist_ok=True)

    count = 0
    for i, img in enumerate(image_elements):
        src = img.get_attribute("src")
        if src and src.startswith("http"):
            filename = f"yahoo_{keyword_safe}_{i:03}.jpg"
            path = os.path.join(save_dir, filename)
            if download_image(src, path):
                count += 1
                print(f"✅ Saved {filename}")
            if count >= max_images:
                break

    print(f"📥 Total saved: {count} images for '{keyword}'")

def main():
    parser = argparse.ArgumentParser(description="📷 Yahoo Japan Image Scraper (Selenium)")
    parser.add_argument("--keywords", type=str, required=True, help="Path to keywords.txt file")
    parser.add_argument("--images_per_keyword", type=int, default=5)
    parser.add_argument("--save_dir", type=str, required=True)
    args = parser.parse_args()

    with open(args.keywords, "r", encoding="utf-8") as f:
        keywords = [line.strip() for line in f if line.strip()]

    # Setup Chrome options
    chrome_options = Options()
    chrome_options.add_argument("--headless=new")
    chrome_options.add_argument("--no-sandbox")
    chrome_options.add_argument("--disable-dev-shm-usage")

    driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=chrome_options)

    for kw in tqdm(keywords, desc="🔍 Scraping Yahoo"):
        print(f"🖼️ Yahoo Japan: {kw}")
        try:
            scrape_yahoo_images(kw, args.save_dir, args.images_per_keyword, driver)
        except Exception as e:
            print(f"❌ Error scraping '{kw}': {e}")
        time.sleep(1.5)

    driver.quit()

if __name__ == "__main__":
    main()