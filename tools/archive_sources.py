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
import random
import re
import sys
import time
import urllib.error
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
    "21": ("Zephaniah", 3),
    "22": ("Haggai", 2),
    "23": ("Zechariah", 14),
    "24": ("Malachi", 3),
    "25a": ("1 Chronicles", 29),
    "25b": ("2 Chronicles", 36),
    "26": ("Psalms", 150),
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
    "ACT": ("Acts", 28),
    "ROM": ("Romans", 16),
    "1CO": ("1 Corinthians", 16),
    "2CO": ("2 Corinthians", 13),
    "GAL": ("Galatians", 6),
    "EPH": ("Ephesians", 6),
    "PHP": ("Philippians", 4),
    "COL": ("Colossians", 4),
    "1TH": ("1 Thessalonians", 5),
    "2TH": ("2 Thessalonians", 3),
    "1TI": ("1 Timothy", 6),
    "2TI": ("2 Timothy", 4),
    "TIT": ("Titus", 3),
    "PHM": ("Philemon", 1),
    "HEB": ("Hebrews", 13),
    "JAS": ("James", 5),
    "1PE": ("1 Peter", 5),
    "2PE": ("2 Peter", 3),
    "1JN": ("1 John", 5),
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


def _mechon_wholebook_backfill(manifest: dict) -> int:
    """Fill any Mechon chapter the per-chapter URL scheme cannot reach.

    Mechon's flat scheme is pt{code}{chapter:02d}.htm — TWO digits — so a book
    with more than 99 chapters has no per-chapter URL for the rest, and every
    such request 404s. Psalms is the only book in the Bible this affects
    (100-150), which is why the archive sat 51 psalms short and Psalm 107 could
    not be checked when Matthew 8 wanted it.

    The fix stays with the SAME source of record rather than introducing a
    second Hebrew text: Mechon also serves the whole book on one page at
    pt{code}.htm (Psalms is ~600KB there), and that page is exactly 150
    <H2>-delimited chapters. We fetch it once and slice.

    Refuses to write anything unless the slice verifies: the chapter count must
    match the book's known length AND every heading must read "Chapter N" in
    order. A guessed slice is worse than a gap.

    Each written file is wrapped so it is indistinguishable in USE from a
    per-chapter fetch — in particular it carries the same
    "<TITLE>Psalms 107 / Hebrew - English Bible / Mechon-Mamre</TITLE>" line,
    because reading that title back is how a careless lookup gets caught (a
    Daniel 7:13 query once silently returned Job 7:13). The manifest records
    the whole-book URL plus derived_from, so nobody later mistakes these for
    individual fetches.
    """
    need = {}   # code -> [chapter, ...]
    for code, (_name, n) in MECHON_BOOKS.items():
        for ch in range(1, n + 1):
            if ch <= 99:
                continue          # the per-chapter scheme reaches these
            dest = OUT / "mechon" / f"pt{code}{ch}.htm"
            if not (dest.exists() and dest.stat().st_size > 500):
                need.setdefault(code, []).append(ch)
    if not need:
        return 0

    written = 0
    for code, chapters in need.items():
        name, n = MECHON_BOOKS[code]
        url = f"https://mechon-mamre.org/p/pt/pt{code}.htm"
        print(f"  whole-book backfill: {name} needs {len(chapters)} chapter(s) "
              f"-> {url}", flush=True)
        page = _fetch(url).decode("utf-8", "replace")
        time.sleep(DELAY_S)
        parts = [p for p in re.split(r"(?=<H2[^>]*>)", page) if re.match(r"<H2", p)]
        if len(parts) != n:
            raise SystemExit(f"{name}: whole-book page sliced into {len(parts)} "
                             f"chapters, expected {n} — refusing to write")
        for idx, chunk in enumerate(parts, start=1):
            head = re.search(r"<H2[^>]*>(.*?)</H2>", chunk, re.S)
            label = re.sub(r"<[^>]+>", "", head.group(1) if head else "").strip()
            if label.lower() != f"chapter {idx}":
                raise SystemExit(f"{name}: chapter {idx} heading reads "
                                 f"{label!r} — refusing to write a guessed slice")
        for ch in chapters:
            body = parts[ch - 1]
            doc = ("<!DOCTYPE HTML>\n<HTML>\n<HEAD>\n"
                   '<meta http-equiv="Content-Type" content="text/html; charset=UTF-8">\n'
                   f"<TITLE>{name} {ch} / Hebrew - English Bible / Mechon-Mamre</TITLE>\n"
                   f"<!-- sliced by tools/archive_sources.py from {url} "
                   f"(Mechon has no per-chapter URL above chapter 99) -->\n"
                   "</HEAD>\n<BODY>\n" + body + "\n</BODY>\n</HTML>\n")
            data = doc.encode("utf-8")
            dest = OUT / "mechon" / f"pt{code}{ch}.htm"
            dest.parent.mkdir(parents=True, exist_ok=True)
            dest.write_bytes(data)
            manifest[f"mechon/pt{code}{ch}.htm"] = {
                "url": url,
                "derived_from": f"whole-book page, <H2> slice {ch} of {n}",
                "sha256": _sha256(data), "bytes": len(data),
                "fetched_at": datetime.now(timezone.utc).isoformat()}
            written += 1
        print(f"  wrote {len(chapters)} chapter file(s) for {name}", flush=True)
    return written


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
    fetched = skipped = missing = 0
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
        try:
            data = _fetch(url)
        except urllib.error.HTTPError as e:
            # A supplier that does not serve a chapter at the expected URL must
            # NOT wedge the archive of every OTHER book. Skip-and-report a
            # 404; anything else is a real problem and still raises.
            # NB the known case here — Mechon has no pt26NNN for Psalms
            # 100-150, because its per-chapter scheme is two-digit — is now
            # FIXED by _mechon_wholebook_backfill() below, which slices those
            # chapters out of the whole-book page. This branch stays as the
            # general safety net, not as the Psalms workaround it once was.
            if e.code == 404:
                missing += 1
                print(f"  missing (404), skipping: {rel}", flush=True)
                time.sleep(DELAY_S)
                continue
            raise
        if len(data) < 500:
            raise SystemExit(f"suspiciously small response ({len(data)}b): {url}")
        dest.write_bytes(data)
        manifest[rel] = {"url": url, "sha256": _sha256(data), "bytes": len(data),
                         "fetched_at": datetime.now(timezone.utc).isoformat()}
        fetched += 1
        print(f"  fetched {rel} ({len(data):,}b)", flush=True)
        time.sleep(DELAY_S)
    derived = _mechon_wholebook_backfill(manifest)
    MANIFEST.write_text(json.dumps(manifest, indent=1, sort_keys=True))
    print(f"fetch done: {fetched} new, {skipped} already local, "
          f"{missing} missing-at-source (404), {derived} sliced from a "
          f"whole-book page, {len(manifest)} in manifest", flush=True)
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
