#!/usr/bin/env python3
"""Resize and compress photos for The Librarian Abroad (/travel/).

A phone photo is 3–6 MB and 4000px wide. A hundred of those would add half a
gigabyte to a repo that is already ~270 MB of git history — and git history is
forever, so an oversized photo committed once can never really be taken back out.
This is the gate: everything that goes into travel/img/ goes through here first.

    python3 tools/travel_photos.py ~/Desktop/lisbon/*.jpg
    python3 tools/travel_photos.py --name sardines ~/Desktop/IMG_4417.jpeg
    python3 tools/travel_photos.py --check          # audit what's already there

It prints the filename to paste into a post's `hero:` line or <figure> tag.

Defaults: 1600px on the long edge, JPEG quality 82, progressive — comfortably
sharp on a retina laptop at the ~860px column this site renders at, and typically
150–350 KB per photo. EXIF is STRIPPED, which matters: phone photos carry GPS
coordinates, and this repo is public.
"""
import argparse
import os
import re
import sys

try:
    from PIL import Image, ImageOps
except ImportError:
    sys.exit("Pillow is required:  python3 -m pip install Pillow")

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
IMG_DIR = os.path.join(ROOT, "travel", "img")

MAX_EDGE = 1600
QUALITY = 82
WARN_KB = 500          # flag anything above this in --check


def slugify(name):
    base = os.path.splitext(os.path.basename(name))[0].lower()
    base = re.sub(r"[^a-z0-9]+", "-", base).strip("-")
    return base or "photo"


def unique_path(stem):
    """Never silently overwrite an existing photo — a second `IMG_4417.jpeg` from a
    different trip would otherwise replace the first one in every post using it."""
    path = os.path.join(IMG_DIR, stem + ".jpg")
    if not os.path.exists(path):
        return path
    n = 2
    while os.path.exists(os.path.join(IMG_DIR, "{}-{}.jpg".format(stem, n))):
        n += 1
    return os.path.join(IMG_DIR, "{}-{}.jpg".format(stem, n))


def convert(src, name=None, max_edge=MAX_EDGE, quality=QUALITY):
    with Image.open(src) as im:
        # Honour the EXIF orientation flag BEFORE stripping EXIF, or portrait
        # photos from a phone come out sideways.
        im = ImageOps.exif_transpose(im)
        if im.mode not in ("RGB", "L"):
            im = im.convert("RGB")
        before = im.size
        im.thumbnail((max_edge, max_edge), Image.LANCZOS)

        out = unique_path(slugify(name or src))
        os.makedirs(IMG_DIR, exist_ok=True)
        # No exif= argument -> EXIF (including GPS) is not carried over.
        im.save(out, "JPEG", quality=quality, optimize=True, progressive=True)

    kb = os.path.getsize(out) / 1024.0
    print("  {:<34} {}x{} -> {}x{}  {:.0f} KB".format(
        os.path.basename(out), before[0], before[1], im.size[0], im.size[1], kb))
    return out


def check():
    if not os.path.isdir(IMG_DIR):
        print("no travel/img/ yet")
        return 0
    total = 0.0
    fat = []
    for fn in sorted(os.listdir(IMG_DIR)):
        p = os.path.join(IMG_DIR, fn)
        if not os.path.isfile(p):
            continue
        kb = os.path.getsize(p) / 1024.0
        total += kb
        if kb > WARN_KB and not fn.endswith(".svg"):
            fat.append((fn, kb))
    print("travel/img/: {} files, {:.1f} MB total".format(
        len(os.listdir(IMG_DIR)), total / 1024.0))
    if fat:
        print("\n⚠ over {} KB — re-run these through the resizer:".format(WARN_KB))
        for fn, kb in sorted(fat, key=lambda x: -x[1]):
            print("   {:<40} {:.0f} KB".format(fn, kb))
    return len(fat)


def main():
    ap = argparse.ArgumentParser(description="Prepare photos for /travel/.")
    ap.add_argument("photos", nargs="*", help="source image files")
    ap.add_argument("--name", help="base filename to use (single photo only)")
    ap.add_argument("--max-edge", type=int, default=MAX_EDGE)
    ap.add_argument("--quality", type=int, default=QUALITY)
    ap.add_argument("--check", action="store_true", help="audit travel/img/ and exit")
    args = ap.parse_args()

    if args.check:
        sys.exit(0 if check() == 0 else 1)
    if not args.photos:
        ap.error("give me some photos (or --check)")
    if args.name and len(args.photos) > 1:
        ap.error("--name only makes sense with a single photo")

    print("writing into travel/img/ (EXIF stripped):")
    for src in args.photos:
        convert(src, args.name, args.max_edge, args.quality)
    print("\nPaste the filename into a post's `hero:` line or a <figure> tag.")


if __name__ == "__main__":
    main()
