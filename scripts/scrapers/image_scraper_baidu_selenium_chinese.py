import os
import time
import argparse
from urllib.parse import quote
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.desired_capabilities import DesiredCapabilities
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
from tqdm import tqdm
import requests
from PIL import Image
from io import BytesIO

HEADERS = {"User-Agent": "Mozilla/5.0"}

def download_image(url, save_path):
    try:
        resp = requests.get(url, headers=HEADERS, timeout=10)
        if resp.status_code == 200:
            img = Image.open(BytesIO(resp.content)).convert("RGB")
            img.save(save_path)
            return True
    except:
        return False
    return False

def scrape_baidu_selenium(keyword, save_dir, max_images, driver):
    print(f"🔍 Baidu (Selenium): {keyword}")
    os.makedirs(save_dir, exist_ok=True)
    keyword_encoded = quote(keyword)
    url = f"https://image.baidu.com/search/index?tn=baiduimage&word={keyword_encoded}"

    # Retry page loading
    for attempt in range(3):
        try:
            driver.set_page_load_timeout(30)
            driver.get(url)
            time.sleep(3)
            break
        except Exception as e:
            print(f"⚠️ Attempt {attempt+1} failed to load {url}: {e}")
            time.sleep(5)
    else:
        print(f"❌ Skipping {keyword} after 3 failed attempts.")
        return 0

    # Scroll to load more images
    for _ in range(2):
        driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
        time.sleep(2)

    images = driver.find_elements(By.TAG_NAME, "img")
    count = 0
    keyword_clean = "".join(c if c.isalnum() else "_" for c in keyword)

    for i, img in enumerate(images):
        src = img.get_attribute("src") or img.get_attribute("data-src")
        if src and src.startswith("http"):
            filename = f"baidu_{keyword_clean}_{i:03}.jpg"
            path = os.path.join(save_dir, filename)
            if download_image(src, path):
                count += 1
                if count >= max_images:
                    break

    print(f"✅ Saved {count} images for '{keyword}'")
    return count

def main():
    parser = argparse.ArgumentParser(description="🔍 Chinese Baidu Image Scraper (Selenium)")
    parser.add_argument("--keywords", type=str, required=True, help="Path to keywords.txt")
    parser.add_argument("--images_per_keyword", type=int, default=5)
    parser.add_argument("--save_dir", type=str, required=True)
    args = parser.parse_args()

    os.makedirs(args.save_dir, exist_ok=True)
    with open(args.keywords, "r", encoding="utf-8") as f:
        keywords = [line.strip() for line in f if line.strip()]

    chrome_options = Options()
    chrome_options.add_argument("--headless")
    chrome_options.add_argument("--no-sandbox")
    chrome_options.add_argument("--disable-dev-shm-usage")
    chrome_options.set_capability("pageLoadStrategy", "eager")

    driver = webdriver.Chrome(
        service=Service(ChromeDriverManager().install()),
        options=chrome_options
    )

    for kw in tqdm(keywords, desc="🔍 Scraping Baidu"):
        print(f"🔍 Baidu (Selenium): {kw}")
        try:
            scrape_baidu_selenium(kw, args.save_dir, args.images_per_keyword, driver)
        except Exception as e:
            print(f"⚠️ Error scraping '{kw}': {e}")

    driver.quit()
    print("✅ Baidu scraping complete.")

if __name__ == "__main__":
    main()