import argparse
import os
import re
import requests
from bs4 import BeautifulSoup
from tqdm import tqdm
from urllib.parse import quote

HEADERS = {
    "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.114 Safari/537.36"
}

def sanitize_filename(name):
    name = re.sub(r"[^\w\s-]", '', name, flags=re.UNICODE)
    name = re.sub(r"\s+", '_', name)
    return name.strip()

def download_image(url, path):
    try:
        resp = requests.get(url, timeout=10)
        if resp.status_code == 200:
            with open(path, "wb") as f:
                f.write(resp.content)
            return True
    except Exception:
        pass
    return False

def scrape_news(keyword, save_dir, max_images):
    print(f"📰 News: {keyword}")
    encoded_kw = quote(keyword)
    url = f"https://search.naver.com/search.naver?where=news&query={encoded_kw}"
    try:
        resp = requests.get(url, headers=HEADERS, timeout=10)
        soup = BeautifulSoup(resp.text, "html.parser")
        imgs = soup.find_all("img")
        count = 0
        for i, img in enumerate(imgs):
            src = img.get("src")
            if not src or "logo" in src or "icon" in src:
                continue
            fname = f"news_{sanitize_filename(keyword)}_{i:03}.jpg"
            path = os.path.join(save_dir, fname)
            if download_image(src, path):
                count += 1
                if count >= max_images:
                    break
        print(f"📥 Total saved: {count} images for '{keyword}'")
    except Exception as e:
        print(f"❌ Error scraping news for '{keyword}': {e}")

def scrape_blog(keyword, save_dir, max_images):
    print(f"📝 Blog: {keyword}")
    encoded_kw = quote(keyword)
    url = f"https://search.naver.com/search.naver?where=post&query={encoded_kw}"
    try:
        resp = requests.get(url, headers=HEADERS, timeout=10)
        soup = BeautifulSoup(resp.text, "html.parser")
        imgs = soup.find_all("img")
        count = 0
        for i, img in enumerate(imgs):
            src = img.get("src")
            if not src or "logo" in src or "icon" in src:
                continue
            fname = f"blog_{sanitize_filename(keyword)}_{i:03}.jpg"
            path = os.path.join(save_dir, fname)
            if download_image(src, path):
                count += 1
                if count >= max_images:
                    break
        print(f"📥 Total saved: {count} images for '{keyword}'")
    except Exception as e:
        print(f"❌ Error scraping blog for '{keyword}': {e}")

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--keywords", type=str, required=True)
    parser.add_argument("--images_per_keyword", type=int, default=5)
    parser.add_argument("--save_dir", type=str, required=True)
    args = parser.parse_args()

    os.makedirs(args.save_dir, exist_ok=True)

    with open(args.keywords, "r", encoding="utf-8") as f:
        keywords = [line.strip() for line in f if line.strip()]

    for kw in tqdm(keywords, desc="🔍 Scraping Blog & News"):
        scrape_news(kw, args.save_dir, args.images_per_keyword)
        scrape_blog(kw, args.save_dir, args.images_per_keyword)

if __name__ == "__main__":
    main()