import argparse
import subprocess

def run_scraper(args):
    print("🚀 Running image scraper...")
    subprocess.run([
        "python3", "scripts/image_scraper_ddg_cli.py",
        "--keywords", args.keywords,
        "--max_images", str(args.max_images),
        "--images_per_keyword", str(args.images_per_keyword),
        "--save_dir", args.save_dir
    ])

def run_ocr_filter(args):
    print("🔍 Running OCR filtering...")
    subprocess.run([
        "python3", "scripts/filter_images_easyocr.py",
        "--input_dir", args.save_dir,
        "--output_dir", args.filtered_dir
    ])

def run_enrichment(args):
    print("🧠 Enriching OCR metadata...")
    subprocess.run([
        "python3", "scripts/enrich_metadata.py",
        "--img_dir", args.filtered_dir,
        "--output_json", "metadata/arabic_image_metadata.json"
    ])

def run_zip_upload():
    print("📦 Zipping and uploading to Drive...")
    subprocess.run(["python3", "scripts/zip_and_upload.py"])

def main():
    parser = argparse.ArgumentParser(description="🔗 Arabic Image Pipeline")
    parser.add_argument("--keywords", type=str, default="scripts/config/keywords.txt", help="Path to keywords.txt")
    parser.add_argument("--max_images", type=int, default=3000, help="Total images to scrape")
    parser.add_argument("--images_per_keyword", type=int, default=100, help="Images per keyword")
    parser.add_argument("--save_dir", type=str, default="data/raw_images", help="Scraper output folder")
    parser.add_argument("--filtered_dir", type=str, default="data/processed", help="Filtered OCR output folder")
    args = parser.parse_args()

    run_scraper(args)
    run_ocr_filter(args)
    run_enrichment(args)
    run_zip_upload()

    print("🎉 Pipeline complete. Dataset is ready and backed up to Drive.")

if __name__ == "__main__":
    main()