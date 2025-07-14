import argparse
import os
import time
import requests
from tqdm import tqdm
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager

def sanitize_filename(text):
    return "".join(c if c.isalnum() else "_" for c in text)

def scrape_naver_images(keyword, save_dir, max_images, driver):
    query = keyword.replace(" ", "+")
    url = f"https://search.naver.com/search.naver?where=image&sm=tab_jum&query={query}"
    driver.get(url)
    time.sleep(2)

    os.makedirs(save_dir, exist_ok=True)
    count = 0
    seen = set()
    keyword_clean = sanitize_filename(keyword)

    # Scroll down
    for _ in range(3):
        driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
        time.sleep(2)

    imgs = driver.find_elements(By.CSS_SELECTOR, "img._fe_image_tab_content")
    if not imgs:
        imgs = driver.find_elements(By.CSS_SELECTOR, "img")

    print(f"🔍 Found {len(imgs)} images for '{keyword}'")

    for i, tag in enumerate(imgs):
        if count >= max_images:
            break
        src = tag.get_attribute("src")
        if not src or "data:" in src or src in seen:
            continue
        try:
            img_data = requests.get(src, timeout=10).content
            fname = f"naver_{keyword_clean}_{count:03}.jpg"
            with open(os.path.join(save_dir, fname), "wb") as f:
                f.write(img_data)
            count += 1
            seen.add(src)
            print(f"✅ Saved {fname}")
        except:
            continue

    print(f"📥 Total saved: {count} images for '{keyword}'")

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--keywords", type=str, required=True)
    parser.add_argument("--images_per_keyword", type=int, default=5)
    parser.add_argument("--save_dir", type=str, required=True)
    args = parser.parse_args()

    chrome_options = Options()
    chrome_options.add_argument("--headless")
    chrome_options.add_argument("--no-sandbox")
    chrome_options.add_argument("--disable-dev-shm-usage")
    driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=chrome_options)

    with open(args.keywords, "r", encoding="utf-8") as f:
        keywords = [line.strip() for line in f if line.strip()]

    for kw in tqdm(keywords, desc="🔍 Scraping Naver"):
        print(f"🖼️ Naver (Fixed): {kw}")
        scrape_naver_images(kw, args.save_dir, args.images_per_keyword, driver)

    driver.quit()

if __name__ == "__main__":
    main()