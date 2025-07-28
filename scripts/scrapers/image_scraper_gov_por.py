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
from bs4 import BeautifulSoup


def sanitize_filename(text):
    return "_".join(text.strip().split())


def download_image(url, path):
    try:
        urllib.request.urlretrieve(url, path)
        return True
    except:
        return False


def scrape_gov_edu_sources(keywords, save_dir, images_per_keyword=5):
    chrome_options = Options()
    chrome_options.add_argument('--headless')
    chrome_options.add_argument('--disable-gpu')
    chrome_options.add_argument('--log-level=3')
    driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=chrome_options)

    sources = {
        "gov.br": "https://www.gov.br/pt-br/busca?SearchableText={}",
        "ifsp.edu.br": "https://www.ifsp.edu.br/component/search/?searchword={}&searchphrase=all"
    }

    for keyword in tqdm(keywords, desc="🔍 Gov/Edu Sources"):
        for source_name, url_template in sources.items():
            print(f"\n🖼️ Source: {source_name} | Keyword: {keyword}")
            search_url = url_template.format(urllib.parse.quote(keyword))
            driver.get(search_url)
            time.sleep(3)
            soup = BeautifulSoup(driver.page_source, 'html.parser')

            # Find all image elements
            images = soup.find_all("img")
            os.makedirs(save_dir, exist_ok=True)
            count = 0

            for i, img in enumerate(images):
                src = img.get("src") or img.get("data-src")
                if src and "http" not in src:
                    src = f"https://{source_name}/{src.lstrip('/')}"
                if src and "http" in src:
                    filename = f"{source_name.split('.')[0]}_{sanitize_filename(keyword)}_{i:03}.jpg"
                    path = os.path.join(save_dir, filename)
                    if download_image(src, path):
                        print(f"✅ Saved {filename}")
                        count += 1
                if count >= images_per_keyword:
                    break

            if count == 0:
                print(f"⚠️ No valid images for '{keyword}' in {source_name}")

    driver.quit()


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="🖼 Gov/Edu Image Scraper")
    parser.add_argument("--keywords", type=str, required=True, help="Path to keywords.txt")
    parser.add_argument("--images_per_keyword", type=int, default=5)
    parser.add_argument("--save_dir", type=str, default="data/raw_gov_edu")
    args = parser.parse_args()

    with open(args.keywords, "r", encoding="utf-8") as f:
        keywords = [line.strip() for line in f if line.strip()]

    scrape_gov_edu_sources(keywords, args.save_dir, args.images_per_keyword)