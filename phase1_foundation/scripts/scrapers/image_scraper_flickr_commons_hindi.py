import os
import requests
from bs4 import BeautifulSoup
from urllib.parse import quote
from tqdm import tqdm
import argparse

HEADERS = {
    "User-Agent": "Mozilla/5.0"
}

def download_image(url, save_path):
    try:
        if url.startswith('//'):
            url = 'https:' + url
        high_res_url = url.replace('_w.jpg', '_b.jpg')  # Try higher resolution
        response = requests.get(high_res_url, timeout=10)
        if response.status_code == 200:
            with open(save_path, 'wb') as f:
                f.write(response.content)
            return True
    except Exception as e:
        print(f"⚠️ Failed to download {url}: {e}")
    return False

def scrape_flickr_commons(keyword, images_per_keyword, save_dir):
    print(f"🖼️ Flickr Commons: {keyword}")
    query = quote(keyword)
    url = f"https://www.flickr.com/search/?text={query}&license=9%2C10&content_types=7"
    res = requests.get(url, headers=HEADERS)
    soup = BeautifulSoup(res.text, 'html.parser')

    image_tags = soup.find_all('img')
    os.makedirs(save_dir, exist_ok=True)

    count = 0
    for i, img in enumerate(image_tags):
        if 'src' not in img.attrs:
            continue
        img_url = img['src']
        if not img_url.endswith('.jpg'):
            continue
        filename = os.path.join(save_dir, f"flickr_{keyword}_{i:03}.jpg")
        if download_image(img_url, filename):
            count += 1
        if count >= images_per_keyword:
            break

    print(f"📥 Total saved: {count} images for '{keyword}'")

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--keywords', type=str, required=True)
    parser.add_argument('--images_per_keyword', type=int, default=5)
    parser.add_argument('--save_dir', type=str, required=True)
    args = parser.parse_args()

    with open(args.keywords, 'r', encoding='utf-8') as f:
        keywords = [line.strip() for line in f if line.strip()]

    for kw in tqdm(keywords, desc="🔍 Scraping Flickr Commons"):
        scrape_flickr_commons(kw, args.images_per_keyword, args.save_dir)

if __name__ == "__main__":
    main()