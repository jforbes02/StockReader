"""
build_mag7_dataset.py
Build a MAG7 logo image dataset for training a classifier.

Pipeline:
  1. SCRAPE  - download images from Bing, several queries per company,
               so you get logos in varied real-world contexts.
  2. CLEAN   - drop corrupt / tiny images, normalize to RGB JPEG.
  3. DEDUPE  - remove near-duplicate images (perceptual hash).
  4. REPORT  - print how many usable images per company.

Output folder layout (feeds straight into the Colab ImageFolder code):
    mag7/
      Apple/  Microsoft/  Nvidia/  Amazon/  Google/  Meta/  Tesla/

Setup (run once):
    pip install icrawler Pillow imagehash

Run:
    python build_mag7_dataset.py

IMPORTANT — after it finishes, open each folder and delete obvious junk
by hand (wrong logos, memes, unrelated photos). Scraped search results are
noisy; ~10-15 min of human review is the difference between a model that
works and one that doesn't. This dataset is for a personal portfolio model
only — don't redistribute the raw images (logos are trademarks).
"""

import os
import shutil
from pathlib import Path

from PIL import Image
import imagehash
from icrawler.builtin import BingImageCrawler

# ----------------------------------------------------------------------
# CONFIG — tweak these
# ----------------------------------------------------------------------

OUT_DIR = Path("mag7")          # final cleaned dataset
RAW_DIR = Path("mag7_raw")      # temp scratch for raw downloads
PER_QUERY = 60                  # images to pull per query (before cleaning)
MIN_SIDE = 80                   # drop images smaller than this (px) on any side
HASH_CUTOFF = 4                 # lower = stricter dedupe (0 = identical only)

# Multiple queries per company => variety (context, angles, surfaces).
# Add/remove queries freely. First word groups them under the company folder.
QUERIES = {
    "Apple": [
        "Apple inc logo",
        "Apple logo storefront sign",
        "Apple logo on macbook",
        "Apple logo black white",
    ],
    "Microsoft": [
        "Microsoft logo",
        "Microsoft logo building sign",
        "Microsoft logo on laptop",
        "Microsoft four square logo",
    ],
    "Nvidia": [
        "Nvidia logo",
        "Nvidia logo green eye",
        "Nvidia logo on graphics card",
        "Nvidia logo sign",
    ],
    "Amazon": [
        "Amazon logo",
        "Amazon smile arrow logo",
        "Amazon logo on box",
        "Amazon logo storefront",
    ],
    "Google": [
        "Google logo",
        "Google G icon logo",
        "Google logo building sign",
        "Google logo on phone",
    ],
    "Meta": [
        "Meta company logo",
        "Meta infinity logo",
        "Meta logo sign headquarters",
        "Meta logo blue",
    ],
    "Tesla": [
        "Tesla logo",
        "Tesla T emblem logo",
        "Tesla logo on car",
        "Tesla logo storefront sign",
    ],
}

VALID_EXT = {".jpg", ".jpeg", ".png", ".webp", ".bmp"}


# ----------------------------------------------------------------------
# 1. SCRAPE
# ----------------------------------------------------------------------

def scrape():
    """Download raw images: one temp subfolder per query, then merge per brand."""
    for brand, queries in QUERIES.items():
        brand_raw = RAW_DIR / brand
        brand_raw.mkdir(parents=True, exist_ok=True)
        counter = 0

        for i, query in enumerate(queries):
            q_dir = brand_raw / f"_q{i}"
            q_dir.mkdir(parents=True, exist_ok=True)
            print(f"[scrape] {brand}: '{query}'")

            crawler = BingImageCrawler(
                downloader_threads=4,
                storage={"root_dir": str(q_dir)},
            )
            try:
                crawler.crawl(keyword=query, max_num=PER_QUERY)
            except Exception as e:
                print(f"   ! crawl failed for '{query}': {e}")

            # merge this query's files into the brand folder with unique names
            for f in q_dir.iterdir():
                if f.suffix.lower() in VALID_EXT:
                    dst = brand_raw / f"{brand.lower()}_{counter:04d}{f.suffix.lower()}"
                    shutil.move(str(f), str(dst))
                    counter += 1
            shutil.rmtree(q_dir, ignore_errors=True)

        print(f"[scrape] {brand}: {counter} raw images")


# ----------------------------------------------------------------------
# 2 + 3. CLEAN + DEDUPE
# ----------------------------------------------------------------------

def clean_and_dedupe():
    """Verify, resize-filter, normalize to RGB JPEG, and drop near-duplicates."""
    OUT_DIR.mkdir(parents=True, exist_ok=True)

    for brand in QUERIES:
        src = RAW_DIR / brand
        dst = OUT_DIR / brand
        dst.mkdir(parents=True, exist_ok=True)
        if not src.exists():
            continue

        seen_hashes = []   # list of imagehash objects we've kept
        kept = 0

        for f in sorted(src.iterdir()):
            if f.suffix.lower() not in VALID_EXT:
                continue
            try:
                # open + verify it's a real, non-truncated image
                with Image.open(f) as im:
                    im.verify()
                with Image.open(f) as im:
                    im = im.convert("RGB")
                    w, h = im.size
                    if min(w, h) < MIN_SIDE:
                        continue  # too small to be useful

                    # perceptual hash for near-dupe detection
                    ph = imagehash.phash(im)
                    if any(ph - k <= HASH_CUTOFF for k in seen_hashes):
                        continue  # near-duplicate of something we kept
                    seen_hashes.append(ph)

                    out_path = dst / f"{brand.lower()}_{kept:04d}.jpg"
                    im.save(out_path, "JPEG", quality=90)
                    kept += 1
            except Exception:
                continue  # corrupt / unreadable -> skip

        print(f"[clean]  {brand}: {kept} usable images")

    shutil.rmtree(RAW_DIR, ignore_errors=True)


# ----------------------------------------------------------------------
# 4. REPORT
# ----------------------------------------------------------------------

def report():
    print("\n=== FINAL DATASET (mag7/) ===")
    total = 0
    for brand in QUERIES:
        d = OUT_DIR / brand
        n = len(list(d.glob("*.jpg"))) if d.exists() else 0
        total += n
        flag = "  <-- LOW, add more queries" if n < 40 else ""
        print(f"  {brand:12s} {n:4d}{flag}")
    print(f"  {'TOTAL':12s} {total:4d}")
    print("\nNext: open each folder, delete obvious junk by hand, then train.")


if __name__ == "__main__":
    scrape()
    clean_and_dedupe()
    report()