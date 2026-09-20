#!/usr/bin/env python3
"""
Unpack downloaded models from Google Colab into the project directory.

Usage:
    python3 -m training.unpack_models
    python3 -m training.unpack_models --zip ~/Downloads/formfix_models_26_classes.zip
"""

import argparse
from pathlib import Path
import shutil
import zipfile


def parse_args():
    parser = argparse.ArgumentParser(description="Unpack trained Colab models into AI-Trainer/models.")
    parser.add_argument(
        "--zip",
        default="",
        help="Path to downloaded formfix_models_26_classes.zip (default: auto-searches ~/Downloads).",
    )
    return parser.parse_args()


def main():
    args = parse_args()
    project_root = Path(__file__).resolve().parent.parent
    target_models_dir = project_root / "models"
    target_models_dir.mkdir(parents=True, exist_ok=True)

    zip_path = None
    if args.zip:
        p = Path(args.zip).expanduser()
        if p.exists():
            zip_path = p
    else:
        # Search common download locations
        downloads_dir = Path.home() / "Downloads"
        candidates = sorted(downloads_dir.glob("*formfix*models*.zip"), key=lambda p: p.stat().st_mtime, reverse=True)
        if candidates:
            zip_path = candidates[0]
        else:
            # Check current workspace
            local_candidates = sorted(project_root.glob("*models*.zip"), key=lambda p: p.stat().st_mtime, reverse=True)
            if local_candidates:
                zip_path = local_candidates[0]

    if not zip_path or not zip_path.exists():
        print("❌ Could not locate 'formfix_models_26_classes.zip'.")
        print("Please specify the path with:")
        print("  python3 -m training.unpack_models --zip /path/to/formfix_models_26_classes.zip")
        return

    print(f"📦 Found model package: {zip_path}")
    print(f"📂 Extracting directly into: {project_root}...")

    with zipfile.ZipFile(zip_path, "r") as z:
        for member in z.namelist():
            # If internal path already starts with models/, extract directly
            out_file = project_root / member
            out_file.parent.mkdir(parents=True, exist_ok=True)
            with z.open(member) as src, open(out_file, "wb") as dst:
                shutil.copyfileobj(src, dst)
            sz_mb = out_file.stat().st_size / 1e6
            print(f"  ✅ Extracted: {member} ({sz_mb:.1f} MB)")

    print("\n🎉 All 26-class models and label mappings are ready in models/!")
    print("Files available:")
    for f in ["exercise_lstm.keras", "exercise_bilstm.keras", "posture_transformer.keras", "label_names.json"]:
        target_f = target_models_dir / f
        if target_f.exists():
            print(f"  - models/{f}")


if __name__ == "__main__":
    main()
