#!/usr/bin/env python3
import os
import time
import argparse
import urllib.request
import urllib.parse
from io import BytesIO
import requests
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from webdriver_manager.chrome import ChromeDriverManager
from PIL import Image
from tqdm import tqdm
import re


def sanitize_filename(name):
    return name.replace(" ", "_").replace("/", "_")


def download_image(url, path, min_size=(800, 600)):
    try:
        headers = {"User-Agent": "Mozilla/5.0"}
        req = urllib.request.Request(url, headers=headers)
        with urllib.request.urlopen(req, timeout=10) as resp:
            data = resp.read()
        img = Image.open(BytesIO(data))
        if img.width < min_size[0] or img.height < min_size[1]:
            return False
        os.makedirs(os.path.dirname(path), exist_ok=True)
        img.save(path)
        return True
    except Exception as e:
        print(f"⚠️ Download failed for {url}: {e}")
        return False


def scrape_wikimedia(keyword, save_dir, max_images):
    print("🗂 Wikimedia Commons...")
    url = f"https://commons.wikimedia.org/w/index.php?search={urllib.parse.quote(keyword)}&type=image"
    resp = requests.get(url, timeout=10)
    soup = BeautifulSoup(resp.text, 'html.parser')
    links = soup.select('div.search-results a.image')
    count = 0
    safe = sanitize_filename(keyword)
    for a in links:
        if count >= max_images:
            break
        href = a.get('href')
        if not href:
            continue
        page_url = urllib.parse.urljoin('https://commons.wikimedia.org', href)
        r2 = requests.get(page_url, timeout=10)
        soup2 = BeautifulSoup(r2.text, 'html.parser')
        full = soup2.select_one('div.fullMedia a')
        if not full:
            continue
        img_url = full['href']
        if img_url.startswith('//'):
            img_url = 'https:' + img_url
        fname = f"wikimedia_{safe}_{count:03d}.jpg"
        if download_image(img_url, os.path.join(save_dir, fname)):
            count += 1
    print(f"✅ Wikimedia: saved {count}/{max_images} for '{keyword}'")


def scrape_archive(keyword, save_dir, max_images):
    print("📚 Archive.org...")
    qs = urllib.parse.quote(keyword + ' language:"Spanish"')
    search_url = f"https://archive.org/advancedsearch.php?q={qs}&rows={max_images}&output=json"
    data = requests.get(search_url, timeout=10).json()
    docs = data.get('response', {}).get('docs', [])
    count = 0
    safe = sanitize_filename(keyword)
    for doc in docs:
        if count >= max_images:
            break
        ident = doc.get('identifier')
        if not ident:
            continue
        meta = requests.get(f"https://archive.org/metadata/{ident}", timeout=10).json()
        for f in meta.get('files', []):
            fmt = f.get('format', '').upper()
            if fmt in ['JPEG', 'JPG', 'PNG']:
                file_name = f.get('name')
                file_url = f"https://archive.org/download/{ident}/{file_name}"
                fname = f"archive_{safe}_{count:03d}.jpg"
                if download_image(file_url, os.path.join(save_dir, fname)):
                    count += 1
                break
    print(f"✅ Archive.org: saved {count}/{max_images} for '{keyword}'")


def scrape_flickr(keyword, save_dir, max_images, driver):
    print("📷 Flickr...")
    url = f"https://www.flickr.com/search/?text={urllib.parse.quote(keyword)}&lang=es"
    driver.get(url)
    WebDriverWait(driver, 10).until(
        EC.presence_of_all_elements_located((By.CSS_SELECTOR, 'div.view.photo-list-photo-view'))
    )
    thumbs = driver.find_elements(By.CSS_SELECTOR, 'div.view.photo-list-photo-view')
    count = 0
    safe = sanitize_filename(keyword)
    for thumb in thumbs:
        if count >= max_images:
            break
        style = thumb.get_attribute('style')
        m = re.search(r'url\((.*?)\)', style)
        if not m:
            continue
        thumb_url = m.group(1).strip('"')
        hi_url = thumb_url.replace('_m.', '_b.')
        fname = f"flickr_{safe}_{count:03d}.jpg"
        if download_image(hi_url, os.path.join(save_dir, fname)):
            count += 1
    print(f"✅ Flickr: saved {count}/{max_images} for '{keyword}'")


def scrape_stocksnap(keyword, save_dir, max_images):
    print("🏞️ StockSnap...")
    url = f"https://stocksnap.io/search/{urllib.parse.quote(keyword)}"
    r = requests.get(url, timeout=10)
    soup = BeautifulSoup(r.text, 'html.parser')
    imgs = soup.select('div.image-item img')
    count = 0
    safe = sanitize_filename(keyword)
    for img in imgs:
        if count >= max_images:
            break
        src = img.get('data-src') or img.get('src')
        fname = f"stocksnap_{safe}_{count:03d}.jpg"
        if download_image(src, os.path.join(save_dir, fname)):
            count += 1
    print(f"✅ StockSnap: saved {count}/{max_images} for '{keyword}'")


def scrape_pexels(keyword, save_dir, max_images):
    print("📸 Pexels...")
    url = f"https://www.pexels.com/search/{urllib.parse.quote(keyword)}/?locale=es"
    r = requests.get(url, timeout=10)
    soup = BeautifulSoup(r.text, 'html.parser')
    imgs = soup.select('article.photo-item img')
    count = 0
    safe = sanitize_filename(keyword)
    for img in imgs:
        if count >= max_images:
            break
        srcset = img.get('srcset', '')
        if srcset:
            candidates = [s.strip() for s in srcset.split(',')]
            hi_url = candidates[-1].split(' ')[0]
        else:
            hi_url = img.get('src')
        fname = f"pexels_{safe}_{count:03d}.jpg"
        if download_image(hi_url, os.path.join(save_dir, fname)):
            count += 1
    print(f"✅ Pexels: saved {count}/{max_images} for '{keyword}'")


def main():
    parser = argparse.ArgumentParser(description="📷 Spanish Super-Scraper (High-Res + Multisource)")
    parser.add_argument("--keywords", required=True, help="Path to Spanish keywords file")
    parser.add_argument("--images_per_keyword", type=int, default=5)
    parser.add_argument("--save_dir", required=True, help="Directory to store images")
    args = parser.parse_args()

    with open(args.keywords, 'r', encoding='utf-8') as f:
        keywords = [l.strip() for l in f if l.strip()]
    os.makedirs(args.save_dir, exist_ok=True)

    opts = Options()
    opts.add_argument("--headless=new")
    opts.add_argument("--no-sandbox")
    opts.add_argument("--disable-dev-shm-usage")
    driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=opts)

    for kw in tqdm(keywords, desc="🔍 Scraping Spanish Sources"):
        print(f"\n🔑 Keyword: {kw}")
        try:
            scrape_wikimedia(kw, args.save_dir, args.images_per_keyword)
        except Exception as e:
            print(f"⚠️ Wikimedia error for '{kw}': {e}")
        try:
            scrape_archive(kw, args.save_dir, args.images_per_keyword)
        except Exception as e:
            print(f"⚠️ Archive.org error for '{kw}': {e}")
        try:
            scrape_flickr(kw, args.save_dir, args.images_per_keyword, driver)
        except Exception as e:
            print(f"⚠️ Flickr error for '{kw}': {e}")
        try:
            scrape_stocksnap(kw, args.save_dir, args.images_per_keyword)
        except Exception as e:
            print(f"⚠️ StockSnap error for '{kw}': {e}")
        try:
            scrape_pexels(kw, args.save_dir, args.images_per_keyword)
        except Exception as e:
            print(f"⚠️ Pexels error for '{kw}': {e}")
        time.sleep(1)

    driver.quit()
    print("\n✅ All sources scraping complete.")

if __name__ == '__main__':
    main()