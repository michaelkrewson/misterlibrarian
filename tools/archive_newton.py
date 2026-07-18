#!/usr/bin/env python3
"""Archive Isaac Newton's public-domain biblical works for The Mister Translation.

Why this exists: Newton wrote more on theology and Scripture than on physics,
and three of his works bear directly on books this project already translates —
his 'Observations upon the Prophecies of Daniel and the Apocalypse of St. John'
(the site has Daniel and Revelation), his textual criticism of the Johannine
Comma and 1 Timothy 3:16 (the New Testament apparatus page flags exactly those
disputed passages), and his biblical/ancient chronology (the site has its own
chronology). All three are fully PUBLIC DOMAIN (Newton died 1727). We keep our
own copies so a dead upstream link can never lose them for us.

Unlike the Hebrew/Greek source archive (tools/archive_sources.py), these texts
carry NO copyright restriction, so the local copies live in a git-TRACKED folder
(source/newton/) — committed to the public repo is itself a durability guarantee
— AND are mirrored to Michael's private S3 for independence from GitHub.

Sources: Project Gutenberg (clean transcriptions) where available, else the
Internet Archive's OCR full text. Every work records its source URL + a sha256
in the manifest, so the provenance is auditable and the archive is restorable.

Usage:
    python3 tools/archive_newton.py            # fetch + manifest + S3 push
    python3 tools/archive_newton.py --no-push  # fetch + manifest only
    python3 tools/archive_newton.py --restore  # rebuild local copies from S3
    python3 tools/archive_newton.py --verify   # re-hash local vs manifest

Idempotent: a file already on disk with non-trivial size is not re-fetched
(delete it locally to force). Polite: a short pause between live requests.
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
OUT = ROOT / "source" / "newton"
MANIFEST = OUT / "MANIFEST.json"
DELAY_S = 2.0
UA = ("Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) "
      "AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0 Safari/537.36")

MSTR_TRADER = Path.home() / "projects" / "mstr-trader"  # for market_data_store
S3_CATEGORY = "newton_works"

# Newton's public-domain biblical works we mirror. Each: local filename ->
# metadata + the stable full-text URL we pull from.
WORKS = {
    "newton-observations-daniel-apocalypse.txt": dict(
        title="Observations upon the Prophecies of Daniel, and the Apocalypse of St. John",
        author="Isaac Newton",
        written="before 1727",
        published="1733 (posthumous)",
        source="Project Gutenberg #16878",
        url="https://www.gutenberg.org/cache/epub/16878/pg16878.txt",
        note="Newton's historicist reading of the two great apocalyptic books — the "
             "same Daniel and Revelation this translation has begun. The manuscript in "
             "which he calculated the world would not end before the year 2060 is a "
             "separate unpublished paper (Yahuda MS 7.3g), not this book.",
    ),
    "newton-chronology-of-ancient-kingdoms.txt": dict(
        title="The Chronology of Ancient Kingdoms Amended",
        author="Isaac Newton",
        written="before 1727",
        published="1728 (posthumous)",
        source="Project Gutenberg #15784",
        url="https://www.gutenberg.org/cache/epub/15784/pg15784.txt",
        note="Newton's attempt to re-date the ancient world against the biblical record "
             "— his own version of the project behind this site's Chronology feature. His "
             "conclusions are now dated, but the method (weighing sources, not asserting) "
             "is the same spirit.",
    ),
    "newton-two-notable-corruptions-of-scripture.txt": dict(
        title="An Historical Account of Two Notable Corruptions of Scripture",
        author="Isaac Newton",
        written="c. 1690 (a letter to John Locke)",
        published="1754 (posthumous); this copy is the 1841 reprint",
        source="Internet Archive (83824690-…), OCR full text",
        url=("https://archive.org/download/"
             "83824690-an-historical-account-of-two-notable-corruptions-of-scripture/"
             "83824690-An-Historical-Account-of-Two-Notable-Corruptions-of-Scripture_djvu.txt"),
        note="Newton's textual criticism arguing that the Johannine Comma (1 John 5:7) "
             "and 1 Timothy 3:16 are later corruptions — the two passages the site's New "
             "Testament apparatus page already names as famously disputed. NB: this is OCR "
             "of a scanned reprint, so expect scanning artefacts; the 1733/1728 works above "
             "are clean Gutenberg transcriptions.",
    ),
}


def _fetch(url: str) -> bytes:
    req = urllib.request.Request(url, headers={"User-Agent": UA})
    with urllib.request.urlopen(req, timeout=60) as r:
        return r.read()


def _sha256(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def fetch_all() -> dict:
    OUT.mkdir(parents=True, exist_ok=True)
    manifest = json.loads(MANIFEST.read_text()) if MANIFEST.exists() else {}
    fetched = skipped = 0
    for fn, meta in WORKS.items():
        dest = OUT / fn
        if dest.exists() and dest.stat().st_size > 1000:
            if fn not in manifest:  # backfill manifest for a pre-existing file
                data = dest.read_bytes()
                manifest[fn] = {**{k: meta[k] for k in
                                   ("title", "author", "written", "published", "source", "url", "note")},
                                "sha256": _sha256(data), "bytes": len(data),
                                "fetched_at": datetime.now(timezone.utc).isoformat()}
            skipped += 1
            continue
        data = _fetch(meta["url"])
        if len(data) < 1000:
            raise SystemExit(f"suspiciously small response ({len(data)}b): {meta['url']}")
        dest.write_bytes(data)
        manifest[fn] = {**{k: meta[k] for k in
                           ("title", "author", "written", "published", "source", "url", "note")},
                        "sha256": _sha256(data), "bytes": len(data),
                        "fetched_at": datetime.now(timezone.utc).isoformat()}
        fetched += 1
        print(f"  fetched {fn} ({len(data):,}b) — {meta['title']}", flush=True)
        time.sleep(DELAY_S)
    MANIFEST.write_text(json.dumps(manifest, indent=1, sort_keys=True))
    print(f"fetch done: {fetched} new, {skipped} already local, {len(manifest)} in manifest", flush=True)
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
    for fn in sorted(manifest):
        data = (OUT / fn).read_bytes()
        if mds.put_blob(S3_CATEGORY, fn, data, "text/plain"):
            ok += 1
        else:
            fail += 1
            print(f"  !! S3 push failed: {fn}", flush=True)
    mds.put_blob(S3_CATEGORY, "MANIFEST.json",
                 json.dumps(manifest, indent=1, sort_keys=True).encode(), "application/json")
    print(f"S3 push done: {ok} ok, {fail} failed (+ manifest)", flush=True)
    if fail:
        raise SystemExit("some S3 pushes failed — re-run to retry")


def restore() -> None:
    mds = _s3()
    OUT.mkdir(parents=True, exist_ok=True)
    blob = mds.get_blob(S3_CATEGORY, "MANIFEST.json")
    if blob is None:
        raise SystemExit("no MANIFEST.json in S3 to restore from")
    manifest = json.loads(blob)
    MANIFEST.write_text(json.dumps(manifest, indent=1, sort_keys=True))
    ok = 0
    for fn in sorted(manifest):
        data = mds.get_blob(S3_CATEGORY, fn)
        if data is None:
            print(f"  !! missing in S3: {fn}"); continue
        (OUT / fn).write_bytes(data)
        ok += 1
        print(f"  restored {fn} ({len(data):,}b)", flush=True)
    print(f"restore done: {ok}/{len(manifest)} files", flush=True)


def verify(manifest: dict) -> None:
    bad = 0
    for fn, meta in sorted(manifest.items()):
        p = OUT / fn
        if not p.exists() or _sha256(p.read_bytes()) != meta["sha256"]:
            print(f"  !! local mismatch/missing: {fn}"); bad += 1
    print(f"local verify: {len(manifest) - bad}/{len(manifest)} match")
    if bad:
        raise SystemExit("verification failures")


if __name__ == "__main__":
    args = set(sys.argv[1:])
    if "--restore" in args:
        restore()
    elif "--verify" in args:
        verify(json.loads(MANIFEST.read_text()))
    else:
        m = fetch_all()
        if "--no-push" not in args:
            push_all(m)
