import os
import time
import argparse
import urllib.request
from bs4 import BeautifulSoup
import requests
from tqdm import tqdm

HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)"
}

def sanitize_filename(text):
    return "_".join(text.strip().split())

def download_image(url, path):
    try:
        urllib.request.urlretrieve(url, path)
        return True
    except:
        return False

def scrape_blog_images(keywords, save_dir, images_per_keyword=5):
    blog_sources = [
        "https://forum.jogos.uol.com.br",
        "https://buzzfeed.com",
        "https://www.vivadecora.com.br",
        "https://tecnoblog.net",
        "https://www.casavogue.globo.com",
        "https://olhardigital.com.br",
        "https://www.tudocelular.com",
        "https://canaltech.com.br",
        "https://www.b9.com.br"
    ]

    for keyword in tqdm(keywords, desc="💬 Blogs & Forums"):
        print(f"\n💬 Searching for: {keyword}")
        os.makedirs(save_dir, exist_ok=True)
        count = 0

        for site in blog_sources:
            try:
                res = requests.get(site, headers=HEADERS, timeout=10)
                soup = BeautifulSoup(res.text, "html.parser")
                imgs = soup.find_all("img")
                for i, img in enumerate(imgs):
                    src = img.get("src") or img.get("data-src")
                    if src and "http" in src:
                        if "data:image" in src:
                            continue
                        filename = f"blog_{sanitize_filename(keyword)}_{count:03}.jpg"
                        path = os.path.join(save_dir, filename)
                        if download_image(src, path):
                            print(f"✅ Saved {filename} from {site}")
                            count += 1
                        if count >= images_per_keyword:
                            break
                if count >= images_per_keyword:
                    break
            except Exception as e:
                print(f"⚠️ Failed: {site}")

        if count == 0:
            print(f"⚠️ No images found for: {keyword}")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="💬 Blog Image Scraper")
    parser.add_argument("--keywords", type=str, required=True, help="Path to keywords.txt")
    parser.add_argument("--images_per_keyword", type=int, default=5)
    parser.add_argument("--save_dir", type=str, default="data/raw_portuguese_blogs")
    args = parser.parse_args()

    with open(args.keywords, "r", encoding="utf-8") as f:
        keywords = [line.strip() for line in f if line.strip()]

    scrape_blog_images(keywords, args.save_dir, args.images_per_keyword)