import os
import argparse
from bing_image_downloader import downloader

def scrape_bing_images(keywords, save_dir, max_images_per_keyword):
    os.makedirs(save_dir, exist_ok=True)

    for keyword in keywords:
        print(f"🔍 Scraping Bing for: {keyword}")
        downloader.download(
            keyword,
            limit=max_images_per_keyword,
            output_dir=save_dir,
            adult_filter_off=True,
            force_replace=False,
            timeout=60
        )

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="🖼 Bing Image Scraper (No API)")
    parser.add_argument("--keywords", type=str, required=True, help="Path to keywords.txt")
    parser.add_argument("--images_per_keyword", type=int, default=10)
    parser.add_argument("--save_dir", type=str, default="data/raw_bing_alt")

    args = parser.parse_args()

    with open(args.keywords, "r", encoding="utf-8") as f:
        keywords = [line.strip() for line in f if line.strip()]

    scrape_bing_images(keywords, args.save_dir, args.images_per_keyword)