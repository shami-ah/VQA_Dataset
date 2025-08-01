import argparse
import subprocess

def run_scraper(source, keywords_file, save_dir, images_per_keyword):
    print(f"🚀 Running scraper for {source}...")
    script_map = {
        "google": "scripts/scrapers/image_scraper_google_cli.py",
        "bing": "scripts/scrapers/image_scraper_bing_cli.py",
        "duckduckgo": "scripts/scrapers/image_scraper_ddg_cli.py",
        "pinterest": "scripts/scrapers/image_scraper_pinterest_cli.py",
        "flickr": "scripts/scrapers/image_scraper_flickr_commons_hindi.py",
        "unsplash": "scripts/scrapers/image_scraper_unsplash_jp.py",
        "pixabay": "scripts/scrapers/image_scraper_pixabay_jp.py",
        "frenchall":"scripts/scrapers/image_scraper_french_all.py"
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
    print("🔍 Running OCR filtering for French...")
    subprocess.run([
        "python3", "scripts/ocr/filter_images_french_ocr.py",
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
    parser = argparse.ArgumentParser(description="📊 French Image Dataset Pipeline")
    parser.add_argument("--keywords", type=str, required=True)
    parser.add_argument("--images_per_keyword", type=int, default=5)
    parser.add_argument("--raw_dir", type=str, default="data/raw_french")
    parser.add_argument("--processed_dir", type=str, default="data/processed_french")
    parser.add_argument("--zip_path", type=str, default="data/french_dataset.zip")

    args = parser.parse_args()

    for src in [
        "google", "bing", "duckduckgo", "pinterest", "flickr",
        "unsplash", "pixabay", "frenchall"
    ]:
        run_scraper(src, args.keywords, args.raw_dir, args.images_per_keyword)

    run_ocr(args.raw_dir, args.processed_dir)
    run_zip(args.processed_dir, args.zip_path)

    print("✅ French dataset pipeline completed.")