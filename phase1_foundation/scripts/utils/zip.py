import zipfile
import os
import argparse

def zip_folder(folder_path, output_zip):
    with zipfile.ZipFile(output_zip, "w", zipfile.ZIP_DEFLATED) as zipf:
        for foldername, subfolders, filenames in os.walk(folder_path):
            for filename in filenames:
                file_path = os.path.join(foldername, filename)
                arcname = os.path.relpath(file_path, folder_path)
                zipf.write(file_path, arcname)
    print(f"✅ Zipped folder saved as {output_zip}")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="📦 Zip Processed Folder")
    parser.add_argument("--processed_dir", type=str, required=True, help="Folder to zip")
    parser.add_argument("--output_zip", type=str, required=True, help="Output zip file path")
    args = parser.parse_args()

    zip_folder(args.processed_dir, args.output_zip)