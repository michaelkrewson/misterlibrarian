#!/usr/bin/env python3
"""Archive the original-language source texts behind The Mister Translation.

Why this exists: the project translates from two free third-party suppliers —
Mechon-Mamre (Masoretic Hebrew, https://mechon-mamre.org) and the SBLGNT
(Greek, via the bible.helloao.org API). Either could vanish. Every chapter we
have SHIPPED embeds its Hebrew/Greek in the built page, but chapters we have
NOT yet translated exist only upstream. This script downloads complete books
(whole books, not just translated chapters), checksums them into a manifest,
and mirrors everything to Michael's private S3 long-term storage.

PRIVATE ARCHIVE — the local copy lives in source/originals/ which is
.gitignored (never pushed to the public repo), and the S3 bucket is private.
We are insuring our own workflow, not redistributing anyone's edition.
(Mechon-Mamre claims copyright on its edition and has long blessed personal
offline copies; SBLGNT is CC BY 4.0. A private archival copy is safe on both.)

Usage:
    python3 tools/archive_sources.py            # fetch + manifest + S3 push
    python3 tools/archive_sources.py --no-push  # fetch + manifest only
    python3 tools/archive_sources.py --verify   # re-hash local vs manifest,
                                                # spot-check S3 round-trip

Idempotent/resumable: a file already on disk with non-trivial size is not
re-fetched (delete it locally to force). Polite: 1.5s between live requests.

To archive a NEW book, add one line to MECHON_BOOKS or SBLGNT_BOOKS below.
S3 layout: blobs/bible_sources/<FILE> (keys uppercased by the store) plus
blobs/bible_sources/MANIFEST.JSON. Restore via market_data_store.get_blob.
"""

from __future__ import annotations

import hashlib
import json
import sys
import time
import urllib.request
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
OUT = ROOT / "source" / "originals"
MANIFEST = OUT / "MANIFEST.json"
DELAY_S = 1.5
UA = ("Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) "
      "AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0 Safari/537.36")

# Mechon-Mamre Hebrew (Masoretic): book code -> (name, chapter count)
# URL: https://mechon-mamre.org/p/pt/pt{code}{chapter:02d}.htm
MECHON_BOOKS = {
    "01": ("Genesis", 50),
    "02": ("Exodus", 40),
    "03": ("Leviticus", 27),
    "04": ("Numbers", 36),
    "05": ("Deuteronomy", 34),
    "06": ("Joshua", 24),
    "07": ("Judges", 21),
    "08a": ("1 Samuel", 31),
    "08b": ("2 Samuel", 24),
    "09a": ("1 Kings", 22),
    "09b": ("2 Kings", 25),
    "10": ("Isaiah", 66),
    "11": ("Jeremiah", 52),
    "12": ("Ezekiel", 48),
    "13": ("Hosea", 14),
    "14": ("Joel", 4),
    "15": ("Amos", 9),
    "16": ("Obadiah", 1),
    "17": ("Jonah", 4),
    "18": ("Micah", 7),
    "19": ("Nahum", 3),
    "20": ("Habakkuk", 3),
    "24": ("Malachi", 3),
    "25a": ("1 Chronicles", 29),
    "25b": ("2 Chronicles", 36),
    "27": ("Job", 42),
    "28": ("Proverbs", 31),
    "29": ("Ruth", 4),
    "30": ("Song of Solomon", 8),
    "31": ("Ecclesiastes", 12),
    "32": ("Lamentations", 5),
    "33": ("Esther", 10),
    "34": ("Daniel", 12),
    "35a": ("Ezra", 10),
    "35b": ("Nehemiah", 13),
}

# SBLGNT Greek via helloao API: book id -> (name, chapter count)
# URL: https://bible.helloao.org/api/grc_sbl/{book}/{chapter}.json
SBLGNT_BOOKS = {
    "MAT": ("Matthew", 28),
    "MRK": ("Mark", 16),
    "LUK": ("Luke", 24),
    "JHN": ("John", 21),
    "2JN": ("2 John", 1),
    "3JN": ("3 John", 1),
    "JUD": ("Jude", 1),
    "REV": ("Revelation", 22),
}

MSTR_TRADER = Path.home() / "projects" / "mstr-trader"  # for market_data_store
S3_CATEGORY = "bible_sources"


def _fetch(url: str) -> bytes:
    req = urllib.request.Request(url, headers={"User-Agent": UA})
    with urllib.request.urlopen(req, timeout=30) as r:
        return r.read()


def _sha256(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def _plan() -> list[tuple[str, str, str]]:
    """-> [(subdir, filename, url), ...] for every chapter of every book."""
    jobs = []
    for code, (_name, n) in MECHON_BOOKS.items():
        for ch in range(1, n + 1):
            fn = f"pt{code}{ch:02d}.htm"
            jobs.append(("mechon", fn, f"https://mechon-mamre.org/p/pt/{fn}"))
    for book, (_name, n) in SBLGNT_BOOKS.items():
        for ch in range(1, n + 1):
            fn = f"{book}-{ch:02d}.json"
            jobs.append(("sblgnt", fn,
                         f"https://bible.helloao.org/api/grc_sbl/{book}/{ch}.json"))
    return jobs


def fetch_all() -> dict:
    manifest = {}
    if MANIFEST.exists():
        manifest = json.loads(MANIFEST.read_text())
    fetched = skipped = 0
    for subdir, fn, url in _plan():
        dest = OUT / subdir / fn
        dest.parent.mkdir(parents=True, exist_ok=True)
        rel = f"{subdir}/{fn}"
        if dest.exists() and dest.stat().st_size > 500:
            if rel not in manifest:  # backfill manifest for pre-existing files
                data = dest.read_bytes()
                manifest[rel] = {"url": url, "sha256": _sha256(data),
                                 "bytes": len(data),
                                 "fetched_at": datetime.now(timezone.utc).isoformat()}
            skipped += 1
            continue
        data = _fetch(url)
        if len(data) < 500:
            raise SystemExit(f"suspiciously small response ({len(data)}b): {url}")
        dest.write_bytes(data)
        manifest[rel] = {"url": url, "sha256": _sha256(data), "bytes": len(data),
                         "fetched_at": datetime.now(timezone.utc).isoformat()}
        fetched += 1
        print(f"  fetched {rel} ({len(data):,}b)", flush=True)
        time.sleep(DELAY_S)
    MANIFEST.write_text(json.dumps(manifest, indent=1, sort_keys=True))
    print(f"fetch done: {fetched} new, {skipped} already local, "
          f"{len(manifest)} in manifest", flush=True)
    return manifest


def _s3():
    sys.path.insert(0, str(MSTR_TRADER))
    import market_data_store as mds  # noqa: PLC0415
    if not mds.enabled():
        raise SystemExit("S3 store not enabled (missing ~/.mstr-trader/backup.env?)")
    return mds


def push_all(manifest: dict) -> None:
    mds = _s3()
    ok = fail = 0
    for rel in sorted(manifest):
        subdir, fn = rel.split("/", 1)
        data = (OUT / subdir / fn).read_bytes()
        ctype = "application/json" if fn.endswith(".json") else "text/html"
        # store key flattens the subdir: mechon/pt0101.htm -> MECHON-PT0101.HTM
        if mds.put_blob(S3_CATEGORY, f"{subdir}-{fn}", data, ctype):
            ok += 1
        else:
            fail += 1
            print(f"  !! S3 push failed: {rel}", flush=True)
    mds.put_blob(S3_CATEGORY, "MANIFEST.json",
                 json.dumps(manifest, indent=1, sort_keys=True).encode(),
                 "application/json")
    print(f"S3 push done: {ok} ok, {fail} failed (+ manifest)", flush=True)
    if fail:
        raise SystemExit("some S3 pushes failed — re-run to retry")


def verify(manifest: dict) -> None:
    bad = 0
    for rel, meta in sorted(manifest.items()):
        subdir, fn = rel.split("/", 1)
        p = OUT / subdir / fn
        if not p.exists() or _sha256(p.read_bytes()) != meta["sha256"]:
            print(f"  !! local mismatch/missing: {rel}")
            bad += 1
    print(f"local verify: {len(manifest) - bad}/{len(manifest)} match")
    mds = _s3()
    import random
    for rel in random.sample(sorted(manifest), min(3, len(manifest))):
        subdir, fn = rel.split("/", 1)
        blob = mds.get_blob(S3_CATEGORY, f"{subdir}-{fn}")
        state = ("OK" if blob is not None
                 and _sha256(blob) == manifest[rel]["sha256"] else "MISMATCH")
        print(f"  S3 spot-check {rel}: {state}")
        if state != "OK":
            bad += 1
    if bad:
        raise SystemExit("verification failures")


if __name__ == "__main__":
    args = set(sys.argv[1:])
    if "--verify" in args:
        verify(json.loads(MANIFEST.read_text()))
    else:
        m = fetch_all()
        if "--no-push" not in args:
            push_all(m)
