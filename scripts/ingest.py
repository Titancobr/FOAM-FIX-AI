#!/usr/bin/env python3
"""Data ingestion script.
Replace the default URL with your own data source.
The script copies or downloads a zip file, extracts it into `data/raw`.
"""
import argparse
import shutil
from pathlib import Path
import subprocess
import sys

def main():
    parser = argparse.ArgumentParser(description="Ingest raw pose data.")
    parser.add_argument(
        "--src",
        default="https://example.com/pose-data.zip",
        help="URL or local path to zip containing raw data",
    )
    parser.add_argument(
        "--dest",
        default="data/raw",
        help="Destination directory (relative to repo root)",
    )
    args = parser.parse_args()

    dest = Path(args.dest)
    dest.mkdir(parents=True, exist_ok=True)

    src_path = Path(args.src)
    if src_path.is_file():
        # local file – just unpack
        shutil.unpack_archive(str(src_path), str(dest))
        print(f"✅ Copied local archive {src_path} → {dest}")
        return

    # otherwise download via curl (available in GitHub actions & mac)
    zip_path = dest / "raw.zip"
    print(f"Downloading {args.src} …")
    subprocess.run(["curl", "-L", "-o", str(zip_path), args.src], check=True)
    shutil.unpack_archive(str(zip_path), str(dest))
    zip_path.unlink()
    print(f"✅ Downloaded and extracted to {dest}")

if __name__ == "__main__":
    main()
