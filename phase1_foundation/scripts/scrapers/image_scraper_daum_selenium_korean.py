import os
import argparse
import time
from urllib.parse import quote
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
from tqdm import tqdm
import requests
from PIL import Image
from io import BytesIO

HEADERS = {
    "User-Agent": "Mozilla/5.0"
}

def download_image(url, save_path):
    try:
        resp = requests.get(url, headers=HEADERS, timeout=10)
        img = Image.open(BytesIO(resp.content)).convert("RGB")
        # Skip very small images (stickers, icons)
        if img.size[0] < 300 or img.size[1] < 300:
            return False
        img.save(save_path)
        return True
    except:
        return False

def scrape_daum(keyword, save_dir, max_images, driver):
    search_url = f"https://search.daum.net/search?w=img&nil_search=btn&DA=NTB&enc=utf8&q={quote(keyword)}"
    driver.get(search_url)
    time.sleep(2)

    for _ in range(3):
        driver.execute_script("window.scrollBy(0, 1500);")
        time.sleep(1)

    images = driver.find_elements(By.TAG_NAME, "img")[:max_images + 10]
    count = 0
    keyword_clean = keyword.replace(" ", "_")

    for idx, img_tag in enumerate(images):
        src = img_tag.get_attribute("src") or img_tag.get_attribute("data-src")
        if src and src.startswith("http"):
            filename = f"daum_{keyword_clean}_{idx:03}.jpg"
            path = os.path.join(save_dir, filename)
            if download_image(src, path):
                count += 1
                if count >= max_images:
                    break
    return count

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--keywords", type=str, required=True)
    parser.add_argument("--images_per_keyword", type=int, default=5)
    parser.add_argument("--save_dir", type=str, required=True)
    args = parser.parse_args()

    os.makedirs(args.save_dir, exist_ok=True)
    with open(args.keywords, "r", encoding="utf-8") as f:
        keywords = [line.strip() for line in f if line.strip()]

    chrome_options = Options()
    chrome_options.add_argument("--headless")
    chrome_options.add_argument("--disable-gpu")
    chrome_options.add_argument("--no-sandbox")

    service = Service(ChromeDriverManager().install())
    driver = webdriver.Chrome(service=service, options=chrome_options)

    for kw in tqdm(keywords, desc="🔍 Scraping Daum"):
        print(f"🌐 Daum (Selenium): {kw}")
        saved = scrape_daum(kw, args.save_dir, args.images_per_keyword, driver)
        print(f"✅ Saved {saved} images for '{kw}'")

    driver.quit()

if __name__ == "__main__":
    main()