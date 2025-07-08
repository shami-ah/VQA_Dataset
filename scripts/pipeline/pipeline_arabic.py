import argparse
import subprocess
import os

def run_scraper(source, keywords_file, save_dir, images_per_source):
    print(f"🚀 Running scraper for {source}...")
    script_map = {
        "bing": "scripts/scrapers/image_scraper_bing_cli.py",
        "google": "scripts/scrapers/image_scraper_google_cli.py",
        "pinterest": "scripts/scrapers/image_scraper_pinterest_cli.py",
        "stock": "scripts/scrapers/image_scraper_stock_sites.py"
    }

    if source not in script_map:
        print(f"❌ Unknown source: {source}")
        return

    flag = "--images_per_keyword" if source != "stock" else "--images_per_source"

    subprocess.run([
        "python3", script_map[source],
        "--keywords", keywords_file,
        flag, str(images_per_source),
        "--save_dir", save_dir
    ])

def run_ocr(input_dir, output_dir):
    print("🔍 Running OCR filtering...")
    subprocess.run([
        "python3", "scripts/ocr/filter_images_easyocr_cli.py",
        "--input_dir", input_dir,
        "--output_dir", output_dir
    ])

def run_zip(processed_dir, output_zip):
    print("📦 Zipping processed dataset...")
    subprocess.run([
        "python3", "scripts/utils/zip.py",
        "--processed_dir", processed_dir,
        "--output_zip", output_zip
    ])

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="📊 Arabic Dataset Pipeline")
    parser.add_argument("--keywords", type=str, required=True)
    parser.add_argument("--images_per_source", type=int, default=5)
    parser.add_argument("--raw_dir", type=str, default="data/raw_arabic")
    parser.add_argument("--processed_dir", type=str, default="data/processed_arabic")
    parser.add_argument("--zip_path", type=str, default="data/arabic_dataset.zip")

    args = parser.parse_args()

    # Step 1: Scraping
    for src in ["bing", "google", "pinterest", "stock"]:
        run_scraper(src, args.keywords, args.raw_dir, args.images_per_source)

    # Step 2: OCR Filter
    run_ocr(args.raw_dir, args.processed_dir)

    # Step 3: Zipping
    run_zip(args.processed_dir, args.zip_path)

    print("✅ Arabic pipeline completed.")