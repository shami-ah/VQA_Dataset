import os
import requests
from bs4 import BeautifulSoup
from urllib.parse import quote
from tqdm import tqdm
import argparse

HEADERS = {
    "User-Agent": "Mozilla/5.0"
}

def sanitize_filename(text):
    return ''.join(c if c.isalnum() else '_' for c in text)

def download_image(img_url, save_path):
    try:
        response = requests.get(img_url, timeout=10)
        if response.status_code == 200:
            with open(save_path, 'wb') as f:
                f.write(response.content)
            return True
    except Exception:
        pass
    return False

def scrape_yahoo_images(keyword, save_dir, max_images):
    print(f"🖼️ Yahoo Image Search: {keyword}")
    query = quote(keyword)
    url = f"https://images.search.yahoo.com/search/images?p={query}"

    try:
        response = requests.get(url, headers=HEADERS, timeout=10)
        soup = BeautifulSoup(response.text, 'html.parser')
        img_tags = soup.find_all('img')

        os.makedirs(save_dir, exist_ok=True)
        count = 0
        for idx, img in enumerate(img_tags):
            src = img.get('data-src') or img.get('src')
            if not src or not src.startswith('http'):
                continue

            filename = os.path.join(save_dir, f"yahoo_{sanitize_filename(keyword)}_{idx:03}.jpg")
            if download_image(src, filename):
                count += 1
                print(f"✅ Saved {os.path.basename(filename)}")
            if count >= max_images:
                break

        print(f"📥 Total saved: {count} images for '{keyword}'")
    except Exception as e:
        print(f"❌ Error for '{keyword}': {e}")

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--keywords', type=str, required=True, help='Path to keyword txt file')
    parser.add_argument('--images_per_keyword', type=int, default=5)
    parser.add_argument('--save_dir', type=str, required=True)
    args = parser.parse_args()

    with open(args.keywords, 'r', encoding='utf-8') as f:
        keywords = [line.strip() for line in f if line.strip()]

    os.makedirs(args.save_dir, exist_ok=True)

    for keyword in tqdm(keywords, desc="🔍 Scraping Yahoo"):
        scrape_yahoo_images(keyword, args.save_dir, args.images_per_keyword)

if __name__ == "__main__":
    main()