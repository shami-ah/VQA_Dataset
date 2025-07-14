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

def run_ocr(input_dir, output_dir):
    print("🔍 Running OCR...")
    subprocess.run([
        "python3", "scripts/ocr/filter_images_easyocr_korean.py",
        "--input_dir", input_dir,
        "--output_dir", output_dir
    ])

def run_zip(processed_dir, output_zip):
    print("📦 Zipping dataset...")
    subprocess.run([
        "python3", "scripts/utils/zip.py",
        "--processed_dir", processed_dir,
        "--output_zip", output_zip
    ])

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--keywords", type=str, required=True)
    parser.add_argument("--images_per_keyword", type=int, default=5)
    parser.add_argument("--raw_dir", type=str, default="data/raw_korean")
    parser.add_argument("--processed_dir", type=str, default="data/processed_korean")
    parser.add_argument("--zip_path", type=str, default="data/korean_dataset.zip")
    args = parser.parse_args()

    # Run each scraper
    run_scraper("scripts/scrapers/image_scraper_google_cli.py", args.keywords, args.raw_dir, args.images_per_keyword)
    run_scraper("scripts/scrapers/image_scraper_bing_cli.py", args.keywords, args.raw_dir, args.images_per_keyword)
    run_scraper("scripts/scrapers/image_scraper_daum_selenium_korean.py", args.keywords, args.raw_dir, args.images_per_keyword)
    run_scraper("scripts/scrapers/image_scraper_naver_selenium_korean.py", args.keywords, args.raw_dir, args.images_per_keyword)
    run_scraper("scripts/scrapers/image_scraper_korean_blog_news.py", args.keywords, args.raw_dir, args.images_per_keyword)  # ✅ Added here

    run_ocr(args.raw_dir, args.processed_dir)
    run_zip(args.processed_dir, args.zip_path)

    print("✅ Korean pipeline complete.")