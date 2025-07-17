#!/usr/bin/env python3
"""
Japanese Image Dataset Pipeline
"""

import argparse
import subprocess
import os

def run_scraper(script, keywords_file, save_dir, images_per_keyword):
    print(f"🚀 Running scraper: {script}")
    subprocess.run([
        "python3", script,
        "--keywords", keywords_file,
        "--images_per_keyword", str(images_per_keyword),
        "--save_dir", save_dir
    ])

def run_ocr(input_dir, output_dir, annotation_path):
    print("🔍 Running OCR filtering...")
    subprocess.run([
        "python3", "scripts/ocr/filter_images_easyocr_japanese.py",
        "--input_dir", input_dir,
        "--output_dir", output_dir,
        "--annotation_path", annotation_path
    ])

def run_zip(processed_dir, output_zip):
    print("📦 Zipping processed dataset...")
    subprocess.run([
        "python3", "scripts/utils/zip.py",
        "--processed_dir", processed_dir,
        "--output_zip", output_zip
    ])

def main():
    parser = argparse.ArgumentParser(description="Japanese Dataset Pipeline")
    parser.add_argument("--keywords", type=str, required=True, help="Path to keywords.txt")
    parser.add_argument("--images_per_keyword", type=int, default=5, help="Images per keyword")
    parser.add_argument("--raw_dir", type=str, default="data/raw_japanese", help="Raw images directory")
    parser.add_argument("--processed_dir", type=str, default="data/processed_japanese", help="Processed images directory")
    parser.add_argument("--zip_path", type=str, default="data/japanese_dataset.zip", help="Output zip file")
    args = parser.parse_args()

    # Step 1: Scraping
    sources = [
        "scripts/scrapers/image_scraper_pixabay_jp.py",
        "scripts/scrapers/image_scraper_pexels_jp.py",
        "scripts/scrapers/image_scraper_unsplash_jp.py",
        "scripts/scrapers/image_scraper_google_cli.py",
        "scripts/scrapers/image_scraper_bing_cli.py",
        "scripts/scrapers/image_scraper_ddg_cli.py",
        "scripts/scrapers/image_scraper_yahoo_japan_selenium.py"
    ]
    for script in sources:
        run_scraper(script, args.keywords, args.raw_dir, args.images_per_keyword)

    # Step 2: OCR Filter
    annotation_path = os.path.join(args.processed_dir, "annotations.json")
    run_ocr(args.raw_dir, args.processed_dir, annotation_path)

    # Step 3: Zipping
    run_zip(args.processed_dir, args.zip_path)

    print("✅ Japanese pipeline completed.")

if __name__ == "__main__":
    main()