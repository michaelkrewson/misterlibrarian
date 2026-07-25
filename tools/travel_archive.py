#!/usr/bin/env python3
"""Archive the ORIGINAL travel photos and videos to S3, out of git's way.

The blog needs two different things from one set of files, and they pull in
opposite directions:

  * The PUBLISHED copies must be small and must live in the repo, because a
    static site can only serve what GitHub Pages is hosting. That is what
    tools/travel_photos.py produces — ~200-400 KB each, EXIF stripped.
  * The ORIGINALS are 4-6 MB a photo and 10 MB+ a video. Committing those would
    put tens of megabytes per dinner into a repo that is already ~270 MB of
    history — permanently, because git history cannot practically be pruned.
    But they are also the only full-quality copy, and videos never get published
    at all, so "just leave them on the Desktop" means one cleanup loses them.

So: originals go to S3, publish-sized copies go to git. Same live-on-disk /
durable-in-S3 split the rest of Michael's records use (tax, medical, insurance).

    python3 tools/travel_archive.py add ramen-ryoma-beaverton ~/Desktop/IMG_*.jpeg ~/Desktop/*.mp4
    python3 tools/travel_archive.py list
    python3 tools/travel_archive.py restore ramen-ryoma-beaverton ~/Desktop/restored
    python3 tools/travel_archive.py check

⚠ CREDENTIALS AND S3 CODE LIVE OUTSIDE THIS PUBLIC REPO. The store module comes
from the mstr-trader checkout and the keys from ~/.mstr-trader/backup.env (0600).
Nothing secret is committed here, and the tool degrades to a clear message rather
than an ImportError if that checkout isn't present.

⚠ KEYS ARE MANGLED ON THE WAY IN — DO NOT PARSE THEM BACK OUT. The store runs
every blob name and key through a sanitiser that upper-cases and turns "/" into
"-", so `ramen/IMG_6370.jpeg` is stored as `RAMEN-IMG_6370.JPEG`. Round-tripping
is safe because put and get apply the same transform, but the original filename
is NOT recoverable from the key. That is what the manifest is for. (The fleet
learned this the expensive way: a repair job once parsed keys back out and wrote
1,262 junk objects that could not be deleted, because the backup IAM user has no
DeleteObject permission. The same applies here — an upload is effectively
permanent, so check before you push 40 MB.)
"""
import argparse
import datetime as dt
import hashlib
import json
import os
import sys

BLOB_NAME = "travel_originals"      # -> s3://…/blobs/TRAVEL_ORIGINALS/
MANIFEST_KEY = "_manifest.json"

CONTENT_TYPES = {
    ".jpg": "image/jpeg", ".jpeg": "image/jpeg", ".png": "image/png",
    ".heic": "image/heic", ".heif": "image/heif", ".tif": "image/tiff",
    ".tiff": "image/tiff", ".dng": "image/x-adobe-dng", ".webp": "image/webp",
    ".mp4": "video/mp4", ".mov": "video/quicktime", ".m4v": "video/x-m4v",
}

# Where the S3 helper lives. Overridable so this isn't hard-wired to one machine.
MSTR_PATHS = [
    os.environ.get("MSTR_TRADER_DIR", ""),
    os.path.expanduser("~/projects/mstr-trader"),
    os.path.expanduser("~/mstr-trader"),
]


def store():
    """Import market_data_store from the mstr-trader checkout, or explain why not."""
    for p in MSTR_PATHS:
        if p and os.path.isfile(os.path.join(p, "market_data_store.py")):
            if p not in sys.path:
                sys.path.insert(0, p)
            import warnings
            with warnings.catch_warnings():
                warnings.simplefilter("ignore")
                import market_data_store as mds
            if not mds.enabled():
                sys.exit("S3 store is present but not configured/reachable "
                         "(check ~/.mstr-trader/backup.env).")
            return mds
    sys.exit("Could not find market_data_store.py. Set MSTR_TRADER_DIR to the "
             "mstr-trader checkout, e.g. MSTR_TRADER_DIR=~/projects/mstr-trader")


def sha256(path):
    h = hashlib.sha256()
    with open(path, "rb") as f:
        for chunk in iter(lambda: f.read(1 << 20), b""):
            h.update(chunk)
    return h.hexdigest()


def load_manifest(mds):
    raw = mds.get_blob(BLOB_NAME, MANIFEST_KEY)
    if not raw:
        return {}
    try:
        return json.loads(raw.decode("utf-8"))
    except (ValueError, UnicodeDecodeError):
        # Never silently start a fresh manifest over a corrupt one — that would
        # orphan every already-uploaded file, and they can't be deleted.
        sys.exit("The S3 manifest exists but is unreadable. Refusing to overwrite it. "
                 "Inspect it by hand before archiving anything else.")


def save_manifest(mds, man):
    ok = mds.put_blob(BLOB_NAME, MANIFEST_KEY,
                      json.dumps(man, indent=2, sort_keys=True).encode("utf-8"),
                      "application/json")
    if not ok:
        sys.exit("Failed to write the manifest to S3 — files may be uploaded but unindexed.")


def _human(n):
    return f"{n/1024/1024:.1f} MB" if n >= 1024 * 1024 else f"{n/1024:.0f} KB"


def cmd_add(args):
    mds = store()
    man = load_manifest(mds)
    entries = man.setdefault(args.slug, [])
    by_hash = {e["sha256"]: e for e in entries}

    total = skipped = 0
    for src in args.files:
        src = os.path.expanduser(src)
        if not os.path.isfile(src):
            print(f"  ! not a file, skipping: {src}")
            continue
        digest = sha256(src)
        name = os.path.basename(src)
        if digest in by_hash:
            # Content-addressed, so re-running the same command is free and safe.
            print(f"  = already archived: {name}")
            skipped += 1
            continue

        data = open(src, "rb").read()
        key = f"{args.slug}/{name}"
        ctype = CONTENT_TYPES.get(os.path.splitext(name)[1].lower(),
                                  "application/octet-stream")
        if args.dry_run:
            print(f"  → would upload {name}  {_human(len(data))}  [{ctype}]")
            total += len(data)
            continue
        if not mds.put_blob(BLOB_NAME, key, data, ctype):
            print(f"  ! UPLOAD FAILED: {name}")
            continue
        entry = {
            "original_name": name,
            "key": key,                       # pass this to get_blob verbatim
            "bytes": len(data),
            "sha256": digest,
            "content_type": ctype,
            "source_path": src,
            "archived_at": dt.datetime.now().astimezone().isoformat(timespec="seconds"),
        }
        entries.append(entry)
        by_hash[digest] = entry
        total += len(data)
        print(f"  ✓ {name}  {_human(len(data))}")

    if args.dry_run:
        print(f"\ndry run — {_human(total)} would be uploaded, nothing was written.")
        return
    if total or skipped:
        save_manifest(mds, man)
    print(f"\narchived {_human(total)} to s3 blobs/{BLOB_NAME.upper()}/ under '{args.slug}'"
          + (f" ({skipped} already there)" if skipped else ""))


def cmd_list(args):
    mds = store()
    man = load_manifest(mds)
    if not man:
        print("nothing archived yet")
        return
    grand = 0
    for slug in sorted(man):
        entries = man[slug]
        size = sum(e["bytes"] for e in entries)
        grand += size
        if args.slug and args.slug != slug:
            continue
        print(f"\n{slug}  —  {len(entries)} file(s), {_human(size)}")
        for e in sorted(entries, key=lambda x: x["original_name"]):
            print(f"    {e['original_name']:<40} {_human(e['bytes']):>9}   {e['archived_at'][:10]}")
    print(f"\ntotal archived: {_human(grand)} across {len(man)} entr{'y' if len(man)==1 else 'ies'}")


def cmd_restore(args):
    mds = store()
    man = load_manifest(mds)
    entries = man.get(args.slug)
    if not entries:
        sys.exit(f"nothing archived under '{args.slug}' — try: travel_archive.py list")
    dest = os.path.expanduser(args.dest)
    os.makedirs(dest, exist_ok=True)
    for e in entries:
        data = mds.get_blob(BLOB_NAME, e["key"])
        if data is None:
            print(f"  ! missing in S3: {e['original_name']}")
            continue
        got = hashlib.sha256(data).hexdigest()
        if got != e["sha256"]:
            # Report it rather than writing a file we know is wrong.
            print(f"  ! CHECKSUM MISMATCH, not written: {e['original_name']}")
            continue
        out = os.path.join(dest, e["original_name"])
        with open(out, "wb") as f:
            f.write(data)
        print(f"  ✓ {e['original_name']}  {_human(len(data))}")
    print(f"\nrestored into {dest}")


def cmd_check(args):
    """Which published posts have their originals safely archived, and which don't."""
    mds = store()
    man = load_manifest(mds)
    root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    src_dir = os.path.join(root, "source", "travel")
    posts = []
    if os.path.isdir(src_dir):
        posts = [f[11:-5] for f in sorted(os.listdir(src_dir))
                 if f.endswith(".html") and not f.startswith("_")]
    print("post                                   originals archived")
    print("-" * 62)
    gaps = 0
    for slug in posts:
        entries = man.get(slug)
        if entries:
            print(f"{slug:<38} ✓ {len(entries)} file(s), {_human(sum(e['bytes'] for e in entries))}")
        else:
            print(f"{slug:<38} — none")
            gaps += 1
    extra = sorted(set(man) - set(posts))
    for slug in extra:
        print(f"{slug:<38} (archived, no post yet)")
    if gaps:
        print(f"\n{gaps} post(s) with no archived originals. If you still have the "
              f"files:\n  python3 tools/travel_archive.py add <slug> <files…>")
    return gaps


def main():
    ap = argparse.ArgumentParser(description="Archive original travel media to S3.")
    sub = ap.add_subparsers(dest="cmd", required=True)

    a = sub.add_parser("add", help="upload originals for a post")
    a.add_argument("slug", help="post slug, e.g. ramen-ryoma-beaverton")
    a.add_argument("files", nargs="+")
    a.add_argument("--dry-run", action="store_true",
                   help="show what would upload without writing (uploads can't be deleted)")
    a.set_defaults(func=cmd_add)

    l = sub.add_parser("list", help="show what's archived")
    l.add_argument("slug", nargs="?")
    l.set_defaults(func=cmd_list)

    r = sub.add_parser("restore", help="pull a post's originals back down")
    r.add_argument("slug")
    r.add_argument("dest")
    r.set_defaults(func=cmd_restore)

    c = sub.add_parser("check", help="which posts are missing archived originals")
    c.set_defaults(func=cmd_check)

    args = ap.parse_args()
    args.func(args)


if __name__ == "__main__":
    main()
