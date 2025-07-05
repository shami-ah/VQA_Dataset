import zipfile
import os
import shutil
import sys

# === CONFIG ===
FILTERED_DIR = "data/processed_test"
METADATA_JSON = "metadata/arabic_image_metadata.json"
ZIP_PATH = "dataset.zip"

# === Create zip archive ===
with zipfile.ZipFile(ZIP_PATH, "w", zipfile.ZIP_DEFLATED) as zipf:
    # Add filtered images
    for fname in os.listdir(FILTERED_DIR):
        fpath = os.path.join(FILTERED_DIR, fname)
        if os.path.isfile(fpath):
            zipf.write(fpath, arcname=fname)

    # Add metadata JSON
    if os.path.exists(METADATA_JSON):
        zipf.write(METADATA_JSON, arcname=os.path.basename(METADATA_JSON))
        print(f"📎 Added metadata: {METADATA_JSON}")
    else:
        print("⚠️ Metadata JSON not found, skipping.")

print(f"📦 Zipped to: {ZIP_PATH}")

# === Upload to Google Drive (if in Colab) ===
try:
    import google.colab
    from google.colab import drive

    print("🔗 Mounting Google Drive...")
    drive.mount('/content/drive')
    shutil.copy(ZIP_PATH, '/content/drive/MyDrive/')
    print("✅ Uploaded to Google Drive → MyDrive/")
except ImportError:
    print("🖥️ Skipping Drive upload (not in Colab).")