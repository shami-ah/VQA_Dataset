import argparse
import subprocess

def run_scraper(source, keywords_file, save_dir, images_per_keyword):
    print(f"🚀 Running scraper for {source}...")
    script_map = {
        "bing": "phase1_foundation/scripts/scrapers/image_scraper_bing_cli.py",
        "google": "phase1_foundation/scripts/scrapers/image_scraper_google_cli.py"
    }

    if source not in script_map:
        print(f"❌ Unknown source: {source}")
        return

    subprocess.run([
        "python3", script_map[source],
        "--keywords", keywords_file,
        "--images_per_keyword", str(images_per_keyword),
        "--save_dir", save_dir
    ])

def run_ocr(input_dir, output_dir):
    print("🔍 Running OCR filtering...")
    subprocess.run([
        "python3", "phase1_foundation/scripts/ocr/filter_images_urdu_ocr.py",
        "--input_dir", input_dir,
        "--output_dir", output_dir
    ])

def run_zip(processed_dir, output_zip):
    print("📦 Zipping processed dataset...")
    subprocess.run([
        "python3", "phase1_foundation/scripts/utils/zip.py",
        "--processed_dir", processed_dir,
        "--output_zip", output_zip
    ])

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="📊 Urdu Image Dataset Pipeline")
    parser.add_argument("--keywords", type=str, required=True)
    parser.add_argument("--images_per_keyword", type=int, default=5)
    parser.add_argument("--raw_dir", type=str, default="data/raw_urdu")
    parser.add_argument("--processed_dir", type=str, default="data/processed_urdu")
    parser.add_argument("--zip_path", type=str, default="data/urdu_dataset.zip")

    args = parser.parse_args()

    # Step 1: Scraping from working sources
    for src in ["bing", "google"]:
        run_scraper(src, args.keywords, args.raw_dir, args.images_per_keyword)

    # Step 2: OCR Filter
    run_ocr(args.raw_dir, args.processed_dir)

    # Step 3: Zipping
    run_zip(args.processed_dir, args.zip_path)

    print("✅ Urdu dataset pipeline completed.")