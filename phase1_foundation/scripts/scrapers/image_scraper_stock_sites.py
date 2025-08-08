import os
import argparse
import requests
from bs4 import BeautifulSoup
from tqdm import tqdm
from urllib.parse import quote
from PIL import Image
from io import BytesIO

HEADERS = {"User-Agent": "Mozilla/5.0"}

def download_image(url, save_path):
    try:
        resp = requests.get(url, headers=HEADERS, timeout=7)
        if resp.status_code == 200:
            img = Image.open(BytesIO(resp.content)).convert("RGB")
            if img.width < 300 or img.height < 300:
                return False  # Skip small images
            img.save(save_path)
            return True
    except Exception as e:
        print(f"⚠️ Skipping {url} due to error: {e}")
    return False
def sanitize_filename(keyword):
    return keyword.replace(" ", "_").replace("/", "_")

def scrape_pixabay(keyword, save_dir, max_images):
    print(f"📷 Pixabay: {keyword}")
    keyword_encoded = quote(keyword)
    url = f"https://pixabay.com/images/search/{keyword_encoded}/"
    resp = requests.get(url, headers=HEADERS)
    soup = BeautifulSoup(resp.text, "html.parser")
    img_tags = soup.find_all("img", limit=max_images + 15)

    count = 0
    keyword_clean = sanitize_filename(keyword)
    for i, tag in enumerate(img_tags):
        src = tag.get("src") or tag.get("data-lazy")

         # ✅ Skip invalid URLs or placeholder images
        if not src or not src.startswith("https") or src.endswith(".gif") or "/static/" in src:
            continue

        filename = f"pixabay_{keyword_clean}_{i:03}.jpg"
        path = os.path.join(save_dir, filename)
        if download_image(src, path):
            count += 1
            if count >= max_images:
                break
    return count

def scrape_getty(keyword, save_dir, max_images):
    print(f"🖼️ Getty Images: {keyword}")
    keyword_encoded = quote(keyword)
    url = f"https://www.gettyimages.com/photos/{keyword_encoded}"
    resp = requests.get(url, headers=HEADERS)
    soup = BeautifulSoup(resp.text, "html.parser")
    img_tags = soup.find_all("img", limit=max_images + 15)

    count = 0
    keyword_clean = sanitize_filename(keyword)
    for i, tag in enumerate(img_tags):
        src = tag.get("src") or tag.get("data-src")
        if src and "media.gettyimages.com" in src:
            filename = f"getty_{keyword_clean}_{i:03}.jpg"
            path = os.path.join(save_dir, filename)
            if download_image(src, path):
                count += 1
                if count >= max_images:
                    break
    return count

def scrape_shutterstock(keyword, save_dir, max_images):
    print(f"🖌️ Shutterstock: {keyword}")
    keyword_encoded = quote(keyword)
    url = f"https://www.shutterstock.com/search/{keyword_encoded}"
    resp = requests.get(url, headers=HEADERS)
    soup = BeautifulSoup(resp.text, "html.parser")
    img_tags = soup.find_all("img", limit=max_images + 20)

    count = 0
    keyword_clean = sanitize_filename(keyword)
    for i, tag in enumerate(img_tags):
        src = tag.get("src") or tag.get("data-src")
        if src and "image.shutterstock.com" in src:
            filename = f"shutterstock_{keyword_clean}_{i:03}.jpg"
            path = os.path.join(save_dir, filename)
            if download_image(src, path):
                count += 1
                if count >= max_images:
                    break
    return count

def main():
    parser = argparse.ArgumentParser(description="📸 Scrape Arabic Images from Stock Sites")
    parser.add_argument("--keywords", type=str, required=True, help="Path to keywords.txt")
    parser.add_argument("--images_per_source", type=int, default=5)
    parser.add_argument("--save_dir", type=str, default="data/raw_stock_sites_test")
    args = parser.parse_args()

    os.makedirs(args.save_dir, exist_ok=True)
    with open(args.keywords, "r", encoding="utf-8") as f:
        keywords = [line.strip() for line in f if line.strip()]

    for keyword in tqdm(keywords, desc="🔍 Scraping Keywords"):
        scrape_pixabay(keyword, args.save_dir, args.images_per_source)
        scrape_getty(keyword, args.save_dir, args.images_per_source)
        scrape_shutterstock(keyword, args.save_dir, args.images_per_source)

    print("✅ Done: Arabic image scraping completed.")

if __name__ == "__main__":
    main()